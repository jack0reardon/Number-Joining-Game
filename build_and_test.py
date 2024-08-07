import re
import subprocess
import sys
from argparse import ArgumentParser
from pathlib import Path

parser = ArgumentParser(description="Run pyproject-build and pytest.")
parser.add_argument('--build', action='store_true', help='Run pyproject-build.')
parser.add_argument('--test', action='store_true', help='Run pytest.')

def run_pipreqs(directory='.', force=True):
    # Build the command list
    command = ['pipreqs', directory]
    if force:
        command.append('--force')
    
    try:
        # Run the command
        subprocess.check_call(command)
        src = Path(directory) / Path('requirements.txt')
        dest = Path('requirements.txt')
        if dest.exists():
            dest.unlink()
        src.rename(dest)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

import re
from packaging.version import parse

def retain_latest_package_versions(file_path='requirements.txt'):
    # Pattern to match package lines with versions
    package_pattern = re.compile(r'^([a-zA-Z0-9_\-]+)\s*([=><!~]*\s*\d+(\.\d+)*(\.\d+)*(?:\s*\S*)?)$', re.IGNORECASE)
    
    try:
        # Read the existing file content
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        # Dictionary to store the latest version for each package
        package_versions = {}
        for line in lines:
            match = package_pattern.match(line.strip())
            if match:
                package_name = match.group(1)
                version_spec = match.group(2).strip()
                if version_spec.startswith('=='):
                    version_spec = version_spec[2:]
                
                if package_name in package_versions:
                    current_version = package_versions[package_name]
                    if parse(version_spec.split()[0]) > parse(current_version.split()[0]):
                        package_versions[package_name] = version_spec
                else:
                    package_versions[package_name] = version_spec
        
        # Write the updated file content
        with open(file_path, 'w') as file:
            for line in lines:
                match = package_pattern.match(line.strip())
                if match:
                    package_name = match.group(1)
                    if package_name in package_versions and line.strip().startswith(package_name):
                        file.write(f"{package_name}=={package_versions[package_name]}\n")
                        del package_versions[package_name] # Remove to ensure only one entry per package
                else:
                    file.write(line)
       
        print(f"Updated '{file_path}' to retain only the latest versions for each package.")
    
    except Exception as e:
        print(f"An error occurred: {e}")

def update_install_requires(setup_cfg_path='setup.cfg', requirements_path='requirements.txt', delete_req_file=True):
    try:
        with open(requirements_path, 'r') as file:
            requirements_lines = [line.strip() for line in file if line.strip()]

        # Prepare the install_requires content
        install_requires_content = '\n'.join(f'    {line}' for line in requirements_lines)
    except Exception as e:
        print(f"An error occurred while reading '{requirements_path}': {e}")
        return
    
    try:
        # Read the current setup.cfg content
        with open(setup_cfg_path, 'r') as file:
            setup_cfg_lines = file.readlines()
        
        # Find and replace the install_requires section
        inside_install_requires = False
        new_lines = []
        for line in setup_cfg_lines:
            if re.match(r'^\[options\]', line):
                inside_install_requires = False
                new_lines.append(line)
                continue

            if inside_install_requires:
                if line.strip() == '':
                    inside_install_requires = False
                    new_lines.append(f'install_requires =\n{install_requires_content}\n\n')
                continue
            
            if re.match(r'^install_requires\s*=', line):
                inside_install_requires = True
                continue
            
            new_lines.append(line)
        
        # If the install_requires section was not found, append it
        if not any(re.match(r'^install_requires\s*=', line) for line in setup_cfg_lines):
            if not any(re.match(r'^\[options\]', line) for line in setup_cfg_lines):
                new_lines.append('\n[options]\n')
            new_lines.append(f'install_requires =\n{install_requires_content}\n')

        # Write the updated setup.cfg content
        with open(setup_cfg_path, 'w') as file:
            file.writelines(new_lines)

        if delete_req_file:
            Path(f'{requirements_path}').unlink()
        
        print(f"Updated '{setup_cfg_path}' with requirements from '{requirements_path}'.")
    
    except Exception as e:
        print(f"An error occurred while updating '{setup_cfg_path}': {e}")


def execute_command(command, cwd=None):
    try:
        print(f"Executing shell command '{command}'.")
        result = subprocess.run(
            command, shell=True, cwd=cwd, text=True, capture_output=True, check=True
        )
        print(f"Command '{command}' executed successfully.")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command '{command}':")
        print(e.stderr)
        sys.exit(e.returncode)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


def main():
    # Set up argument parsing
    parser = ArgumentParser(description="Run pyproject-build and pytest.")
    parser.add_argument('--no-update-req', action='store_true', help='Don''t update ''requirements.txt''.')
    parser.add_argument('--no-build', action='store_true', help='Don''t run ''pyproject-build''.')
    parser.add_argument('--no-install', action='store_true', help='Don''t run ''pip install -e .''.')
    parser.add_argument('--no-test', action='store_true', help='Don''t run ''pytest''.')

    # Parse command-line arguments
    args = parser.parse_args()

    if not args.no_update_req:
        run_pipreqs(directory='src')
        retain_latest_package_versions()
        update_install_requires()
    
    if not args.no_build:
        execute_command('pyproject-build')

    if not args.no_install:
        execute_command('pip install -e .')
    
    if not args.no_test:
        execute_command('pytest')

if __name__ == "__main__":
    main()
