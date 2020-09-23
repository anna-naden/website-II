from jinja2 import Environment, FileSystemLoader

file_loader = FileSystemLoader("../templates")
env = Environment(loader=file_loader)
template = env.get_template('us-hot2-t.html')

output = template.render()
with open('../static/us-hot2.html','w') as f:
    f.write(output)

template = env.get_template('county-hot-t.html')
output = template.render()
with open('../static/county-hot.html', 'w') as f:
    f.write(output)