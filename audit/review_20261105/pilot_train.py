"""Real LoRA policy-gradient pilot, restricted one-digit arithmetic actions.

This is actual backpropagation/AdamW on a pretrained LM, not free-form RLVR.
See TRAINING_PROTOCOL.md, fixed before execution. Requires torch, transformers, peft, numpy.
"""
import argparse
import hashlib
import json
import platform
import subprocess
import time
from pathlib import Path

import numpy as np
import torch
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer


def pressure():
    level = int(subprocess.check_output(['sysctl', '-n', 'kern.memorystatus_vm_pressure_level'], text=True))
    if level == 4:
        raise RuntimeError('memory pressure 4; training stopped')
    return level


def params_hash(params):
    h = hashlib.sha256()
    for n, p in params.items():
        h.update(n.encode())
        h.update(p.detach().cpu().numpy().tobytes())
    return h.hexdigest()


def advantage(r):
    if r.numel() == 0:
        return r
    if r.numel() == 1:
        return r / (1 + 1e-6)
    return (r-r.mean()) / (r.std(correction=1) + 1e-6)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--model', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--steps', type=int, default=24)
    ap.add_argument('--seeds', nargs='+', type=int, default=[11,22,33])
    a = ap.parse_args()
    if a.out.exists():
        ap.error('choose a fresh output directory')
    a.out.mkdir(parents=True)
    pressure()
    started = time.monotonic()
    torch.set_num_threads(2)
    torch.manual_seed(20261105)
    device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
    tok = AutoTokenizer.from_pretrained(a.model, local_files_only=True)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(a.model, local_files_only=True, dtype=torch.float32)
    model = get_peft_model(model, LoraConfig(r=4,lora_alpha=8,target_modules=['q_proj','v_proj'],lora_dropout=0,
                                           bias='none',task_type='CAUSAL_LM'))
    model.to(device)
    model.eval()  # dropout off; autograd remains enabled for the trainable adapters.
    trainable = {n:p for n,p in model.named_parameters() if p.requires_grad}
    initial = {n:p.detach().clone() for n,p in trainable.items()}
    initial_hash = params_hash(trainable)
    digit_ids = [tok.encode(str(i), add_special_tokens=False) for i in range(10)]
    if not all(len(t)==1 for t in digit_ids):
        raise ValueError('all digit actions must be one token')
    digit_ids = torch.tensor([t[0] for t in digit_ids], device=device)
    pairs = np.array([(i,j) for i in range(20) for j in range(20)])
    rng = np.random.default_rng(20261105)
    rng.shuffle(pairs)
    texts = [f'Answer with only the last decimal digit of the sum. {i} + {j} =' for i,j in pairs]
    encoded = tok(texts, padding=True, return_tensors='pt')
    encoded = {k:v.to(device) for k,v in encoded.items()}
    lengths = encoded['attention_mask'].sum(-1)-1
    labels = torch.tensor(pairs.sum(-1)%10, device=device)
    base = model.get_base_model()

    def logits(indices):
        ix = torch.tensor(indices, dtype=torch.long, device=device)
        out = base.model(input_ids=encoded['input_ids'][ix], attention_mask=encoded['attention_mask'][ix],use_cache=False)
        last = out.last_hidden_state[torch.arange(len(ix), device=device),lengths[ix]]
        return torch.nn.functional.linear(last, base.get_output_embeddings().weight[digit_ids])

    with torch.no_grad():
        base_probs = torch.cat([logits(range(s,min(s+16,400))).softmax(-1).cpu() for s in range(0,400,16)])
    # Calibration never reads oracle labels from training prompts or failed training samples.
    calp = base_probs[200:300].numpy().ravel()
    caly = (np.arange(10)[None,:] == (pairs[200:300].sum(-1)%10)[:,None]).ravel().astype(float)
    bins = np.minimum((calp*10).astype(int),9)
    counts = np.bincount(bins,minlength=10)
    sums = np.bincount(bins,weights=caly,minlength=10)
    reliability = (sums+1)/(counts+2)
    q = torch.tensor(reliability[np.minimum((base_probs.numpy()*10).astype(int),9)],dtype=torch.float32,device=device)
    test_y = (np.arange(10)[None,:] == (pairs[300:].sum(-1)%10)[:,None]).astype(float)
    calibration = {'bin_counts':counts.tolist(),'bin_positive':sums.tolist(),'q':reliability.tolist(),
                   'test_brier_all_candidates':float(np.mean((q[300:].cpu().numpy()-test_y)**2)),
                   'split_sha256':hashlib.sha256(pairs.tobytes()).hexdigest()}

    def evaluate():
        with torch.no_grad():
            probs = torch.cat([logits(range(s,min(s+16,400))).softmax(-1) for s in range(300,400,16)])
            y = labels[300:]
            ref = base_probs[300:].to(device)
            return {'greedy_accuracy':float((probs.argmax(-1)==y).float().mean().cpu()),
                    'expected_oracle_reward':float(probs.gather(1,y[:,None]).mean().cpu()),
                    'kl_to_initial':float((probs*(probs.clamp_min(1e-12).log()-ref.clamp_min(1e-12).log())).sum(-1).mean().cpu())}

    result = {'protocol':'TRAINING_PROTOCOL.md','model_revision':'12fd25f77366fa6b3b4b768ec3050bf629380bac',
              'model_file_sha256':hashlib.sha256((a.model/'model.safetensors').read_bytes()).hexdigest(),
              'model_bytes':(a.model/'model.safetensors').stat().st_size,
              'environment':{'platform':platform.platform(),'python':platform.python_version(),'torch':torch.__version__,
                             'device':str(device)},'trainable_parameters':sum(p.numel() for p in trainable.values()),
              'initial_adapter_sha256':initial_hash,'calibration':calibration,'steps':a.steps,'seeds':a.seeds,'runs':[]}
    trace_path = a.out/'steps.jsonl'
    with trace_path.open('w') as trace:
        for seed in a.seeds:
            for policy in ('oracle','zero','exclude','calibrated'):
                with torch.no_grad():
                    for n,p in trainable.items():
                        p.copy_(initial[n])
                if params_hash(trainable) != initial_hash:
                    raise ValueError('adapter reset failed')
                opt = torch.optim.AdamW(trainable.values(),lr=3e-4,weight_decay=0.01)
                draws = np.random.default_rng(seed)
                metrics = [{'step':0,**evaluate()}]
                max_grad = total_failed = total_positive = 0
                arm_start = time.monotonic()
                for step in range(a.steps):
                    level = pressure()
                    ix = draws.integers(0,200,4)
                    action_u = draws.random((4,8))
                    fail_u = draws.random((4,8))
                    lp = logits(ix).log_softmax(-1)
                    p_np = lp.detach().exp().cpu().numpy()
                    # Inverse-CDF actions use the same base uniforms across treatment paths.
                    sampled = np.minimum((action_u[:,:,None] > np.cumsum(p_np,axis=1)[:,None,:]).sum(-1),9)
                    action = torch.tensor(sampled,device=device)
                    clean = (action == labels[torch.tensor(ix,device=device)][:,None]).float()
                    failed = torch.tensor(fail_u<0.25,device=device)
                    observed = clean.masked_fill(failed,0)
                    active = torch.ones_like(failed) if policy != 'exclude' else ~failed
                    used = clean if policy == 'oracle' else observed
                    if policy == 'calibrated':
                        imputed = q[torch.tensor(ix,device=device)].gather(1,action)
                        used = torch.where(failed,imputed,observed)
                    adv = torch.zeros_like(clean)
                    for j in range(4):
                        adv[j,active[j]] = advantage(used[j,active[j]])
                    chosen = lp.gather(1,action)
                    denom = active.sum().clamp_min(1)
                    pg = -(chosen*adv.detach()*active).sum()/denom
                    ref = base_probs[ix].to(device).clamp_min(1e-12)
                    kl = (lp.exp()*(lp-ref.log())).sum(-1).mean()
                    loss = pg+0.01*kl
                    opt.zero_grad(set_to_none=True)
                    loss.backward()
                    gn = float(torch.nn.utils.clip_grad_norm_(trainable.values(),1.0).detach().cpu())
                    opt.step()
                    max_grad = max(max_grad,gn)
                    total_failed += int(failed.sum().cpu())
                    total_positive += int(clean.sum().cpu())
                    entry = {'seed':seed,'policy':policy,'step':step+1,'loss':float(loss.detach().cpu()),'grad_norm':gn,
                             'injected_missing':int(failed.sum().cpu()),'true_positive_actions':int(clean.sum().cpu()),
                             'loss_rows':int(active.sum().cpu()),'pressure':level}
                    trace.write(json.dumps(entry)+'\n'); trace.flush()
                    if step+1 in (12,a.steps):
                        metrics.append({'step':step+1,**evaluate()})
                delta = sum(float(((p.detach()-initial[n])**2).sum().cpu()) for n,p in trainable.items())**0.5
                record = {'seed':seed,'policy':policy,'metrics':metrics,'max_grad_norm':max_grad,'adapter_update_l2':delta,
                          'adapter_final_sha256':params_hash(trainable),'injected_missing':total_failed,
                          'true_positive_actions':total_positive,'seconds':time.monotonic()-arm_start}
                if not (max_grad>0 and delta>0 and record['adapter_final_sha256']!=initial_hash):
                    raise ValueError('no real parameter update')
                result['runs'].append(record)
                (a.out/'results.json').write_text(json.dumps(result,indent=2)+'\n')
                print(json.dumps(record),flush=True)
    result['seconds'] = time.monotonic()-started
    (a.out/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
