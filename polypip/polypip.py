import argparse
import os
import re
import ast
import logging

def get_imports_from_file(path): # parse imports from a python script file using ast
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
        logging.info(f"no imports found in file {path}")

    return all_imports

def generate_requirements_file(path, imports):
    with open(path, 'w', encoding='utf-8') as req_file:
        for package, (symbol, version) in sorted(imports.items()):
            if symbol and version:
                req_file.write(f"{package}{symbol}{version}\n")
            else:
                req_file.write(f"{package}\n")

def _get_standard_libraries():
    with open("stdlib", "r") as f:
        stdlibs = {line.strip() for line in f}
    return stdlibs

def get_external_imports(path, recursion=True):
    python_files = []
    local_modules = set()

    path_is_file = False
    if os.path.isfile(path):
        python_files.append(path)
        path_is_file = True
    
    if not path_is_file:
        if recursion:
            for root, dirs, files in os.walk(path):
                local_modules.add(os.path.basename(root))
                for filename in files:
                    if filename.endswith('.py') or filename.endswith('.pyw'):
                        python_files.append(os.path.join(root, filename))
        else:
            for filename in os.listdir(path):
                abs_path = os.path.join(path, filename)
                if os.path.isdir(abs_path):
                    local_modules.add(os.path.basename(abs_path))
                if os.path.isfile(abs_path) and (filename.endswith('.py') or filename.endswith('.pyw')):
                    python_files.append(abs_path)
    
    raw_imports = set()
    for file_path in python_files:
        file_imports = get_imports_from_file(file_path)
        local_modules.add(os.path.splitext(os.path.basename(file_path))[0])
        for imp in file_imports:
            package = imp[0] or imp[1]
            package = package.split('.')[0]
            raw_imports.add(package)
    logging.info(f"found {len(local_modules)} local modules: {local_modules}")
    logging.info(f"found {len(raw_imports)} raw imports: {raw_imports}")

    external_imports = raw_imports - local_modules  # Remove local modules
    external_imports -= _get_standard_libraries()  # Remove stdlibs
    return external_imports

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

        logging.info(f"parsed reference requirements file {path} with {len(imports)} imports, {list(imports.keys())}...")
        return imports

def driver(args):
    
    input_path = args.path

    if input_path is None:
        
        input_path = os.path.abspath(os.curdir)

    if os.path.isfile(input_path):
        
        if args.shallow:
            logging.info('specified --shallow but input is a single file, did you mean to do this? ignoring.')

        save_path = os.path.join(os.path.dirname(input_path), 'requirements.txt')

    else:

        save_path = os.path.join(input_path, 'requirements.txt')

    if not args.overwrite and os.path.exists(save_path):
        logging.error('requirements.txt already exists. Use --o or --overwrite to overwrite.')
        return        
    
    imports = get_external_imports(input_path, recursion=args.shallow)

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
        
        final_imports = {imp: (None, None) for imp in imports}

    if not args.dry_run:
        generate_requirements_file(save_path, final_imports)
    else:
        logging.info(f"dry run: requirements.txt that would be generated at {save_path}:")
        for package, (symbol, version) in sorted(final_imports.items()):
            if symbol and version:
                logging.info(f"\t{package}{symbol}{version}")
            else:
                logging.info(f"\t{package}")


def main():
    
    parser = argparse.ArgumentParser(prog='polypip')

    parser.add_argument('--path', '--p', help='path to the directory or file to scan for imports)')
    parser.add_argument('--reference', '--r', help='path to a requirements.txt file to reference versions from')
    parser.add_argument('--overwrite', '--o', action='store_true', help='overwrite requirements.txt if it already exists')
    parser.add_argument('--shallow', '--s', action='store_false', help='do not search for python files recursively')
    parser.add_argument('--dry-run', action='store_true', help='preview the requirements.txt that would be generated')

    group = parser.add_mutually_exclusive_group()

    group.add_argument('--quiet', '--q', action='store_true', help='enable quiet mode')
    group.add_argument('--verbose', '--v', action='store_true', help='enable verbose mode')

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
