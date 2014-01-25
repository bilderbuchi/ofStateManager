#!/usr/bin/env python
import logging
import argparse
import sys
import os
import subprocess
import json
import errno
from datetime import datetime


###############################################################################
def validate_git_repo(strict=True):
    """Validate if current directory is in a git repo.

    Return 0 on success, 1 on error if not in a git repo,
    2 for warning about not being in a git repo"""

    LOGGER.debug('Checking if in a git repository?')
    # python3.3 offers subpocess.DEVNULL for output redirection
    if ((0 == subprocess.call(['git', 'rev-parse'])) and
        (1 == subprocess.call(
                'git clean -xnd `pwd` | grep "Would remove \./" > /dev/null',
                shell=True))):
    # we are in a git repository, but not in an ignored directory inside a git
    # repo (i.e. in OF/addons/someAddon)
        LOGGER.debug('Yes, this is in a git repository.')
        # check for uncommitted modifications
        # apparently --quiet is not 100% reliable. Use --exit-code instead
        if 0 != subprocess.call('git diff --exit-code HEAD > /dev/null',
                                 shell=True):
            LOGGER.error('Repository has uncommitted changes, ' +
                         'commit those before continuing!')
            return 1
        else:
            # Check for untracked files
            if not subprocess.call(
                        'git ls-files --others --exclude-standard ' +
                        '--error-unmatch . > /dev/null 2>&1',
                        shell=True):
                LOGGER.error('Repository has untracked files, ' +
                             'either commit, ignore or delete them.')
                return 1
            else:
                LOGGER.debug('Repository clean')
                return 0
    else:
        if strict is True:
            LOGGER.error('Not in a git repository: ' + os.getcwd())
            return 1
        else:
            LOGGER.warning('Not in a git repository: ' + os.getcwd())
            return 2


###############################################################################
def git_archive_repo(archivename, archivepath, repopath, repo_sha):
    """Archive a git repo snapshot in the given archive file."""

    try:
        with open(archivename, 'r') as _archivefile:
            LOGGER.info(archivename + ' already exists. Skipping ...')
    except IOError as exc:
        if exc.errno == errno.ENOENT:
            os.chdir(archivepath)
            LOGGER.info('Archiving ' + archivename)
            os.chdir(repopath)
            # git archive --format=tar.gz --output=arch.tar.gz \
            # --remote=./openFrameworks/ sha
            outpath = os.path.abspath(os.path.join(archivepath, archivename))
            prefixpath = os.path.basename(repopath) + os.sep
            subprocess.call(['git', 'archive', '--format=tar.gz',
                             '--output=' + outpath,
                             '--prefix=' + prefixpath, repo_sha])
            # This doesn't work with the remote option, since git repos don't
            # allow clients access to arbitrary sha's, only named ones.
            # Solution: go to repo directory, use -o to put resulting file into
            # right path
            # cf. http://git.661346.n2.nabble.com/Passing-
            # commit-IDs-to-git-archive-td7359753.html
            # TODO: error catching
            os.chdir(archivepath)
        else:  # pragma: no cover
            raise


###############################################################################
def check_for_snapshot_entry(name, json_object):
    """Return snapshot entry if it already exists."""
    return_entry = {}
    for entry in json_object['snapshots']:
        if entry['name'] == name:
            LOGGER.info('Selecting snapshot ' + name)
            return_entry = entry
            break
    return return_entry


###############################################################################
def record(args, filename):
    """Record a snapshot in a json file, as specified by arguments in args.

    Return 0 on success, 1 on failure."""

    LOGGER.debug('In subcommand record.')
    os.chdir(args.project)
    projectpath = os.getcwd()

    # parse addons.make into a list of addons
    addons_list = []
    try:
        with open('addons.make', 'r') as addons_make:
            for line in addons_make.readlines():
                addons_list.append(line.rstrip())
    except IOError as exc:
        if exc.errno == errno.ENOENT:
            LOGGER.debug('No addons.make file found.')
        else:  # pragma: no cover
            raise
    if len(addons_list) is 0:
        LOGGER.info('No addons found.')

    # search config.make for OF location
    with open('config.make', 'r') as config_make:
        of_path = ''
        for line in config_make.readlines():
            if 'OF_ROOT =' in line:
                of_path = line.split('=', 1)[-1].strip()
                break
        if len(of_path) == 0:
            LOGGER.error('Did not find OF location in config.make in ' +
                         os.getcwd())
            return 1

    LOGGER.info('Processing OF at ' + of_path)
    os.chdir(of_path)
    core_dict = {'path': of_path}
    if validate_git_repo() != 0:
        LOGGER.error('OF git repo could not be validated successfully.')
        return 1

    LOGGER.debug('Recording commit SHA')
    out = subprocess.check_output(['git', 'rev-parse', 'HEAD'],
                                  universal_newlines=True)
    core_dict['sha'] = out.strip()
    LOGGER.debug('OF commit SHA: ' + core_dict['sha'])

    LOGGER.info('Processing addons')
    addons_path = os.path.join(os.getcwd(), 'addons')
    os.chdir(addons_path)
    # get list of official addons
    official_addons = []
    with open('.gitignore', 'r') as gitignore_file:
        for line in gitignore_file:
            if line.startswith('!ofx'):
                official_addons.append(line[1:].strip())
    # prune official addons (which are in the OF repo already)
    # not very efficient (better with sets),
    # but irrelevant for the small lists we expect
    addons_list = [{'name': x}
                   for x
                   in addons_list
                   if x
                   not in official_addons]

    for addon in addons_list:
        LOGGER.info('Processing addon ' + addon['name'])
        try:
            os.chdir(os.path.join(addons_path, addon['name']))
        except Exception as exc:
            if exc.errno == errno.ENOENT:
                LOGGER.error(addon['name'] + ' does not exist at ' +
                             addons_path + '.')
                sys.exit('Aborting')
            else:  # pragma: no cover
                raise

        ret = validate_git_repo(strict=False)
        if ret == 0:
            out_string = subprocess.check_output(['git', 'rev-parse', 'HEAD'],
                                                 universal_newlines=True)
            addon['sha'] = out_string.strip()
        elif ret == 2:
            addon['sha'] = 'non-git'
        else:
            LOGGER.error(addon['name'] +
                         ' git repo could not be validated successfully.')
            return 1

    LOGGER.info('Storing metadata')
    os.chdir(projectpath)

    # Open/initialise metadata file
    try:
        with open(filename, 'r') as metafile:
            json_object = json.load(metafile)
            LOGGER.info('loaded data from ' + filename)
            LOGGER.debug(json_object)
    except IOError as exc:
        if exc.errno == errno.ENOENT:
            LOGGER.info(filename + ' does not exist yet. Creating..')
            open(filename, 'w').close()
            # create new skeleton json_object
            json_object = json.loads('{ "snapshots": [] }')
        else:  # pragma: no cover
            raise

    # Store/update metadata
    # check if snapshot entry already exists
    for entry in json_object['snapshots']:
        if entry['name'] == args.name:
            if (args.update is False) and (args.name is not 'latest'):
                LOGGER.error(args.name +
                             ': entry with the same name already exists. ' +
                             'Use -u option to overwrite.')
                return 1
            json_object['snapshots'].remove(entry)

    # write updated entry
    temp = {'name': args.name,
            'date': datetime.now().isoformat(),
            'description': args.description,
            'core': core_dict,
            'addons': addons_list}
    json_object['snapshots'].append(temp)

    LOGGER.info('Writing updated data to ' + filename)
    with open(filename, 'w') as metafile:
        json.dump(json_object, metafile, indent=1, sort_keys=True)

    return 0


###############################################################################
def create_entry_then_archive(args, basedir, filename):
    """run record, then archive, """
    os.chdir(basedir)
    setattr(args, 'description', '')
    # call record to create the necessary entry:
    if record(args, filename) == 0:
        os.chdir(basedir)
        return archive(args, filename)  # call archive recursively
    else:
        LOGGER.error('Creation of snapshot ' + args.name + 'failed.')
        return 1


###############################################################################
def archive(args, filename):
    """Archive a snapshot from a json file, as specified by arguments in args.

    Return 0 on success, 1 on failure."""
    LOGGER.debug('In subcommand archive.')
    basedir = os.getcwd()
    os.chdir(args.project)
    projectpath = os.getcwd()

    LOGGER.debug('Opening metadata file')
    try:
        with open(filename, 'r') as metafile:
            json_object = json.load(metafile)
            LOGGER.info('loaded data from ' + filename)
            LOGGER.debug(json_object)
            # update with data
    except IOError as exc:
        if exc.errno == errno.ENOENT:
            LOGGER.info('Metadata file ' + filename +
                        ' does not exist yet. Creating...')
            return create_entry_then_archive(args, basedir, filename)
        else:  # pragma: no cover
            raise

    # check if snapshot entry already exists, if not create it
    entry = check_for_snapshot_entry(args.name, json_object)
    if not entry:
        LOGGER.info('Entry ' + args.name + ' does not exist yet. Creating...')
        return create_entry_then_archive(args, basedir, filename)
    #--------------------------------------------------------------------------
    else:
        # entry exists, start archiving
        # create subdirectory for archive
        basename = str(os.path.basename(projectpath))
        archivedirectory = basename + '_archive'
        try:
            os.mkdir(archivedirectory)
        except OSError as exc:
            if exc.errno == errno.EEXIST:
                LOGGER.debug('Directory ' + archivedirectory +
                             ' already exists. Continuing.')
            else:  # pragma: no cover
                LOGGER.error('Could not create directory: ' +
                             archivedirectory + ': ' + str(exc))
                raise
        os.chdir(archivedirectory)

        # archive all elements
        # Description file
        if entry['description'] != '':
            LOGGER.info('Writing description file')
            with open(basename + '_' + entry['name'] +
                      '_description.txt', 'w') as descriptionfile:
                descriptionfile.write(entry['description'])

        # OF itself
        archivename = (basename + '_' + entry['name'] +
                       '_OF_' + entry['core']['sha'][0:7] + '.tar.gz')
        repopath = os.path.abspath(os.path.join(projectpath,
                                                entry['core']['path']))
        git_archive_repo(archivename, os.getcwd(),
                         repopath, entry['core']['sha'])

        # addons
        for addon in entry['addons']:
            LOGGER.info('Archiving addon ' + addon['name'])
            archivename = (basename + '_' + entry['name'] + '_' +
                           os.path.basename(addon['name']) + '_' +
                           addon['sha'][0:7] + '.tar.gz')
            repopath = os.path.abspath(os.path.join(projectpath,
                                                    entry['core']['path'],
                                                    'addons',
                                                    addon['name']))
            if addon['sha'] != 'non-git':
                git_archive_repo(archivename, os.getcwd(),
                                 repopath, addon['sha'])
            else:
                LOGGER.info(addon['name'] +
                            ' is not a git repo. Packing as tar.gz file.')
                subprocess.call(['tar', '-zcf', archivename,
                                 '--directory=' + os.path.dirname(repopath),
                                 os.path.basename(repopath)])

        return 0


###############################################################################
def get_branchname(target_sha):
    """
    Return branch name if a branch exists in cwd which points to target_sha.
    Return target_sha otherwise
    """
    # Create an eval-able dictionary containing SHAs and associated branchnames
    my_dict = (
        '{' +
        subprocess.check_output(['git',
                                 'for-each-ref',
                                 '--sort=authordate',
                                 '--python',
                                 '--format=%(objectname): %(refname:short),',
                                 'refs/heads/'], universal_newlines=True) +
        '}')

    try:
        name = eval(my_dict)[target_sha]
        LOGGER.debug('Found branch ' + name + ' pointing at ' + target_sha)
    except KeyError as _exc:
        name = target_sha
    return name


###############################################################################
def checkout(args, filename):
    """Check out snapshot from a json file, as specified by arguments in args.

    Return 0 on success, 1 on failure."""
    LOGGER.debug('In subcommand checkout.')
    os.chdir(args.project)
    projectpath = os.getcwd()
    non_git_repos = []

    # open metadata.json, abort on error
    try:
        with open(filename, 'r') as metafile:
            json_object = json.load(metafile)
            LOGGER.info('Loaded json data from ' + filename)
            LOGGER.debug(json_object)
    except IOError as exc:
            LOGGER.error('Could not open file: ' + str(exc))
            return 1

    entry = check_for_snapshot_entry(args.name, json_object)
    if not entry:
        LOGGER.error('Snapshot entry ' + args.name + ' does not exist.')
        return 1

    # make sure all components have clean repos before actual operations,
    # skip non-git
    LOGGER.info('Making sure repos are clean: OF')
    os.chdir(entry['core']['path'])
    if validate_git_repo() != 0:
        LOGGER.error('OF git repo could not be validated successfully.')
        return 1

    LOGGER.info('Making sure repos are clean: addons')
    addons_path = os.path.join(os.getcwd(), 'addons')
    os.chdir(addons_path)
    for addon in entry['addons']:
            LOGGER.info('Processing addon ' + addon['name'])
            if addon['sha'] == 'non-git':
                LOGGER.info('Skipping non-git addon ' + addon['name'])
                non_git_repos.append(addon['name'])
            else:
                os.chdir(addon['name'])
                if validate_git_repo() != 0:
                    LOGGER.error(
                        addon['name'] +
                        ' git repo could not be validated successfully.')
                    return 1
                os.chdir(addons_path)

    LOGGER.info('Checking out openFrameworks')
    LOGGER.info('Checking out ' + entry['core']['sha'] +
                ' of ' + entry['core']['path'])
    os.chdir(projectpath)
    os.chdir(entry['core']['path'])
    # check for named refs to avoid unnecessarily detached heads
    refname = get_branchname(entry['core']['sha'])
    if subprocess.call(['git', 'checkout', refname]) != 0:
        LOGGER.error('An error occured checking out ' + entry['core']['path'])
        return 1

    LOGGER.info('Checking out addons')
    os.chdir(addons_path)
    for addon in entry['addons']:
            if addon['sha'] == 'non-git':
                LOGGER.info('Skipping non-git addon ' + addon['name'])
            else:
                LOGGER.info('Checking out ' + addon['sha'] +
                            ' of ' + addon['name'])
                os.chdir(addon['name'])
                # check for named refs to avoid unnecessarily detached heads
                refname = get_branchname(addon['sha'])
                if subprocess.call(['git', 'checkout', refname]) != 0:
                    LOGGER.error('An error occured checking out '
                                 + addon['name'])
                    return 1
                os.chdir(addons_path)
    LOGGER.info('Finished checking out snapshot ' + entry['name'])
    if non_git_repos:
        LOGGER.warning('The following addons not under git control were ' +
                       'found. Correct code state cannot be guaranteed!')
        for item in non_git_repos:
            LOGGER.warning(str(item))

    return 0


###############################################################################
def list_command(args, filename):
    """List available snapshots. If a snapshot name is supplied,
    give more detailed info.

    Return 0 on success, 1 on failure."""

    LOGGER.debug('In subcommand list.')
    os.chdir(args.project)

    with open(filename, 'r') as metafile:
        json_object = json.load(metafile)
        LOGGER.info('Loaded json data from ' + filename)
        LOGGER.debug(json_object)

    if args.name_was_given:
        entry = check_for_snapshot_entry(args.name, json_object)
        if not entry:
            LOGGER.error('Snapshot entry ' + args.name + ' does not exist.')
            return 1
        else:
            LOGGER.info('Detailed info for snapshot ' + entry['name'] + ':')
            if entry['description'] != '':
                LOGGER.info('Description: ' + entry['description'])
            LOGGER.info('Date: ' + entry['date'])
            LOGGER.info('Openframeworks:')
            LOGGER.info('  path: ' + entry['core']['path'])
            LOGGER.info('  SHA: ' + entry['core']['sha'])
            LOGGER.info('Addons:')
            for addon in entry['addons']:
                LOGGER.info('  name: ' + addon['name'])
                LOGGER.info('  SHA: ' + addon['sha'])
            return 0
    else:
        LOGGER.info('Available snapshots:')
        for snapshot in json_object['snapshots']:
            temp_string = '  ' + snapshot['name']
            if snapshot['description'] != '':
                temp_string += (': ' + snapshot['description'])
            LOGGER.info(temp_string)
        LOGGER.info('Get more information by specifying desired ' +
                    'snapshot with -n <name>.')
        return 0


###############################################################################
class LessThanLevelFilter(logging.Filter):
    def __init__(self, passlevel):
        self.passlevel = passlevel

    def filter(self, some_record):
        return (some_record.levelno < self.passlevel)


###############################################################################
def main():

    # Set up logging
    my_format = "%(levelname)s\t%(message)s"
    #Warning and above goes to stderr
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(logging.Formatter(my_format))
    stderr_handler.setLevel(logging.WARNING)
    # everything from Debug to Info goes to stdout
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(logging.Formatter(my_format))
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.addFilter(LessThanLevelFilter(logging.WARNING))
    LOGGER.addHandler(stderr_handler)
    LOGGER.addHandler(stdout_handler)

    #*************************************
    # command line argument parser
    parser = argparse.ArgumentParser(
                description='Record and restore the state of your ' +
                            'openFrameworks projects and archive their files.')
    #Parent parser contains common options
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('-p',
                               '--project',
                                default=os.getcwd(),
                                help='Path to the desired project directory,' +
                                     ' defaults to the current directory if' +
                                     ' this option is not given')
    parent_parser.add_argument('-n',
                               '--name',
                               help='Name of the desired snapshot. Defaults ' +
                                    'to "latest", except when using list.')
    parent_parser.add_argument('-v',
                               '--verbose',
                               action='store_true',
                               help='Switch on debug logging.')

    subparsers = parser.add_subparsers(help='Available commands')
    record_parser = subparsers.add_parser('record',
                                          help='Record the state of all ' +
                                               'relevant components into a ' +
                                               'snapshot',
                                          parents=[parent_parser])
    record_parser.add_argument('-u',
                               '--update',
                               action='store_true',
                               help='If name already exists, ' +
                                    'overwrite existing entry')
    record_parser.add_argument('-d',
                               '--description',
                               default='',
                               help='Short message describing the snapshot ' +
                                    'in more detail than the name. Do not ' +
                                    'forget " " around DESCRIPTION if it ' +
                                    'contains whitespace.')
    record_parser.set_defaults(func=record)

    checkout_parser = subparsers.add_parser('checkout',
                                            help='Check out the complete ' +
                                                 'named or latest snapshot ' +
                                                 'of your project and OF',
                                            parents=[parent_parser])
    checkout_parser.set_defaults(func=checkout)

    archive_parser = subparsers.add_parser('archive',
                                           help='Archive all relevant ' +
                                                'components for the named or' +
                                                ' latest snapshot',
                                           parents=[parent_parser])
    archive_parser.set_defaults(func=archive)

    list_parser = subparsers.add_parser('list',
                                        help='List available snapshots. -n ' +
                                             'gives more detailed info about' +
                                             ' named snapshot',
                                        parents=[parent_parser])
    list_parser.set_defaults(func=list_command)

    args = parser.parse_args()
#    args=parser.parse_args(('archive -p tests/mockTree/mockProject1 -n ' +
#                           'somesnapshot -v').split())
#    # pass '-xyzZ'.split() for debugging

    # Manual defaults for name, to enable correct parsing in list()
    if not args.name:
        setattr(args, 'name', 'latest')
        setattr(args, 'name_was_given', False)
    else:
        setattr(args, 'name_was_given', True)

    #Verify option/argument validity
    #TODO: verification routines

    # Initialisation
    if args.verbose is True:
        LOGGER.setLevel(logging.DEBUG)
        # more detailed error messages for verbose mode
        my_format = "%(levelname)s\t%(funcName)s: %(message)s"
        stdout_handler.setFormatter(logging.Formatter(my_format))
        stderr_handler.setFormatter(logging.Formatter(my_format))
    else:
        LOGGER.setLevel(logging.INFO)  # DEBUG/INFO/WARNING/ERROR/CRITICAL

    LOGGER.debug(args)
    metadata_filename = 'metadata.json'  # file with metadata about project
    LOGGER.debug('Metadata filename: ' + metadata_filename)

    #Main function
    LOGGER.info('Start processing.')
    ret = args.func(args, metadata_filename)
    if  ret != 0:
        LOGGER.critical('An error occurred! Aborting execution.')
    else:
        LOGGER.info('Successfully finished processing!')

    #Cleanup
    logging.shutdown()
    return ret

###############################################################################
if __name__ == '__main__':  # pragma: no branch
    LOGGER = logging.getLogger('OFStateMgr')
    RET_VAL = main()
    sys.exit(RET_VAL)
