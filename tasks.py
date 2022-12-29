#! /usr/bin/env python

####
#
# General:
#   inv [--dry] TASK [OPTIONS]
#   inv --list
#   inv --help TASK
#
# Tasks:
#   inv tags
#   inv test [--cov]
#   inv tox
#   inv bump [--kind <major|minor|patch>] [--local]
#   inv dist [--publish] [--test]
#
####

import subprocess
import sys
from invoke import task
from pathlib import Path

LIB = 'kwexception'

@task
def tags(c):
    '''
    Run mtags for the project
    '''
    c.run('mtags --recipe .kwexceptionpy --write w')
    c.run('mtags --recipe .kwexceptiontxt --write u --toc order')

@task
def test(c, func = None, cov = False, vv = False):
    '''
    Run pytest. optionally opening coverage report.
    '''
    # Set the target: the thing to be tested.
    if func is None:
        target = 'tests'
    else:
        path = path_for_test_func(func)
        target = f'{path}::{func}'
    # Build pytest command.
    cov_args = f'--cov {LIB} --cov-report html' if cov else ''
    verbosity = '-vv' if vv else '-v'
    cmd = f'pytest --color yes -s {verbosity} {cov_args} {target}'
    # Run and cover.
    c.run(cmd)
    if cov:
        c.run('open htmlcov/index.html')

def path_for_test_func(func):
    # Takes a test function name.
    # Returns the path to its test file, or exits.
    args = ('ack', '-l', f'^def {func}', 'tests')
    result = subprocess.run(args, stdout = subprocess.PIPE)
    out = result.stdout.decode('utf-8').strip()
    paths = out.split('\n') if out else []
    n = len(paths)
    if n == 1:
        return paths[0]
    elif n == 0:
        sys.exit('No matching paths.')
    else:
        txt = '\n'.join(paths)
        sys.exit(f'Too many matching paths.\n{txt}')

@task
def bump(c, kind = 'minor', edit_only = False, push = False):
    '''
    Version bump: minor|major|patch [--edit-only] [--push]
    '''
    # Validate.
    assert kind in ('major', 'minor', 'patch')

    # Get current version as a 3-element list.
    path = f'src/{LIB}/version.py'
    lines = open(path).readlines()
    version = lines[0].split("'")[1]
    major, minor, patch = [int(x) for x in version.split('.')]

    # Compute new version.
    tup = (
        (major + 1, 0, 0) if kind == 'major' else
        (major, minor + 1, 0) if kind == 'minor' else
        (major, minor, patch + 1)
    )
    version = '.'.join(str(x) for x in tup)

    # Write new version file.
    if c['run']['dry']:
        print(f'# Dry run: modify version.py: {version}')
    else:
        with open(path, 'w') as fh:
            fh.write(f"__version__ = '{version}'\n\n")
        print(f'Bumped to {version}.')

    # Commit and push.
    if not edit_only:
        c.run(f"git commit {path} -m 'Version {version}'")
        if push:
            c.run('git push origin master')

@task
def tox(c):
    '''
    Run tox for the project
    '''
    d = dict(PYENV_VERSION = '3.11.1:3.10.9:3.9.4:3.8.9:3.7.10:3.6.13:3.5.10')
    c.run('tox', env = d)

@task
def dist(c, publish = False, test = False):
    '''
    Create distribution, optionally publishing to pypi or testpypi.
    '''
    repo = 'testpypi' if test else 'pypi'
    c.run('rm -rf dist')
    c.run('python setup.py sdist bdist_wheel')
    c.run('echo')
    c.run('twine check dist/*')
    if publish:
        c.run(f'twine upload -r {repo} dist/*')

