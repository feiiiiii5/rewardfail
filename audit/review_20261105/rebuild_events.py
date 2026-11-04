"""Rebuild retained historical events without writing to their directory.

Uses the frozen companion analyzer, not its retained rows or report labels.
Only a TemporaryDirectory receives symlinks, buckets and reconstructed rows.
Usage: python3 -I -B rebuild_events.py --companion ROOT --run RUN --out NEW.json
Optional --old-analyzer FILE rebuilds the reference with the pre-correction rule.
"""
import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def pressure():
    value = subprocess.check_output(['sysctl', '-n', 'kern.memorystatus_vm_pressure_level'], text=True).strip()
    if value == '4':
        raise RuntimeError('memory pressure 4; stopped before next analysis bucket')


def files(segment):
    paths = set()
    for pattern in ('obs-*.jsonl', 'results-*.jsonl', 'warm-*.jsonl', 'guard*.jsonl', 'interrupts.json',
                    'child_logs/child-*.jsonl'):
        paths.update(segment.glob(pattern))
    return sorted(paths)


def rebuild(analyzer, src, dst):
    dst.mkdir()
    for p in files(src):
        q = dst / p.relative_to(src)
        q.parent.mkdir(exist_ok=True)
        q.symlink_to(p.resolve())
    stats = analyzer.summarize_stream(dst, dst / 'rebuilt.jsonl', batch=1000, strict=True, tick=pressure)
    rows, warm = {}, Counter()
    for line in (dst / 'rebuilt.jsonl').read_text().splitlines():
        row = json.loads(line)
        if row.get('warm'):
            warm[row['class']] += 1
        else:
            if row['id'] in rows:
                raise ValueError('duplicate reconstructed id')
            rows[row['id']] = row
    retained = {r['id']: r for r in map(json.loads, (src / 'rows.jsonl').read_text().splitlines()) if not r.get('warm')}
    changed = [{'id': k, 'retained': retained.get(k, {}).get('class'), 'rebuilt': row['class']}
               for k, row in rows.items() if retained.get(k, {}).get('class') != row['class']]
    return rows, {'stats': stats, 'classes': dict(Counter(r['class'] for r in rows.values())),
                  'warm_classes': dict(warm), 'retained_row_class_differences': changed,
                  'rows_sha256': sha(dst / 'rebuilt.jsonl')}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--companion', type=Path, required=True)
    ap.add_argument('--run', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--formal-report', type=Path, required=True, help='corrected formal report; the retained run report may be pre-correction')
    ap.add_argument('--formal-key', choices=('main_metric','extension'), default='main_metric')
    ap.add_argument('--segments', nargs='+', default=['default','reference','limit2s','limit10s','replay1','replay2','replay3','retest'])
    ap.add_argument('--main-rebuild', type=Path, help='for complement: combine independently reconstructed main counts')
    ap.add_argument('--old-analyzer', type=Path)
    a = ap.parse_args()
    if a.out.exists():
        ap.error('output exists; choose a new output')
    source = a.companion / 'rewardfail/s2/analyze.py'
    rp = a.companion / 'rewardfail/s2/report.py'
    sys.path.insert(0, str(a.companion.resolve()))
    analyzer, report = module(source, 'rf_analyze'), module(rp, 'rf_report')
    names = tuple(a.segments)
    paths = [p for name in names for p in files(a.run / name)]
    manifest = [{'path': str(p.resolve()), 'bytes': p.stat().st_size, 'sha256': sha(p)} for p in paths]
    result = {'source_run': str(a.run.resolve()), 'analyzer_sha256': sha(source),
              'report_code_sha256': sha(rp), 'inputs': manifest, 'segments': {}}
    classes, kept = {}, {}
    with tempfile.TemporaryDirectory(prefix='rewardfail-events-') as t:
        for name in names:
            pressure()
            rows, info = rebuild(analyzer, a.run / name, Path(t) / name)
            classes[name] = {k: r['class'] for k, r in rows.items()}
            if name in ('default', 'reference'):
                kept[name] = rows
            result['segments'][name] = info
            print(name, len(rows), info['classes'], flush=True)
        ids = sorted(classes['default'])
        metric, k_ids, u_ids = report.main_metric(ids, classes['default'], classes['reference'])
        formal = json.loads(a.formal_report.read_text())
        expected = formal[a.formal_key]
        same = metric == expected if a.formal_key=='main_metric' else (
            all(metric[k]==expected[k] for k in ('n','k','u')) and
            set(k_ids)==set(expected['k_ids']) and set(u_ids)==set(expected['u_ids']))
        result.update(metric=metric, k_ids=k_ids, u_ids=u_ids,
                      formal_comparison_type='full_metric' if a.formal_key=='main_metric' else 'n_k_u_and_id_sets',
                      formal_metric_equal=same, formal_report_sha256=sha(a.formal_report),
                      formal_report_path=str(a.formal_report.resolve()), retained_run_report_sha256=sha(a.run / 'report.json'))
        errors = [k for k in ids if report.default_verdict(classes['default'][k]) == 0
                  and '出错' in classes['reference'].get(k, '')]
        result['reference_error_zero_ids'] = errors
        result['error_inclusive'] = {'u': len(set(u_ids) | set(errors)), 'upper_count': len(k_ids) + len(set(u_ids) | set(errors))}
        if 'limit2s' in classes and 'limit10s' in classes:
            result['limits'] = report.limits_table(sorted(classes['limit2s']), classes['limit2s'], classes['default'], classes['limit10s'])
        if 'retest' in classes:
            result['retest'] = report.retest(sorted(classes['retest']), classes['default'], classes['retest'])
        if a.main_rebuild:
            main_result=json.loads(a.main_rebuild.read_text())
            pooled={k:metric[k]+main_result['metric'][k] for k in ('n','k','u')}
            pooled['same_recovery_question']=set(k.split('-')[1] for k in k_ids)==set(k.split('-')[1] for k in main_result['k_ids'])
            pooled['unresolved_questions']=len(set(k.split('-')[1] for k in u_ids+main_result['u_ids']))
            pooled['formal_counts_equal']=all(pooled[k]==formal['all_answers'][k] for k in ('n','k','u'))
            result['pooled']=pooled
        if a.old_analyzer:
            old = module(a.old_analyzer, 'rf_old_analyze')
            old_rows, old_info = rebuild(old, a.run / 'reference', Path(t) / 'old_reference')
            old_metric, _, _ = report.main_metric(ids, classes['default'], {k:r['class'] for k,r in old_rows.items()})
            result['old_reference'] = {'analyzer_sha256': sha(a.old_analyzer), 'metric': old_metric, **old_info}
            result['correction_transitions'] = dict(Counter(old_rows[k]['class'] + ' -> ' + r['class']
                for k, r in kept['reference'].items() if old_rows[k]['class'] != r['class']))
        result['inputs_unchanged'] = all(p.stat().st_size == m['bytes'] and sha(p) == m['sha256']
                                         for p,m in zip(paths,manifest))
    a.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'metric': result['metric'], 'formal_metric_equal': result['formal_metric_equal'],
                      'inputs_unchanged': result['inputs_unchanged']}, ensure_ascii=False), flush=True)
    return 0 if result['formal_metric_equal'] and result['inputs_unchanged'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
