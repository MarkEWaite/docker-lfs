#! /usr/bin/python3

import fnmatch
import getpass
import optparse
import os
import re
import socket
import string
import subprocess
import sys
import tempfile

import docker_build

#-----------------------------------------------------------------------

def update_plugins(args = []):
    help_text = """%prog [options] [host(s)]
Build docker images.   Use -h for help."""
    parser = optparse.OptionParser(usage=help_text)

    # keep at optparse for 2.6. compatibility
    parser.add_option("-r", "--report", action="store_true", default=False, help="Report the command to update plugins and exit without building the image")

    options, arg_hosts = parser.parse_args()

    original_branch = docker_build.get_current_branch()
    base_jenkins_version = docker_build.compute_jenkins_base_version(original_branch, True)

    if options.report:
        docker_build.report_update_plugins_commands(base_jenkins_version)
        quit()

    existing_plugins = []
    with open('plugins.txt', 'r+') as f:
        for line in f.readlines():
            existing_plugins.append(line.strip())
    existing_plugins.sort()

    get_available_updates_command = docker_build.get_available_updates_command(base_jenkins_version)
    get_available_updates_command += [ '-o', 'txt' ]
    available_updates = subprocess.check_output(get_available_updates_command).decode('utf-8').split('\n')
    available_updates.sort()
    if available_updates[0] == '':
        available_updates = available_updates[1:]

    print("existing - available")
    print(list(set(existing_plugins) - set(available_updates)))
    print("available - existing")
    print(list(set(available_updates) - set(existing_plugins)))

    get_download_updates_command = docker_build.get_download_updates_command(base_jenkins_version)
    subprocess.check_call(get_download_updates_command)

#-----------------------------------------------------------------------

if __name__ == "__main__": update_plugins(sys.argv[1:])
