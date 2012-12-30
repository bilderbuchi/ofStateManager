# ofStateManager

## ATTENTION!

Watch out, this is alpha-quality software!
Don't use on production systems or where losing data may be a problem.

##Description

This script helps you organize and archive your openFrameworks projects.
The subcommands `record`, `achive` and `restore` are used for these purposes in conjunction with a metadata file in your project directory.

The metadata.json file is structured so that other information (e.g. dependencies) can easily be added in the future.

### ofStateManager.py record
This command records a snapshot of the state (i.e. commit ID) of every involved component (your project, OF itself, any used non-core addons) into a metadata.json file in the project directory.

### ofStateManager.py checkout
This command restores all relevant components back to a given snapshot state.

Be aware that when checking out a specific commit (as opposed to a branch) puts your git into a "detached HEAD" state, i.e. your current HEAD will not point to a branch. This is perfectly normal. See the section on detached heads on [this page](http://git-scm.com/docs/git-checkout) for an explanation.
You can continue work on the affected repository (this is not your *project's* repository, but either OF itself or an addon) either by checking out another branch (e.g. `git checkout master`), or by starting a new branch from the checked out commit branch (i.e. `git checkout -b foo`)

### ofStateManager.py archive
This command archives/collects all relevant external components into a folder in your project.

This yields a self-contained project containing all necessary code, e.g. for backup purposes.
Components under git control are archived as a snapshot (i.e. without git repo or history).
OpenFrameworks as a compressed archive comes in at about 220MB.

Please note that the folder structure of your project in relation to OF and addons is not preserved, so when starting work from an archived snapshot, you have to unpack all components to their respective places, which can be deduced from the information in metadata.json.

##Usage

	usage: ofStateManager.py record [-h] [-p PROJECT] [-n NAME] [-v] [-u]

	optional arguments:
	  -h, --help            show this help message and exit
	  -p PROJECT, --project PROJECT
		                    Path to the desired project directory, defaults to the
		                    current directory if this option is not given
	  -n NAME, --name NAME  Name of the desired state, defaults to "latest" if
		                    this option is not given
	  -v, --verbose         Switch on debug logging.
	  -u, --update          If name already exists, overwrite existing entry

	usage: ofStateManager.py checkout [-h] [-p PROJECT] [-n NAME] [-v]

	optional arguments:
	  -h, --help            show this help message and exit
	  -p PROJECT, --project PROJECT
		                    Path to the desired project directory, defaults to the
		                    current directory if this option is not given
	  -n NAME, --name NAME  Name of the desired state, defaults to "latest" if
		                    this option is not given
	  -v, --verbose         Switch on debug logging.


	usage: ofStateManager.py archive [-h] [-p PROJECT] [-n NAME] [-v]

	optional arguments:
	  -h, --help            show this help message and exit
	  -p PROJECT, --project PROJECT
		                    Path to the desired project directory, defaults to the
		                    current directory if this option is not given
	  -n NAME, --name NAME  Name of the desired state, defaults to "latest" if
		                    this option is not given
	  -v, --verbose         Switch on debug logging.

### Examples

* `ofStatemanager.py record` in your project folder records a snapshot of the current state under the default name `latest`
* `ofStatemanager.py record --name releaseV1.1` records a snapshot of the current state under the given name
* `ofStatemanager.py record -u --name releaseV1.1` as previous, but updates snapshot if the name already exists
* `ofStatemanager.py record -v --project <project-path>` records a snapshot in the project in the given directory, additionally printing debug information
* `ofStatemanager.py archive` archives all necessary components for the project in an archive folder within. If `metadata.json` or the snapshot name don't exist, they are automatically created first.
* `ofStatemanager.py checkout --name myRelease` restores all related components to the state defined in the snapshot myRelease.

## Requirements/Dependencies

* OS: Only Linux is tested, MacOS should work, too. Full cross-platformness is intended.
* python, argparse 
* git
* basic shell - grep, |, pwd, tar
* config.make and addons.make files have to be present, they contain the necessary information
* addons should be under git control, OF must be.
* any git repos must not have uncommitted changes, otherwise recording the state becomes meaningless.

## License

The code in this repository is available under the MIT License (see license.md).

Copyright (c) 2012- Christoph Buchner
