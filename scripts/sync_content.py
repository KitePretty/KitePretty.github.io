#!/usr/bin/env python3
"""Import only public copy from the local editable master; never import internal notes."""
from pathlib import Path
import json
import re
import sys

SITE = Path(__file__).resolve().parents[1]
MASTER = Path(sys.argv[1]) if len(sys.argv) > 1 else SITE.parent / 'Website_Copy_Editable.md'
text = MASTER.read_text(encoding='utf-8')
public = text[text.index('## Page 1'):text.index('## 配图与文件对应')]
public = re.sub(r'<!--.*?-->', '', public, flags=re.S)
public = re.sub(r'<a id="[^"]+"></a>', '', public)
pages = re.split(r'^## Page \d+ · [^\n]+\n', public, flags=re.M)[1:]
assert len(pages) == 7, 'Expected Home, Research, and five project pages.'

SLUGS = ['breast-health', 'eating-disorder-mutual-aid', 'rainbow-school', 'ehr-patient-portals', 'yoga']
IMAGES = ['breast-health', 'mutual-aid', 'rainbow-school', 'patient-portals', 'yoga']
ALTS = [
    'Illustration of a person looking for breast health information and peer support on a phone.',
    'Illustration of eating-disorder mutual aid through personal reflection and shared podcast conversations.',
    'Overview of Rainbow School, a virtual school with classrooms, common spaces, and resources representing an inclusive school environment.',
    'Illustration of a person viewing electronic health records on a patient portal.',
    'Illustration in muted pinks of a person viewing yoga images in a Xiaohongshu-style feed.',
]

def write_page(path, meta, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n\n' + body.strip() + '\n', encoding='utf-8')

def subsection(page, heading):
    return page.split('### ' + heading + '\n', 1)[1].split('\n### ', 1)[0].strip()

def card_info(block):
    lines=block.strip().split('\n',1)
    title=lines[0].strip()
    body=lines[1]
    summary=body.split('**My role:**',1)[0].strip()
    role=body.split('**My role:**',1)[1].split('\n',1)[0].strip()
    return title,summary,role

home=subsection(pages[0], 'About me')
home=re.sub(r'\n\[Download CV\].*', '', home).strip()
write_page(SITE/'content/_index.md', {'title':'Home','description':'Yuting Peng · Human–Computer Interaction and Social Computing · Research Assistant at UNC–Chapel Hill.'}, home)
contact=subsection(pages[0], 'Get in touch').split('\n[ytpeng@unc.edu]',1)[0].strip()
(SITE/'data/home.json').write_text(json.dumps({'contact':contact},ensure_ascii=False,indent=2)+'\n')
research=subsection(pages[1], 'Research interests')
write_page(SITE/'content/research/_index.md', {'title':'Research','description':'Research on community support, health, inclusive environments, and social media.'}, research)
list_cards=re.split(r'^#### ',subsection(pages[1], 'Projects'),flags=re.M)[1:]
home_cards=re.split(r'^#### ',subsection(pages[0], 'Selected Research'),flags=re.M)[1:]
assert len(list_cards)==5 and len(home_cards)==3
for i,(slug,img,alt,block,page) in enumerate(zip(SLUGS,IMAGES,ALTS,list_cards,pages[2:])):
    title,summary,role=card_info(block)
    body=page[page.index('#### Overview'):]
    headings=re.findall(r'^#### (.+)$',body,re.M)
    assert headings==['Overview','My role','Approach','Findings','Manuscript'], (slug,headings)
    body=re.sub(r'^#### ', '## ', body, flags=re.M)
    if slug=='eating-disorder-mutual-aid':
        body=body.replace('\n## Findings', '\n{{< organization-map >}}\n\n## Findings')
    meta={'title':title,'slug':slug,'weight':(i+1)*10,'description':summary,'summary':summary,'role':role,'image':'images/'+img+'.webp','image_alt':alt,'featured':i<3}
    if i<3: meta['home_summary']=card_info(home_cards[i])[1]
    if slug=='rainbow-school': meta['image_caption']='Rainbow School, a virtual environment built by a community team from blueprints co-designed with eight Korean queer youth.'
    if slug=='yoga': meta['editorial_note']='Role and findings can be updated when the full manuscript summary is available.'
    write_page(SITE/'content/research'/slug/'index.md',meta,body)
print('Imported seven pages and contact copy. Internal notes and local file paths are excluded.')
