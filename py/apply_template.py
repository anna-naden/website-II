from jinja2 import Environment, FileSystemLoader
from get_config import get_config

config = get_config()
file_loader = FileSystemLoader(config['DEFAULT']['templates'])
env = Environment(loader=file_loader)

files = ['index', 'us-hot2', 'state-hot', 'county-time-series2', 'us-hot2-m', 'world-m', 'world']
for file in files:
    input = file+'-t'+'.html'
    output_file = file + '.html'
    template = env.get_template(input)
    output = template.render()
    with open('/var/www/html/'+output_file,'w') as f:
        f.write(output)
    print(f'{output_file} created')
