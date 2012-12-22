# ofStateManager

## ATTENTION!

Watch out, this is alpha-quality software!
Don't use on production systems or where losing data may be a problem.

##Description

This script helps you organize and archive your openFrameworks projects.
* It can record the state (i.e. commit ID) of every involved component (your project, OF itself, any used addons) into a metadata.json file in the project directory.

* It can restore all relevant components back to the defined state. (**not yet implemented**)

* It can archive a snapshot of all relevant components to another location. (**not yet implemented**)

The metadata.json file is designed so that other information (e.g. dependencies) can easily be added in the future.

##Usage

This python script comes with help texts. 
It has 3 subcommands: `record`, `checkout`, `collect`. 
Call up their help texts by supplying the `-h` argument (e.g. `ofStateManager record -h`, just like git).

## Requirements/Dependencies

* OS: Only Linux is tested, MacOS should work, too. Full cross-platformness is intended.
* python, argparse 
* git
* basic shell - grep, |, pwd
* config.make and addons.make files have to be present, they contain the necessary information
* all relevant components should be under git control
* any git repos must not have unstaged files, otherwise recording the state becomes meaningless

## License

The code in this repository is available under the MIT License (see license.md).

Copyright (c) 2012- Christoph Buchner
