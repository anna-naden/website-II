from jinja2 import Environment, FileSystemLoader

file_loader = FileSystemLoader("../templates")
env = Environment(loader=file_loader)
template = env.get_template('us-hot2-t.html')

try:
    with open('../templates/google-analytics.html', 'r') as f:
        ga = f.read()
    with open('../templates/logo.html', 'r') as f:
        logo = f.read()
except:
    print("error reading templates")
    exit()
output = template.render(google_analytics=ga, logo=logo)
with open('../static/us-hot2.html','w') as f:
    f.write(output)

template = env.get_template('county-hot-t.html')
output = template.render(google_analytics=ga, logo=logo)
with open('../static/county-hot.html', 'w') as f:
    f.write(output)