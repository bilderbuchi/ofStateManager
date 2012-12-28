# ofStateManager

## ATTENTION!

Watch out, this is alpha-quality software!
Don't use on production systems or where losing data may be a problem.

##Description

This script helps you organize and archive your openFrameworks projects.
* It can record the state (i.e. commit ID) of every involved component (your project, OF itself, any used non-core addons) into a metadata.json file in the project directory.

* It can restore all relevant components back to the defined state. (**not yet implemented**)

* It can archive/collect all relevant external components into a folder in your project. 
This yields a self-contained project containing all necessary code, e.g. for backup purposes.
Components under git control are archived as a snapshot (i.e. without git repo or history).
OpenFrameworks as a compressed archive comes in at about 220MB.
Please note that the folder structure of your project in relation to OF and addons is not preserved, so when starting work from an archived snapshot, you have to unpack all components to their respective places, which can be deduced from the information in metadata.json.

The metadata.json file is designed so that other information (e.g. dependencies) can easily be added in the future.

##Usage

This python script comes with help texts. 
It has 3 subcommands: `record`, `checkout`, `archive`. 
Call up help texts by supplying the `-h` argument (e.g. `ofStateManager record -h`, just like for git).

### Examples


* `ofStatemanager record` in your project folder records a snapshot of the current state under the default name `latest`
* `ofStatemanager record --name releaseV1.1` records a snapshot of the current state under the given name
* `ofStatemanager record -u --name releaseV1.1` as previous, but updates snapshot if the name already exists

* `ofStatemanager record -v --project <project-path>` records a snapshot in the project in the given directory, additionally printing debug information
* `ofStatemanager archive` archives all necessary components for the project in an archive folder within. If `metadata.json` or the snapshot name don't exist, they are automatically created first.

## Requirements/Dependencies

* OS: Only Linux is tested, MacOS should work, too. Full cross-platformness is intended.
* python, argparse 
* git
* basic shell - grep, |, pwd, tar
* config.make and addons.make files have to be present, they contain the necessary information
* addons should be under git control, OF must be.
* any git repos must not have unstaged files, otherwise recording the state becomes meaningless

## License

The code in this repository is available under the MIT License (see license.md).

Copyright (c) 2012- Christoph Buchner
