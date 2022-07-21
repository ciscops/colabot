import os
from jinja2 import Template

envars = os.environ
env_dict = {}
for k,v in envars.items():
    env_dict[k] = v

with open('colabot-secrets-dev.yaml.j2', 'r', encoding="utf8") as f:
    template = Template(f.read())

with open('output-secrets-dev.yaml', 'w', encoding="utf8") as f:
    f.write(template.render(env_dict))

with open('colabot-manifest-dev.yaml.j2', 'r', encoding="utf8") as f:
    template = Template(f.read())

with open('output-manifest-dev.yaml', 'w', encoding="utf8") as f:
    f.write(template.render(env_dict))
