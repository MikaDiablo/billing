import os
import re

secrets = "https://console.cloud.google.com/security/secret-manager?referrer=search&project=opensee-ci"

def extract_file_description(script_path):
    with open(script_path, 'r') as script_file:
        lines = script_file.readlines()

    # Initialize file description as blank
    file_description = ''

    # Check the first two lines for comments
    for line in lines[:2]:
        line = line.strip()
        if line.startswith('#'):
            file_description += line.lstrip('#').strip() + '\n'
    
    return file_description

def extract_function_definitions(script_path):
    function_definitions = []
    
    with open(script_path, 'r') as script_file:
        script_contents = script_file.read()
    
    function_pattern = r"def\s+(\w+)\s*\([^)]*\):"
    matches = re.finditer(function_pattern, script_contents)
    
    for match in matches:
        function_name = match.group(1)
        function_definitions.append((function_name, match.group(0)))
    
    return function_definitions

def extract_function_description(script_path, function_name):
    with open(script_path, 'r') as script_file:
        lines = script_file.readlines()

    function_description = ''

    # Search for comments within two lines before the function definition
    for i, line in enumerate(lines):
        if function_name in line:
            for j in range(i - 1, i - 3, -1):
                if j >= 0 and lines[j].strip().startswith('#'):
                    function_description += lines[j].lstrip('#').strip() + '\n'
    
    return function_description

def generate_readme(script_path):
    function_definitions = extract_function_definitions(script_path)
    file_description = extract_file_description(script_path)
    
    if not function_definitions:
        return
    
    filename = os.path.splitext(os.path.basename(script_path))[0]
    readme_file_name = filename + ".md"
    readme_file_path = os.path.join("docs", readme_file_name)
    
    readme_content = f"# {filename}\n\n"
    
    # Description section
    readme_content += "## Description\n\n"
    readme_content += file_description + "\n\n"
    
    # Functions section
    readme_content += "## Functions\n\n"
    
    for function_name, function_definition in function_definitions:
        readme_content += f"### {function_name}\n"
        readme_content += "```python\n"
        readme_content += f'{function_definition}\n'
        readme_content += "```\n\n"
        function_description = extract_function_description(script_path, function_name)
        if function_description:
            readme_content += "#### Description: \n" 
            readme_content += f"{function_description}\n\n"
    
    with open(readme_file_path, 'w') as readme_file:
        readme_file.write(readme_content)

def create_main_readme(current_directory, py_md_index, py_file_descriptions):
    main_readme_file_path = os.path.join(current_directory, 'README.md')
    
    readme_content = f"# {os.path.basename(current_directory)}\n\n"
    
    # Description section
    readme_content += "## Description\n\n"
    for file in os.listdir(current_directory):
        if file.endswith('.py') and file not in ('install.py', 'docs.py'):
            py_file_descriptions[file] = extract_file_description(file)
            readme_content += f"{py_file_descriptions[file]}"
    
    # Usage section
    readme_content += "## Usage\n"
    readme_content += f"""
Get the secrets from the secret manager, [Google Console]({secrets}). First you will need `billing_google_application_credentials` to authenticate, you must save it to a json file.
Then you will need `billing_resoto_psk` & `billing_slack_bot_token` tokens to authenticate to resoto and slack.\n

Run 
```
SECRET_PATH=path/to/the/dowloaded/json/secret RESOTO_PSK=<Resoto-token> token SLACK_BOT_TOKEN=<Slack-token> python3 install.py
``` 
to install the binary and the python requirements.
After the installation is done you may need to ```source ~/.bashrc``` and then begin to use the binary by running ```billing --help``` to see the available commands.
"""
    
    # Index section
    readme_content += "## Index\n\n"
    
    # Create a table for indexing .py files with .md files and descriptions
    readme_content += "| Python Script | Markdown File | Description |\n"
    readme_content += "|---------------|---------------|-------------|\n"
    for py_file, md_file in py_md_index.items():
        if py_file not in ('install.py', 'docs.py'):
            description = py_file_descriptions.get(py_file, "")
            readme_content += f"| [{py_file}]({md_file}) | [{md_file}]({md_file}) | {description} |\n"
    
    # Contributing section
    readme_content += "\n## Contributing\n"
    readme_content += """
To contribute you will just need to add the command and the definitions that go with and don't forget to put a comment in the beginnig of the file if you create a new one, and a comment before each definition you will create.
After you finish your development run ```python3 docs.py``` to generate docs for the new definitions and commands you add it.
    """
    
    with open(main_readme_file_path, 'w') as readme_file:
        readme_file.write(readme_content)

if __name__ == "__main__":
    current_directory = os.getcwd()
    docs_directory = os.path.join(current_directory, "docs")
    
    # Check and delete existing .md files in the "docs" directory
    for root, _, files in os.walk(docs_directory):
        for file in files:
            if file.endswith('.md'):
                os.remove(os.path.join(root, file))
    
    # Create the "docs" directory if it doesn't exist
    os.makedirs(docs_directory, exist_ok=True)
    
    # Store the mapping of .py files to .md files
    py_md_index = {}
    
    # Store descriptions for .py files
    py_file_descriptions = {}
    
    for root, _, files in os.walk(current_directory):
        for file in files:
            if file.endswith('.py') and file not in ('install.py', 'docs.py'):
                script_path = os.path.join(root, file)
                generate_readme(script_path)
                md_file_name = os.path.splitext(file)[0] + ".md"
                py_md_index[file] = os.path.join("docs", md_file_name)
    
    # Fill descriptions for .py files in the parent directory
    for file in os.listdir(current_directory):
        if file.endswith('.py') and file not in ('install.py', 'docs.py'):
            py_file_descriptions[file] = extract_file_description(file)
    
    
    # Generate a README in the main directory with the index and descriptions
    create_main_readme(current_directory, py_md_index, py_file_descriptions)
    
    print(".md files generated and saved in the 'docs' directory successfully!")
