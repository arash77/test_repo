import re

import yaml

with open("plugins.yml", 'r') as file:
    plugins = yaml.safe_load(file)

env_var_pattern = re.compile(r"\$(\w+)")

env_vars = set()

for plugin in plugins.get('plugins', []):
    config = plugin.get('config', {})
    for key, value in config.items():
        if isinstance(value, str):
            match = env_var_pattern.search(value)
            if match:
                env_vars.add(match.group(1))

with open('$GITHUB_ENV', 'a') as env_file:
    for env_var in sorted(env_vars):
        env_file.write(f"{env_var}=${{{{ secrets.{env_var} }}}}\n")

print(f"Extracted and saved {len(env_vars)} environment variables.")
