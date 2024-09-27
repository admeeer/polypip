# polypip
A lightweight python module of command line tools to generate a requirements.txt file from your project based on python source file imports.

```
pip install polypip
```

## usage

```
usage:
    polypip [options] [<path>]

arguments:
    <path>                path to the directory or file to scan for imports

options:
    --refererence, --r <path>   path to a requirements.txt file to reference versions from
    --overwrite, --o            overwrite requirements.txt file if it already exists
    --shallow, --s              do not search for imports recursively
    --dry-run                   preview the requirements.txt that would be generated
    --quiet, --q                enable quiet mode
    --verbose, --v              enable verbose mode
```

