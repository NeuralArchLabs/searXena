import os
import glob

EXTENSIONS = ['.py', '.sh', '.ps1', '.yml', '.yaml', '.json', '.md', '.rst', '.txt', '.txt', '.ini', '.toml', '']
# Some have no extension like 'manage', 'Makefile', 'Dockerfile'

to_check = []
for root, dirs, files in os.walk('.'):
    if '.git' in root or 'node_modules' in root or '__pycache__' in root or '.venv' in root or 'local' in root:
        continue
    for file in files:
        if file.endswith(tuple(EXTENSIONS)) or '.' not in file:
            to_check.append(os.path.join(root, file))

replacements = {
    'searxng_extra': 'searxena_extra',
    'searxng_useragent': 'searxena_useragent',
    '[pname]': '[reload,pname]'
}

for path in to_check:
    if os.path.basename(path) == 'replace_rebrands.py' or os.path.basename(path) == 'rebrand_searxena.py':
        continue
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        continue
    
    new_content = content
    for old, new in replacements.items():
        new_content = new_content.replace(old, new)
        
    if content != new_content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {path}")
