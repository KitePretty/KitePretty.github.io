#!/usr/bin/env python3
"""Import approved public copy by project anchor; exclude internal editing notes."""
from pathlib import Path
import json
import re
import sys

SITE = Path(__file__).resolve().parents[1]
MASTER = Path(sys.argv[1]) if len(sys.argv) > 1 else SITE.parent / 'Website_Copy_Editable.md'
text = MASTER.read_text(encoding='utf-8')
public = text[text.index('<a id="home">'):text.index('## 配图与文件对应')]
public = re.sub(r'<!--.*?-->', '', public, flags=re.S)
pages = dict(re.findall(r'^<a id="([^"]+)"></a>\s*\n## Page \d+ · [^\n]+\n(.*?)(?=^<a id=|\Z)', public, flags=re.M | re.S))

PROJECTS = {
    'breast-health': ('breast-health.jpg', 'A person raising one arm and touching the side of their chest.'),
    'eating-disorder-mutual-aid': ('mutual-aid.jpg', 'A plate of cake beside a note reading EAT, with a person seated in the background.'),
    'accessible-bar': ('accessible-bar.jpeg', 'The entrance of Pub HandyCup, with a yellow and white striped awning and outdoor seating.'),
    'ehr-patient-portals': ('patient-portals.jpg', 'A laptop, tablet displaying health charts, and stethoscope on a desk.'),
    'yoga': ('yoga.png', 'A six-image collage showing assisted yoga poses.'),
}
assert set(pages) == {'home', 'research', *PROJECTS}, 'Expected Home, Research, and five project anchors.'

def write_page(path, meta, body):
    assert not re.search(r'/Users/|[\u4e00-\u9fff]|My role', body), 'Unresolved editing notes in public copy.'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n\n' + body.strip() + '\n', encoding='utf-8')

def subsection(page, heading):
    return page.split('### ' + heading + '\n', 1)[1].split('\n### ', 1)[0].strip()

def cards(page, heading):
    result = {}
    for block in re.split(r'^#### ', subsection(page, heading), flags=re.M)[1:]:
        title, body = block.strip().split('\n', 1)
        summary, rest = body.split('**Method:**', 1)
        method = rest.split('\n', 1)[0].strip()
        slug = re.search(r'\[Explore the project →\]\(#([^\)]+)\)', rest).group(1)
        assert slug not in result
        result[slug] = {'title': title.strip(), 'summary': summary.strip(), 'method': method}
    return result

home = subsection(pages['home'], 'About me')
home = re.sub(r'\n\[Download CV\].*', '', home).strip()
topics = subsection(pages['home'], 'Name and affiliation').splitlines()[-1].split(' · ')
write_page(SITE / 'content/_index.md', {'title': 'Home', 'description': 'Yuting Peng · ' + ' · '.join(topics) + ' · Research Assistant at UNC–Chapel Hill.'}, home)
contact = subsection(pages['home'], 'Get in touch').split('\n[ytpeng@unc.edu]', 1)[0].strip()
(SITE / 'data/home.json').write_text(json.dumps({'contact': contact, 'topics': topics}, ensure_ascii=False, indent=2) + '\n')
research = subsection(pages['research'], 'Research interests')
write_page(SITE / 'content/research/_index.md', {'title': 'Research', 'description': 'Research on community support, health, accessibility, inclusive environments, and social media.'}, research)
list_cards = cards(pages['research'], 'Projects')
home_cards = cards(pages['home'], 'Selected Research')
assert set(list_cards) == set(PROJECTS) and len(home_cards) == 2
assert set(home_cards) <= set(list_cards)
for i, (slug, card) in enumerate(list_cards.items()):
    image, alt = PROJECTS[slug]
    assert (SITE / 'assets/images' / image).is_file(), image
    body = pages[slug][pages[slug].index('#### Overview'):]
    headings = re.findall(r'^#### (.+)$', body, re.M)
    assert headings == ['Overview', 'Approach', 'Findings', 'Manuscript'], (slug, headings)
    body = re.sub(r'^#### ', '## ', body, flags=re.M)
    if slug == 'eating-disorder-mutual-aid':
        body = body.replace('\n## Findings', '\n{{< organization-map >}}\n\n## Findings')
    meta = {**card, 'slug': slug, 'weight': (i+1)*10, 'description': card['summary'],
            'image': 'images/' + image, 'image_alt': alt, 'featured': slug in home_cards}
    if slug in home_cards:
        assert home_cards[slug]['method'] == card['method']
        meta['home_summary'] = home_cards[slug]['summary']
    write_page(SITE / 'content/research' / slug / 'index.md', meta, body)
print('Imported seven pages, five project methods, four research topics, and contact copy. Internal notes excluded.')
