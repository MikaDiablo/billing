import os
import subprocess


JSON_SECRET_PATH = os.environ['SECRET_PATH']
RESOTO_PSK = os.environ['RESOTO_PSK']
SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']

def install_requirements(requirements_file):
    """
    Install Python packages listed in a requirements.txt file.

    Args:
        requirements_file (str): The path to the requirements.txt file.

    Returns:
        bool: True if packages were successfully installed, False otherwise.
    """
    if not os.path.exists(requirements_file):
        print(f"Error: Requirements file '{requirements_file}' does not exist.")
        return False
    
    try:
        # Use subprocess to run the pip install command
        subprocess.run(["pip", "install", "-r", requirements_file], check=True)
        print("Packages from requirements.txt installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing packages from requirements.txt: {e}")
        return False

def setup_alias_for_location(alias_name, script_path):
    if not os.path.exists(script_path):
        print(f"Error: Script path '{script_path}' does not exist.")
        return False
    current_dir = os.getcwd()
    home_dir = os.path.expanduser("~")

    full_script_path = os.path.abspath(script_path)
    
    # Check if the script is located in the current directory
    if full_script_path.startswith(current_dir):
        # Create an alias using a symbolic link
        bashrc_path = os.path.join(home_dir, ".bashrc")
        command = f'python3 {full_script_path}'
        bashrc_text =f"""# billing
alias {alias_name}='{command}'
export GOOGLE_APPLICATION_CREDENTIALS={JSON_SECRET_PATH}
export RESOTO_PSK={RESOTO_PSK}
export SLACK_BOT_TOKEN={SLACK_BOT_TOKEN}
# billing 
"""
        try:
            with open(bashrc_path, "r") as bashrc_file:
                if bashrc_text in bashrc_file.read():
                    print(f"Alias '{alias_name}' already exists in ~/.bashrc.")
                    return True
    
            # Append the alias to ~/.bashrc
            with open(bashrc_path, "a") as bashrc_file:
                bashrc_file.write(bashrc_text)

            print(f"Alias '{alias_name}' and GOOGLE_APPLICATION_CREDENTIALS added to ~/.bashrc.")
            return True
        except Exception as e:
            print(f"Error adding alias to ~/.bashrc: {e}")
            return False
        
if __name__ == "__main__":
    alias_name = "billing"
    script_path = "billing.py"
    requirements_file = "requirements.txt"

    if install_requirements(requirements_file):
        if setup_alias_for_location(alias_name, script_path):
            print("Alias and environment setup completed.")
        else:
            print("Error setting up alias.")
    else:
        print("Error installing requirements.")
