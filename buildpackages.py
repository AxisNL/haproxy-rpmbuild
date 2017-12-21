#!/bin/env python
import os
import platform
import subprocess
import sys

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


dist = platform.linux_distribution()
linux = dist[0]
osmajorver = dist[1]

currentpath = os.path.dirname(os.path.realpath(sys.argv[0]))
list_of_spec_files = os.listdir(os.path.join(currentpath, 'SPECS'))

if not linux.upper().startswith('CENTOS'):
    print_err("Error, not a centos machine..")
    exit(1)

if osmajorver.startswith('7'):

    for specfile in list_of_spec_files:
        if '.el7.' in specfile:
            specfile_fullpath = os.path.join(currentpath, 'SPECS', specfile)
            print_ok('Starting with specfile {}'.format(specfile))
            print_ok('-------------------')
            # download all requirements for spec file
            command_line = "/usr/bin/spectool -R -g {}".format(specfile_fullpath)
            print_ok('Running command \'{}\''.format(command_line))
            command_result = subprocess.Popen(command_line, stdout=subprocess.PIPE, shell=True)
            command_output = command_result.communicate()[0]
            if not command_result.returncode == 0:
                print_warn(command_output)
            else:
                print_diff(command_output)

            # download all requirements for spec file
            command_line = "/usr/bin/rpmbuild -bb {}".format(specfile_fullpath)
            print_ok('Running command \'{}\''.format(command_line))
            command_result = subprocess.Popen(command_line, stdout=subprocess.PIPE, shell=True)
            command_output = command_result.communicate()[0]
            if not command_result.returncode == 0:
                print_warn(command_output)
            else:
                print_diff(command_output)

            print_ok(' ')

elif osmajorver.startswith('6'):
    for specfile in list_of_spec_files:
        if '.el6.' in specfile:
            print(specfile)

else:
    print_err("Error, version {} not supported..".format(osmajorver))
    exit(1)
