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

def get_dockerfile(branch_name):
    if "alpine" in branch_name:
        return "Dockerfile-alpine"
    if "slim" in branch_name:
        return "Dockerfile-slim"
    if "jdk17" in branch_name:
        return "Dockerfile-jdk17"
    if "jdk11" in branch_name:
        return "Dockerfile-jdk11"
    if "jdk8" in branch_name:
        return "Dockerfile-jdk8"
    return "Dockerfile"

#-----------------------------------------------------------------------

def compute_jenkins_base_version(branch_name, numeric_only):
    dockerfile_name = get_dockerfile(branch_name)
    dockerfile_contents = open(dockerfile_name, "r").read()
    version_matcher = "([-A-Za-z0-9.]+)"
    if numeric_only:
        version_matcher = "([0-9.]+)"
    m = re.search("FROM jenkins/jenkins:" + version_matcher, dockerfile_contents)
    if m:
        return m.group(1).strip()
    m = re.search("FROM cloudbees/cloudbees-jenkins-distribution:([-A-Za-z0-9.]+)", dockerfile_contents)
    if m:
        return m.group(1).strip()
    m = re.search("JENKINS_VERSION.*JENKINS_VERSION:-([0-9.]*)", dockerfile_contents)
    if m:
        return m.group(1).strip()
    return "latest"

#-----------------------------------------------------------------------

def compute_tag(branch_name):
    jenkins_base_version = compute_jenkins_base_version(branch_name, False)
    return "markewaite/" + branch_name + ":" + jenkins_base_version

#-----------------------------------------------------------------------

def is_home_network():
    if "hp-ux" in sys.platform:
        return False # No HP-UX on my home networks
    from socket import socket, SOCK_DGRAM, AF_INET
    s = socket(AF_INET, SOCK_DGRAM)
    s.settimeout(1.0)
    try:
        s.connect(("google.com", 0))
    except:
        return True
    return s.getsockname()[0].startswith("172")

#-----------------------------------------------------------------------

def get_fqdn():
    fqdn = socket.getfqdn()
    if not "." in fqdn:
        if is_home_network():
            fqdn = fqdn + ".markwaite.net"
        else:
            fqdn = fqdn + ".example.com"
    return fqdn

#-----------------------------------------------------------------------

# Fully qualified domain name of the host running this script
fqdn = get_fqdn()

#-----------------------------------------------------------------------

def replace_text_recursively(find, replace, include_pattern):
    print(("Replacing '" + find + "' with '" + replace + "', in files matching '" + include_pattern + "'"))
    # Thanks to https://stackoverflow.com/questions/4205854/python-way-to-recursively-find-and-replace-string-in-text-files
    for path, dirs, files in os.walk(os.path.abspath("ref")):
        for filename in fnmatch.filter(files, include_pattern):
            filepath = os.path.join(path, filename)
            with open(filepath) as f:
                s = f.read()
            s = s.replace(find, replace)
            with open(filepath, "w") as f:
                f.write(s)

#-----------------------------------------------------------------------

def replace_constants_in_ref():
    if not os.path.isdir("ref"):
        return
    replacements = { "localhost" : fqdn, "JENKINS_ADVERTISED_HOSTNAME" : fqdn, "JENKINS_HOSTNAME" : fqdn, "LOGNAME" : getpass.getuser() }
    for find in replacements:
        replace_text_recursively(find, replacements[find], "*.xml")

#-----------------------------------------------------------------------

def undo_replace_constants_in_ref():
    if not os.path.isdir("ref"):
        return
    command = [ "git", "checkout", "--", "ref" ]
    subprocess.check_call(command)

#-----------------------------------------------------------------------

def get_available_updates_command(base_jenkins_version):
    available_updates_command = [ "./jenkins-plugin-cli.sh", "--jenkins-version", base_jenkins_version,
                                  "-d", "ref/plugins",
                                  "-f", "plugins.txt",
                                  "--no-download",
                                  "--available-updates",
    ]
    return available_updates_command

#-----------------------------------------------------------------------

def report_update_plugins_commands(base_jenkins_version):
    download_updates_command = [ "./jenkins-plugin-cli.sh", "--jenkins-version", base_jenkins_version,
                                 "-d", "ref/plugins",
                                 "-f", "plugins.txt",
    ]
    print("Run " + " ".join(get_available_updates_command(base_jenkins_version) + ["-o", "txt"]) + " | grep -v ' ' > x && mv x plugins.txt")
    print("and " + " ".join(download_updates_command))

#-----------------------------------------------------------------------

def update_plugins(base_jenkins_version):
    if not os.path.isdir("ref"):
        return

    update_plugins_output = subprocess.check_output(get_available_updates_command(base_jenkins_version)).strip().decode("utf-8")
    if "has an available update" in update_plugins_output:
        undo_replace_constants_in_ref()
        print("Plugin update available")
        print("Stopping because a plugin update is available: " + update_plugins_output)
        report_update_plugins_commands(base_jenkins_version)
        quit()

#-----------------------------------------------------------------------

def build_one_image(branch_name, clean):
    replace_constants_in_ref()
    if branch_name in ["lts-with-plugins", "lts-with-plugins-add-credentials-and-nodes-rc", "lts-with-plugins-add-credentials-and-nodes-weekly"]:
        base_jenkins_version = compute_jenkins_base_version(branch_name, True)
        print(("Updating plugins for " + base_jenkins_version))
        update_plugins(base_jenkins_version)
    tag = compute_tag(branch_name)
    print(("Building " + tag))
    command = [ "docker", "build",
                    "--file", get_dockerfile(tag),
                    "--tag", tag,
              ]
    if clean:
        command.extend([ "--pull", "--no-cache" ])
    command.extend([ ".", ])
    subprocess.check_call(command)
    undo_replace_constants_in_ref()

#-----------------------------------------------------------------------

def get_predecessor_branch(current_branch, all_branches):
    last = "upstream/" + current_branch
    if current_branch == "lts":
        last = "upstream/master"
    if current_branch == "cjd":
        last = "cjd"
    if current_branch == "cjt":
        last = "cjt"
    if current_branch == "cjp":
        last = "cjp"
    for branch in all_branches:
        if branch == current_branch:
            return last
        if current_branch.startswith(branch):
            last = branch
    return last

#-----------------------------------------------------------------------

def merge_predecessor_branch(current_branch, all_branches):
    predecessor_branch = get_predecessor_branch(current_branch, all_branches)
    command = [ "git", "merge", "--no-edit", predecessor_branch ]
    print(("Merging from " + predecessor_branch + " to " + current_branch))
    subprocess.check_call(command)

#-----------------------------------------------------------------------

def push_current_branch():
    status_output = subprocess.check_output([ "git", "status"]).strip().decode("utf-8")
    if "Your branch is ahead of " in status_output:
        command = [ "git", "push" ]
        print("Pushing current branch")
        subprocess.check_call(command)

#-----------------------------------------------------------------------

def checkout_branch(target_branch):
    subprocess.check_call(["git", "clean", "-xffd"])
    subprocess.check_call(["git", "reset", "--hard", "HEAD"])
    # -with-plugins branches contain large binaries
    if target_branch.endswith("-with-plugins"):
        subprocess.check_call(["git", "lfs", "fetch", "public", "public/" + target_branch])
    # cjt-with-plugins-add-credentials contains some large binaries
    if target_branch == "cjt-with-plugins-add-credentials":
        subprocess.check_call(["git", "lfs", "fetch", "private", "private/" + target_branch])
    subprocess.check_call(["git", "checkout", target_branch])
    subprocess.check_call(["git", "pull"])

#-----------------------------------------------------------------------

def docker_build(args = []):
    help_text = """%prog [options] [host(s)]
Build docker images.   Use -h for help."""
    parser = optparse.OptionParser(usage=help_text)

    # keep at optparse for 2.6. compatibility
    parser.add_option("-a", "--all", action="store_true", default=False, help="build all images")
    parser.add_option("-c", "--clean", action="store_true", default=False, help="Pull the base image even if it is already cached")
    parser.add_option("-r", "--report", action="store_true", default=False, help="Report the command to update plugins and exit without building the image")

    options, arg_hosts = parser.parse_args()

    original_branch = get_current_branch()
    all_branches = get_all_branches()

    if options.all:
        branches = all_branches
    else:
        branches = [ original_branch, ]

    if options.report:
        base_jenkins_version = compute_jenkins_base_version(original_branch, True)
        report_update_plugins_commands(base_jenkins_version)
        quit()

    for branch in branches:
        print(("Building " + branch))
        checkout_branch(branch)
        merge_predecessor_branch(branch, all_branches)
        build_one_image(branch, options.clean)
        push_current_branch()

    if original_branch != get_current_branch():
        checkout_branch(original_branch)

#-----------------------------------------------------------------------

if __name__ == "__main__": docker_build(sys.argv[1:])
