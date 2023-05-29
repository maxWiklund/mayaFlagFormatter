![Maya Flag Formatter Logo](logo.png)

## Introduction
Command line tool and api to format maya command flags.

The Maya Flag Formatter (mayaff) was created to standardise maya flag names.
When you're working in a team it's likely that some of your colleagues are not as familiar with the maya API as others.
Using long flag names can help unfamiliar developers with code review and debugging. 
The mayaff project was implemented to ease development with Maya commands (`maya.cmds`).

**Input**
```python
from maya import cmds as abc
source = "..."
abc.textureWindow(source, ra=(
    abc.about(ppc=True),
    abc.about(li=True),
))
```
**Output**
```python
from maya import cmds as abc
source = "..."
abc.textureWindow(source, removeAllImages=(
    abc.about(macOSppc=True),
    abc.about(linux=True),
))
```

Contents
* [Introduction](#introduction)
* [Installation](#installation)
    * [Generating new configs](#generating-new-configs)
* [Python versions](#python-versions)
* [Usage](#usage)
* [Known limitations](#known-limitations)


## Installation
To use mayaff out of the box just install it like a normal python package with a setup.py file.
To Generate custom presets got to [Generating new configs](#generating-new-configs)
```bash
git clone https://github.com/maxWiklund/mayaFlagFormatter.git
cd mayaff
python setup.py install
```

## Generating new configs
mayaff is based on config files with all maya flags.
You can find all included configs under `mayaff/maya_configs/` directory,
if you want your own maya plugins to be formatted you can generate your own config.
The config generation script can be found in the root of git repo `maya_config_generator.py`.
To use your own custom config `mayaff . --config /path/to/your/config.json`.

## Python versions
mayaff only supports python 3.7+

## Usage
Options:
```
usage: mayaff [-h] [-v] [-t {2018,2020,2022,2023} | --config CONFIG] [--check] [--diff] [--quiet] [--exclude EXCLUDE] [--exclude-files EXCLUDE_FILES [EXCLUDE_FILES ...]] [--modules MODULES]
              [--single-thread]
              source [source ...]

Command line tool to find and replace short maya flags.

positional arguments:
  source                Directory or files you want to format.

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -t {2018,2020,2022,2023}, --target-version {2018,2020,2022,2023}
                        Target Maya version to use when formatting flags.
  --config CONFIG       Custom maya config file. If you want to provide a custom config file different to the target options.
  --check               Don't write to files. Just return the return code.
  --diff                Don't write the files back, just output a diff for each file to stdout.
  --quiet, -q           Output nothing to stdout and set return value.
  --exclude EXCLUDE     A regular expression for file names to exclude.
  --exclude-files EXCLUDE_FILES [EXCLUDE_FILES ...]
                        Exclude files. Separate files with space.
  --modules MODULES     Maya modules to use for import. Examples: --modules 'maya:cmds,pymel:core'
  --single-thread       Only execute mayaff on single thread.
```

```
mayaff . --exclude-files package.py
```

Some companies have custom wrappers around `cmds`. If you want `mayaff` to find your cmds module somewhere else use `--modules`.
Example: `mayaff . --modules "maya:cmds,custom.module:cmds"`


## Known limitations

```python
from somthing import cmds

def my_function():
    from maya import cmds
    cmds.about(...)


# This will break.
cmds.lookThru(q=True)  # somthing.cmds module.

```
