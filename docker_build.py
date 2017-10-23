#! /usr/bin/python

import optparse
import os
import re
import subprocess
import sys

#-----------------------------------------------------------------------

def get_current_branch():
    branch_list = os.popen("git branch", "r").readlines()
    for branch_line in branch_list:
        branch = branch_line.strip()
	if branch.startswith("* "):
	    return branch[2:]
    return "unknown branch"

#-----------------------------------------------------------------------

def get_all_branches():
    branches = [ ]
    branch_list = os.popen("git branch", "r").readlines()
    for branch_line in branch_list:
        branch = branch_line.strip()
	if branch.startswith("* "):
	    branches.append(branch[2:])
	else:
	    branches.append(branch)
    return branches

#-----------------------------------------------------------------------

def compute_tag(branch_name):
    dockerfile_contents = open("Dockerfile", "r").read()
    m = re.search("JENKINS_VERSION.*JENKINS_VERSION:-([0-9.]*)", dockerfile_contents)
    if m:
        return "markewaite/" + branch_name + ":" + m.group(1)
    return "markewaite/" + branch_name + ":latest"

#-----------------------------------------------------------------------

def build_one_image(branch_name):
    tag = compute_tag(branch_name)
    args = [ "docker",
             "build",
             "-t",
             tag,
             ".",
           ]
    print("Building " + tag)
    subprocess.check_call(args)

#-----------------------------------------------------------------------

def get_predecessor_branch(current_branch, all_branches):
    last = "upstream/" + current_branch
    if current_branch == "lts":
        last = "upstream/master"
    if current_branch == "cjt":
        last = "upstream/master"
    for branch in all_branches:
        if branch == current_branch:
	    return last
        if current_branch.startswith(branch):
	    last = branch
    return last

#-----------------------------------------------------------------------

def merge_predecessor_branch(current_branch, all_branches):
    predecessor_branch = get_predecessor_branch(current_branch, all_branches)
    args = [ "git",
             "merge",
             "--no-edit",
	     predecessor_branch
           ]
    print("Merging from " + predecessor_branch + " to " + current_branch)
    subprocess.check_call(args)

#-----------------------------------------------------------------------

def push_current_branch():
    args = [ "git", "push" ]
    print("Pushing current branch")
    subprocess.check_call(args)

#-----------------------------------------------------------------------

def checkout_branch(target_branch):
    subprocess.check_call(["git", "clean", "-xffd"])
    subprocess.check_call(["git", "reset", "--hard", "HEAD"])
    subprocess.check_call(["git", "checkout", target_branch])
    # Assumes lts-with-plugins contains all large binaries
    if target_branch == "lts-with-plugins":
        subprocess.check_call(["git", "lfs", "fetch", "public", "public/" + target_branch])
    subprocess.check_call(["git", "pull"])

#-----------------------------------------------------------------------

def docker_build(args = []):
    help_text = """%prog [options] [host(s)]
Build docker images.   Use -h for help."""
    parser = optparse.OptionParser(usage=help_text)

    # keep at optparse for 2.6. compatibility
    parser.add_option("-a", "--all", action="store_true", default=False, help="build all images")

    options, arg_hosts = parser.parse_args()

    original_branch = get_current_branch()
    all_branches = get_all_branches()

    if options.all:
        branches = all_branches
    else:
        branches = [ original_branch, ]

    for branch in branches:
        print("Building " + branch)
        checkout_branch(branch)
        merge_predecessor_branch(branch, all_branches)
        build_one_image(branch)
        push_current_branch()

    if original_branch != get_current_branch():
        checkout_branch(original_branch)

#-----------------------------------------------------------------------

if __name__ == "__main__": docker_build(sys.argv[1:])
