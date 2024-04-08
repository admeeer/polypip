import argparse
import os
import re
from collections import defaultdict
import ast
import logging

def find_python_files(path, recursion=True):
    if recursion:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                if filename.endswith('.py') or filename.endswith('.pyw'):
                    yield os.path.join(dirpath, filename)
    else:
        # os.listdir() returns both files and directories, hence the os.path.isfile check
        for filename in os.listdir(path):
            abs_path = os.path.join(path, filename)
            if os.path.isfile(abs_path) and (filename.endswith('.py') or filename.endswith('.pyw')):
                yield abs_path


# parse files using ast
def get_imports_from_file(path):
    with open(path, 'r', encoding='utf-8') as file:
        code = file.read()

    tree = ast.parse(code)

    all_imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            all_imports.extend([(name.name, name.asname) for name in node.names])
        elif isinstance(node, ast.ImportFrom):
            all_imports.extend([(node.module, name.asname) for name in node.names])

    if not all_imports:
        logging.warning(f"No imports found in {path}")

    return all_imports


def generate_requirements_file(path, imports):
    with open(path, 'w', encoding='utf-8') as req_file:
        for package, (symbol, version) in sorted(imports.items()):
            if symbol and version:
                req_file.write(f"{package}{symbol}{version}\n")
            else:
                req_file.write(f"{package}\n")


def get_all_imports(files):
    imports = set()
    for file_path in files:
        for imp in get_imports_from_file(file_path):
            package = imp[0] or imp[1]
            package = package.split('.')[0]
            imports.add(package)
    return imports


def parse_requirements_file(path):
    with open(path, 'r', encoding='utf-8') as requirements_file:
        
        imports = {}
        regex = re.compile(r"([^=<>~!]+)(==|>=|<=|!=|~=|>|<)?(\d+(?:\.\d+)*(?:\.\d+)?)?")

        for line in requirements_file:

            if line.strip() == "" or line.strip().startswith('#'):
                continue

            match = regex.match(line.strip())

            if match:
                name, symbol, version = match.groups()
                imports[name.strip()] = (symbol if symbol else None, version if version else None)
            
        if not imports:
            logging.warning(f"parsed reference requirements file but no imports found!")

        return imports


def driver(args):
    
    input_path = args.path

    if input_path is None:
        
        input_path = os.path.abspath(os.curdir)

    if os.path.isfile(input_path):
        
        if args.shallow:
            logging.info('used --shallow but input is a single file. ignoring.')
        
        files = [input_path]

        save_path = os.path.join(os.path.dirname(input_path), 'requirements.txt')

    else:

        files = find_python_files(path=input_path, recursion=args.shallow)

        save_path = os.path.join(input_path, 'requirements.txt')

    if not args.overwrite and os.path.exists(save_path):
        logging.error('requirements.txt already exists. Use --o or --overwrite to overwrite.')
        return        
    
    imports = get_all_imports(files)

    final_imports = {}

    if args.reference:
    
        if os.path.exists(args.reference):
            
            reference_imports = parse_requirements_file(args.reference)

            for imp in imports:
                if imp in reference_imports:
                    symbol, version = reference_imports[imp]
                else:
                    symbol, version = None, None
                
                final_imports[imp] = (symbol, version)


        else:
            logging.error(f"couldn't find file {args.reference}")
            return
    
    else:
        
        final_imports = {imp: imp for imp in imports}

    if not args.dry_run:
        generate_requirements_file(save_path, final_imports)
    else:
        for package, (symbol, version) in sorted(final_imports.items()):
            if symbol and version:
                logging.info(f"\t{package}{symbol}{version}")
            else:
                logging.info(f"\t{package}")


def main():
    
    parser = argparse.ArgumentParser(prog='polypip')

    parser.add_argument('--path', '--p', help='path to the directory or file to scan for imports')
    parser.add_argument('--reference', '--r', help='path to a requirements.txt file to reference versions from')
    parser.add_argument('--overwrite', '--o', action='store_true', help='overwrite requirements.txt if it already exists')
    parser.add_argument('--shallow', '--s', action='store_false', help='do not search recursively')
    parser.add_argument('--dry-run', action='store_true', help='preview the requirements.txt that would be generated')

    group = parser.add_mutually_exclusive_group()

    group.add_argument('--quiet', action='store_true', help='enable quiet mode')
    group.add_argument('--verbose', action='store_true', help='enable verbose mode')

    args = parser.parse_args()

    log_level = logging.INFO

    if args.quiet:
        log_level = logging.WARNING
    elif args.verbose:
        log_level = logging.DEBUG

    logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')

    driver(args)

if __name__ == "__main__":
    main()