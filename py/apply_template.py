from jinja2 import Environment, FileSystemLoader
from get_config import get_config

config = get_config()
file_loader = FileSystemLoader(config['DEFAULT']['templates'])
env = Environment(loader=file_loader)
template = env.get_template('us-hot2-t.html')

output = template.render()
with open(config['FILES']['us_hot'],'w') as f:
    f.write(output)
print('static html created')
