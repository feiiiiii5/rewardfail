"""Read-only comparison after arXiv announcement; never logs in or submits.

Usage: python3 -I -B check_arxiv_announcement.py --arxiv-id YYMM.NNNNN \
  --local-tex paper/main.tex --local-pdf paper/rewardfail-preprint-2026-11-03.pdf
Requires pdfinfo on PATH. Exit 0=all requested fields agree, 1=mismatch,
2=invalid input/local parse error, 3=not announced (404), 4=network blocked/error.
The private submit/ number is deliberately rejected. A match is not authorship
approval, peer review, or permission to change application materials.
"""
import argparse
import difflib
import hashlib
import html
import json
import re
import subprocess
import tempfile
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path


def identifier(value):
    m = re.fullmatch(r'(\d{4}\.\d{4,5})(?:v([1-9]\d*))?', value)
    if not m:
        raise ValueError('use a public arXiv identifier YYMM.NNNNN[ vN without spaces ]; submit/ numbers are not arXiv IDs')
    return m.group(1), int(m.group(2)) if m.group(2) else None


def argument(text, start):
    """Read a balanced TeX brace argument, including nested thanks/formatting."""
    if text[start] != '{':
        raise ValueError('expected TeX brace argument')
    depth = 1
    for end in range(start+1,len(text)):
        if text[end] in '{}':
            backslashes = len(text[:end])-len(text[:end].rstrip('\\'))
            if backslashes % 2:
                continue
            depth += 1 if text[end]=='{' else -1
            if depth == 0:
                return text[start+1:end], end+1
    raise ValueError('unbalanced TeX argument')


def tex_plain(value):
    value = re.sub(r'\\mv\s*\{\}', 'Math-Verify', value)
    value = value.replace('\\\\',' ').replace('~',' ').replace('\\,',' ')
    value = re.sub(r'\\([%&#_$])',r'\1',value)
    value = re.sub(r'\\(?:texttt|textbf|emph|textit|mathrm)\s*', '', value)
    value = value.replace('{','').replace('}','').replace('$','')
    if re.search(r'\\[A-Za-z]+',value):
        raise ValueError('unsupported TeX macro; inspect source rather than guessing metadata')
    return re.sub(r'\s+',' ',value).strip()


def local_metadata(tex):
    source = re.sub(r'(?m)(?<!\\)%.*$', '', tex)
    fields = {}
    for command in ('title','author'):
        m = re.search(r'\\'+command+r'\s*\{',source)
        if not m:
            raise ValueError('local TeX has no '+command)
        fields[command],_ = argument(source,m.end()-1)
    author = fields['author']
    while (m:=re.search(r'\\thanks\s*\{',author)):
        _,end=argument(author,m.end()-1)
        author=author[:m.start()]+author[end:]
    author=author.split('\\\\',1)[0]
    authors=[tex_plain(x) for x in author.split('\\and')]
    abstract=re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}',source,re.S)
    if not abstract:
        raise ValueError('local TeX has no abstract')
    return {'title':tex_plain(fields['title']),'authors':authors,'abstract':tex_plain(abstract[1])}


def normalize(value):
    value=unicodedata.normalize('NFKC',html.unescape(value))
    for dash in ('–','—','−'):
        value=value.replace(dash,'-')
    value=value.replace('``','"').replace("''",'"')
    return re.sub(r'\s+',' ',value).strip().casefold()


def author_normalize(value):
    # arXiv citation_author uses "Family, Given"; local TeX uses display order.
    if ',' in value:
        family,given=value.split(',',1)
        value=given+' '+family
    return normalize(value)


class AbsParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.meta={}; self.abstract=[]; self.in_abstract=False
    def handle_starttag(self,tag,attrs):
        attr=dict(attrs)
        if tag=='meta' and attr.get('name','').startswith('citation_'):
            self.meta.setdefault(attr['name'],[]).append(attr.get('content',''))
        if tag=='blockquote' and 'abstract' in attr.get('class','').split():
            self.in_abstract=True
    def handle_endtag(self,tag):
        if tag=='blockquote': self.in_abstract=False
    def handle_data(self,data):
        if self.in_abstract: self.abstract.append(data)


def remote_metadata(document,requested_id):
    p=AbsParser(); p.feed(document)
    get=lambda name: p.meta.get('citation_'+name,[''])[0]
    rid=get('arxiv_id')
    if not rid:
        raise ValueError('arXiv HTML missing citation_arxiv_id; no guessed identity')
    core,version=identifier(rid)
    pdf=get('pdf_url')
    if pdf:
        endpoint=urllib.parse.urlsplit(pdf)
        if endpoint.hostname not in ('arxiv.org','export.arxiv.org') or not endpoint.path.startswith('/pdf/'):
            raise ValueError('unexpected arXiv PDF URL')
        pdfid,pdfv=identifier(endpoint.path.removeprefix('/pdf/').removesuffix('.pdf'))
        if pdfid!=core:
            raise ValueError('PDF URL identifier differs from metadata')
        version=pdfv or version
    if version is None:
        matches=re.findall(r'arXiv:\s*'+re.escape(core)+r'v(\d+)',html.unescape(document))
        history=re.findall(r'\[v(\d+)\]',document)
        version=int(matches[-1]) if matches else max(map(int,history),default=None)
    abstract=get('abstract') or ''.join(p.abstract)
    abstract=re.sub(r'^\s*Abstract:\s*','',abstract)
    if not get('title') or not p.meta.get('citation_author') or not abstract or version is None or not pdf:
        raise ValueError('missing title/authors/abstract/version/PDF URL; inspect announced page')
    return {'arxiv_id':core,'version':version,'title':get('title'),
            'authors':p.meta['citation_author'],'abstract':abstract.strip(),
            'reported_pdf_url':pdf,'pdf_url':f'https://arxiv.org/pdf/{core}v{version}'}


def page_count(path):
    proc=subprocess.run(['pdfinfo',str(path)],capture_output=True,text=True,check=True)
    match=re.search(r'^Pages:\s+(\d+)\s*$',proc.stdout,re.M)
    if not match: raise ValueError('pdfinfo returned no page count')
    return int(match[1])


def fetch(url,max_bytes):
    parsed=urllib.parse.urlsplit(url)
    if parsed.scheme!='https' or parsed.hostname not in ('arxiv.org','export.arxiv.org'):
        raise ValueError('only public arXiv HTTPS URLs are allowed')
    req=urllib.request.Request(url,headers={'User-Agent':'rewardfail-announcement-check/1.0 (read-only)'})
    with urllib.request.urlopen(req,timeout=30) as response:
        final=urllib.parse.urlsplit(response.geturl())
        if final.hostname not in ('arxiv.org','export.arxiv.org'):
            raise ValueError('unexpected redirect host')
        data=response.read(max_bytes+1)
        if len(data)>max_bytes: raise ValueError('remote file exceeds byte limit')
        return data


def compare(local,remote,rid,expected_version,local_pages,remote_pages,expected_abstract=None):
    abstract_reference = local['abstract'] if expected_abstract is None else expected_abstract
    checks={'identifier':remote['arxiv_id']==rid,'version':remote['version']==expected_version,
            'title':normalize(local['title'])==normalize(remote['title']),
            'authors':[author_normalize(x) for x in local['authors']]==[author_normalize(x) for x in remote['authors']],
            'abstract':normalize(abstract_reference)==normalize(remote['abstract']),
            'pdf_pages':local_pages==remote_pages}
    out={'status':'match' if all(checks.values()) else 'mismatch','checks':checks,'local':local,
         'public':remote,'local_pdf_pages':local_pages,'public_pdf_pages':remote_pages,
         'abstract_reference':'paper' if expected_abstract is None else 'explicit_submission_abstract',
         'paper_abstract_matches_public':normalize(local['abstract'])==normalize(remote['abstract'])}
    if expected_abstract is not None:
        out['expected_submission_abstract']=expected_abstract
        if not out['paper_abstract_matches_public']:
            out['paper_abstract_diff']=list(difflib.unified_diff(normalize(local['abstract']).split(),
                                                               normalize(remote['abstract']).split(),lineterm=''))
    if not checks['abstract']:
        out['abstract_diff']=list(difflib.unified_diff(normalize(abstract_reference).split(),
                                                     normalize(remote['abstract']).split(),lineterm=''))
    return out


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--arxiv-id',required=True)
    ap.add_argument('--expected-version',type=int,default=1)
    ap.add_argument('--local-tex',type=Path,required=True)
    ap.add_argument('--local-pdf',type=Path,required=True)
    ap.add_argument('--expected-abstract-file',type=Path,help='Explicitly compare the public abstract to this prepared submission text; still report differences from the paper abstract.')
    a=ap.parse_args()
    try:
        rid,requested_version=identifier(a.arxiv_id)
        expected=requested_version or a.expected_version
        if expected<1: raise ValueError('expected-version must be positive')
        local=local_metadata(a.local_tex.read_text())
        expected_abstract=a.expected_abstract_file.read_text().strip() if a.expected_abstract_file else None
        if expected_abstract is not None and not expected_abstract:
            raise ValueError('expected abstract file is empty')
        local_paths=[a.local_tex,a.local_pdf]+([a.expected_abstract_file] if a.expected_abstract_file else [])
        before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in local_paths}
        remote=remote_metadata(fetch('https://arxiv.org/abs/'+a.arxiv_id,4*1024*1024).decode('utf-8'),rid)
        pdf=fetch(remote['pdf_url'],50*1024*1024)
        if not pdf.startswith(b'%PDF-'): raise ValueError('public PDF URL did not return a PDF')
        with tempfile.TemporaryDirectory(prefix='rewardfail-arxiv-') as t:
            p=Path(t)/'public.pdf';p.write_bytes(pdf)
            out=compare(local,remote,rid,expected,page_count(a.local_pdf),page_count(p),expected_abstract)
        out['local_sha256']=before;out['public_pdf_sha256']=hashlib.sha256(pdf).hexdigest()
        out['local_files_unchanged']=all(hashlib.sha256(p.read_bytes()).hexdigest()==before[str(p)] for p in local_paths)
        print(json.dumps(out,ensure_ascii=False,indent=2))
        return 0 if out['status']=='match' and out['local_files_unchanged'] else 1
    except urllib.error.HTTPError as e:
        print(json.dumps({'status':'not_announced' if e.code==404 else 'network_blocked','http_status':e.code}))
        return 3 if e.code==404 else 4
    except (urllib.error.URLError,TimeoutError) as e:
        print(json.dumps({'status':'network_error','error':str(e)}));return 4
    except (ValueError,OSError,subprocess.CalledProcessError) as e:
        print(json.dumps({'status':'invalid_input_or_parse_error','error':str(e)}));return 2


if __name__=='__main__':
    raise SystemExit(main())
