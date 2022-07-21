import os
from jinja2 import Template

envars = os.environ
env_dict = dict()
for k,v in envars.items():
    env_dict[k] = v
print(os.getcwd())


with open('colabot-secrets-dev.yaml.j2', 'r') as f:
    template = Template(f.read())

with open('output-secrets-dev.yaml', 'w') as f:
    f.write(template.render(env_dict))

with open('colabot-manifest-dev.yaml.j2', 'r') as f:
    template = Template(f.read())

with open('output-manifest-dev.yaml', 'w') as f:
    f.write(template.render(env_dict))

print(os.listdir())
print(env_dict['BOT_NAME_DEV'])
