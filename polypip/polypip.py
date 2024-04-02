import argparse
import os
import re
from collections import defaultdict

def find_python_files(path):
    """Recursively find all Python script files in path."""
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if filename.endswith('.py'):
                yield os.path.join(dirpath, filename)

def extract_imports(path):
    """Extract import statements from a Python script file."""
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
    return re.findall(r'^import (\S+)|^from (\S+) import', content, re.MULTILINE)

def normalize_package_name(package):
    """Simplistic normalization of package names."""
    # This can be replaced with a more sophisticated normalization or resolution process.
    return package.split('.')[0]

def generate_requirements(directory):
    """Generate a requirements.txt file from Python files in the given directory."""
    imports = defaultdict(int)
    for file_path in find_python_files(directory):
        for imp in extract_imports(file_path):
            package = imp[0] or imp[1]
            normalized_package = normalize_package_name(package)
            imports[normalized_package] += 1

    with open('requirements.txt', 'w', encoding='utf-8') as req_file:
        for package in sorted(imports.keys()):
            req_file.write(f"{package}\n")

def main():
    
    parser = argparse.ArgumentParser(prog='polypip')
    parser.add_argument('path')
    
    args = parser.parse_args()

    if os.path.isdir(args.path):
        generate_requirements(args.path)
        print("requirements.txt has been generated.")
    elif os.path.isfile(args.path) and args.path.endswith('.py'):
        generate_requirements(os.path.dirname(args.path))
        print("requirements.txt has been generated for the single Python file.")
    else:
        print("Please provide a valid Python file or directory.")

if __name__ == "__main__":
    main()
