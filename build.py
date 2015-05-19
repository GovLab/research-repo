import glob
import os
import yaml
from slugify import slugify
import csv

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from jinja2 import Environment, FileSystemLoader


TEMPLATES_DIR = 'templates'

#PUBLICATIONS = yaml.load(open('data/publications.yaml'))

PUBLICATIONS = []
with open('data/publications.csv', 'rb') as csvfile:
    reader = csv.reader(csvfile)
    next(reader, None)

    for item in reader:
        # add one field called `org` before authors.
        (thumbnail, title, authors, date, url,
            innovation_tags, objective_tags, sector_tags, region_tags, methodology_tags,
            abstract) = item
        innovation  = map(lambda x: x.strip(), innovation_tags.split(','))
        objective   = map(lambda x: x.strip(), objective_tags.split(','))
        sector      = map(lambda x: x.strip(), sector_tags.split(','))
        region      = map(lambda x: x.strip(), region_tags.split(','))
        methodology = map(lambda x: x.strip(), methodology_tags.split(','))
        PUBLICATIONS.append({'title': title,
            #'org': org,
            'authors': authors,
            'date': date,
            'url': url,
            'thumbnail': thumbnail,
            'tags': {'innovation': innovation, 'objective': objective, 'sector': sector, 'region': region, 'methodology': methodology},
            'abstract': abstract})

mySlug = lambda x: slugify(x, separator='_', to_lower=True)

tagFilters = {}

for index, case in enumerate(PUBLICATIONS):
    case['cover'] = "%02d.png" % (index+1)
    case['slug'] = mySlug(case['title'])
    case['__tags__'] = []
    for dim in case['tags']:
        if dim in tagFilters:
            pass
        else:
            tagFilters[dim] = {}
        for tag in case['tags'][dim]:
            case['__tags__'].append(mySlug(tag))
            tagFilters[dim][tag] = mySlug(tag)

template_data = {
    'title': 'Research Repository',
    'PUBLICATIONS': sorted(PUBLICATIONS, key=lambda x: x['title']),
    'total_publications': len(PUBLICATIONS),
}
for k, v in tagFilters.items():
    template_data['%sFilters' % k] = v


tag_mapping = {
    'topic-behavioral-science': 'Behavioral Science and Nudges',
    'topic-citizen-engagement': 'Citizen Engagement',
    'topic-civic-technology':  'Civic Technology',
    'topic-data-analysis': 'Data Analysis',
    'topic-expert-networking': 'Expert Networking',
    'topic-labs': 'Labs and Experimentation',
    'topic-opendata': 'Open Data'
}


def filterPublications(tag):
    # We filter by tag
    print "Filtering by %s" % tag
    if tag not in tag_mapping:
        print "No filter"
        return PUBLICATIONS
    print "fitering for %s" % tag_mapping[tag]
    return [p for p in PUBLICATIONS if tag_mapping[tag] in p['tags']['innovation']]


def Main():
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR),
        extensions=['jinja2.ext.with_'])

    for p in PUBLICATIONS:
        template = env.get_template('publication_detail.html')
        html = template.render(p)
        with open('site/ajax/%s.html' % p['slug'], 'w') as f:
            f.write(html.encode('utf8'))
            f.close()

    pages = ['index', 'about', 'topic-filter-page']
    for page in pages:
        template = env.get_template('%s.html' % page)
        html = template.render(template_data)
        with open('site/%s.html' % page, 'w') as f:
            f.write(html.encode('utf8'))
            f.close()

    pages = tag_mapping.keys()
    for page in pages:
        template = env.get_template('topic-filter-page.html')
        template_data['searchTopic'] = tag_mapping[page]
        template_data['PUBLICATIONS'] = filterPublications(page)
        template_data['total_publications'] = len(template_data['PUBLICATIONS'])
        html = template.render(template_data)
        with open('site/%s.html' % page, 'w') as f:
            f.write(html.encode('utf8'))
            f.close()

if __name__ == '__main__':
  Main()