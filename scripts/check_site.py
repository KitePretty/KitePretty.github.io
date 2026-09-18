#!/usr/bin/env python3
"""Check the generated public artifact before a deployment."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote
import re

ROOT=Path(__file__).resolve().parents[1]/'public'
EXPECTED=['index.html','research/index.html','research/breast-health/index.html','research/eating-disorder-mutual-aid/index.html','research/accessible-bar/index.html','research/ehr-patient-portals/index.html','research/yoga/index.html','404.html']
class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.urls=[]; self.ids=set(); self.h1=0; self.canonical=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='link' and a.get('rel')=='canonical': self.canonical=a.get('href')
        if tag=='h1': self.h1+=1
        if 'id' in a: self.ids.add(a['id'])
        for key in ('href','src'):
            if a.get(key): self.urls.append(a[key])
        if tag=='img':
            assert 'alt' in a, 'Image missing alt attribute'
            assert 'width' in a and 'height' in a, 'Image missing dimensions'

parsed={}
for filename in EXPECTED:
    path=ROOT/filename
    assert path.is_file(),f'Missing {filename}'
    content=path.read_text()
    assert not re.search(r'/Users/|localhost:|127\.0\.0\.1|[\u4e00-\u9fff]|My role|my-role',content),f'Internal content or removed role in {filename}'
    p=Page();p.feed(content);parsed[filename]=p
    assert p.h1==1,(filename,p.h1)

site_host=urlparse(parsed['index.html'].canonical or '').netloc.lower()
assert site_host, 'Homepage must declare its canonical URL'
count=0
for filename,page in parsed.items():
    for url in page.urls:
        u=urlparse(url)
        if u.scheme in ('mailto','tel','data'):continue
        if u.netloc and u.netloc.lower()!=site_host:continue
        if u.path:
            p=ROOT/unquote(u.path.lstrip('/')) if u.path.startswith('/') else (ROOT/filename).parent/unquote(u.path)
            if p.is_dir():p=p/'index.html'
        else:p=ROOT/filename
        assert p.is_file(),f'Broken link {filename} → {url}'
        if u.fragment and p.suffix=='.html':
            dest=Page();dest.feed(p.read_text());assert unquote(u.fragment) in dest.ids,f'Broken anchor {url}'
        count+=1
for filename in EXPECTED[2:-1]:
    text=(ROOT/filename).read_text()
    assert all(f'id={x}' in text or f'id="{x}"' in text for x in ['overview','approach','findings','manuscript']),filename
assert (ROOT/'index.html').read_text().count('<strong>Method:</strong>') == 2
assert (ROOT/'research/index.html').read_text().count('<strong>Method:</strong>') == 5
assert 'AI for Health' in (ROOT/'index.html').read_text()
assert 'marginalized and vulnerable populations' in (ROOT/'index.html').read_text()
assert b'%PDF-'==(ROOT/'files/yuting-peng-cv.pdf').read_bytes()[:5]
assert not any(p.suffix in ('.docx','.tex') for p in ROOT.rglob('*'))
PUBLIC_PDFS={'files/yuting-peng-cv.pdf','files/peng-cscw26-womens-health-workshop.pdf'}
assert {str(p.relative_to(ROOT)) for p in ROOT.rglob('*.pdf')} == PUBLIC_PDFS, 'Only explicitly approved PDFs should be published.'
assert all((ROOT/p).read_bytes().startswith(b'%PDF-') for p in PUBLIC_PDFS), 'Invalid public PDF.'
print(f'Passed: {len(EXPECTED)} pages, {count} local links, CV, image attributes, heading structure, and public-content checks.')
