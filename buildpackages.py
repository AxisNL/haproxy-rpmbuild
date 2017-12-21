#!/bin/env python
import json
import os
import platform
import subprocess
import sys

# Global
dist = platform.linux_distribution()
linux = dist[0]
osmajorver = dist[1]

currentpath = os.path.dirname(os.path.realpath(sys.argv[0]))
list_of_spec_files = os.listdir(os.path.join(currentpath, 'SPECS'))


# Functions
class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


def print_ok(string):
    print(colors.OKGREEN + string + colors.ENDC)


def print_warn(string):
    print(colors.WARNING + string + colors.ENDC)


def print_err(string):
    print(colors.FAIL + string + colors.ENDC)


def print_diff(string):
    print(colors.ENDC + string + colors.ENDC)


def check_for_gpgkey():
    config = json.load(open('config.json'))
    private_gpg_key_id =  config['gpg_key_id']
    if len(private_gpg_key_id) < 8:
        print_err('value gpg_key_id not found in config, or value invalid')
        exit(1)

    command_line = "/usr/bin/gpg --list-secret-keys {0}".format(private_gpg_key_id)
    command_result = subprocess.Popen(command_line, stdout=subprocess.PIPE, shell=True)
    command_output = command_result.communicate()[0]
    if not command_result.returncode == 0:
        print_err("Error finding the configured private key.")
        print_err(command_output)
        exit(1)


def check_macros():
    config = json.load(open('config.json'))
    private_gpg_key_name =  config['gpg_key_name']
    if len(private_gpg_key_name) < 1:
        print_err('value private_gpg_key_name not found in config, or value invalid')
        exit(1)

    with open(os.path.expanduser('~/.rpmmacros'), 'w') as f:
        f.write('%_signature gpg\n')
        f.write('%_gpg_path ~/.gnupg\n')
        f.write('%_gpg_name Fernando Aleman\n')
        f.write('%_gpgbin /usr/bin/gpg\n')


def process_specfile(specfile):
    global currentpath
    specfile_fullpath = os.path.join(currentpath, 'SPECS', specfile)
    print_ok('Starting with specfile {0}'.format(specfile))
    print_ok('-------------------')
    # download all requirements for spec file
    command_line = "/usr/bin/spectool -R -g {0}".format(specfile_fullpath)
    print_ok('Running command \'{0}\''.format(command_line))
    command_result = subprocess.Popen(command_line, stdout=subprocess.PIPE, shell=True)
    command_output = command_result.communicate()[0]
    if not command_result.returncode == 0:
        print_warn(command_output)
    else:
        print_diff(command_output)

    # download all requirements for spec file
    command_line = "/usr/bin/rpmbuild -bb --define \"debug_package %{{nil}}\" {0}".format(specfile_fullpath)
    print_ok('Running command \'{0}\''.format(command_line))
    command_result = subprocess.Popen(command_line, stdout=subprocess.PIPE, shell=True)
    command_output = command_result.communicate()[0]
    if not command_result.returncode == 0:
        print_warn(command_output)
    else:
        print_diff(command_output)

    print_ok(' ')


if not linux.upper().startswith('CENTOS'):
    print_err("Error, not a centos machine..")
    exit(1)

# check if we have a private key so we can sign the packages
check_for_gpgkey()

# Check rpmmacros
check_macros()

if osmajorver.startswith('7'):
    # loop through each specfile for EL7
    for specfile in list_of_spec_files:
        if '.el7.' in specfile:
            process_specfile(specfile)

elif osmajorver.startswith('6'):
    # loop through each specfile for EL6
    for specfile in list_of_spec_files:
        if '.el6.' in specfile:
            process_specfile(specfile)

else:
    print_err("Error, version {0} not supported..".format(osmajorver))
    exit(1)
