import glob
import os
import yaml
from slugify import slugify

from jinja2 import Environment, FileSystemLoader


TEMPLATES_DIR = 'templates'

PUBLICATIONS = yaml.load(open('data/publications.yaml'))

mySlug = lambda x:slugify(x, separator='_', to_lower=True)

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

print tagFilters

template_data = {
	'title': 'Research Repository',
	'PUBLICATIONS': sorted(PUBLICATIONS, key=lambda x:x['title']), 
	'total_publications': len(PUBLICATIONS),
}
for k,v in tagFilters.items():
	template_data['%sFilters' % k] = v



def Main():
	env = Environment(loader=FileSystemLoader(TEMPLATES_DIR),
		extensions=['jinja2.ext.with_'])

	for p in PUBLICATIONS:
		template = env.get_template('publication_detail.html')
		html = template.render(p)
		with open('site/ajax/%s.html' % p['slug'], 'w') as f:
			f.write(html.encode('utf8'))
			f.close()

	pages = [ 'index' ]
	for page in pages:
		template = env.get_template('%s.html' % page)
		html = template.render(template_data)
		with open('site/%s.html' % page, 'w') as f:
			f.write(html.encode('utf8'))
			f.close()

if __name__ == '__main__':
  Main()