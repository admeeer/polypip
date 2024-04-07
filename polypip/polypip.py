import argparse
import os
import re
from collections import defaultdict
import ast
import logging

def find_python_files(path):
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if filename.endswith('.py') or filename.endswith('.pyw'):
                yield os.path.join(dirpath, filename)


# Changed to incorporate AST parsing. Parsing the AST is more reliable than using regex. In addition if an import is there and not commented out, it will be picked up by the AST parser.
def get_imports_from_file(path):
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
    tree = ast.parse(content)
    imports = [(node.names[0].name,) for node in ast.walk(tree) if isinstance(node, ast.Import)]
    from_imports = [(node.module,) for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
    all_imports = imports + from_imports
    if not all_imports:
        logging.warning(f"No imports found in {path}")
    return all_imports

def generate_requirements_file(imports):
    with open('requirements.txt', 'w', encoding='utf-8') as req_file:
        for package in sorted(imports.keys()):
            req_file.write(f"{package}\n")

def gather_imports(files):
    imports = defaultdict(int)
    for file_path in files:
        for imp in get_imports_from_file(file_path):
            package = imp[0] or imp[1]
            imports[package] += 1
    return imports

def normalize_imports(imports):
    normalized_imports = defaultdict(int)
    for package, count in imports.items():
        normalized_package = package.split('.')[0]
        normalized_imports[normalized_package] += count
    return normalized_imports

def driver(args):
    path = args.path
    if path is None:
        path = os.path.abspath(os.curdir)
    files = find_python_files(path)
    imports = gather_imports(files)
    normalized_imports = normalize_imports(imports)
    generate_requirements_file(normalized_imports)


def main():
    parser = argparse.ArgumentParser(prog='polypip')
    parser.add_argument('--path')
    
    args = parser.parse_args()

    driver(args)

if __name__ == "__main__":
    main()
