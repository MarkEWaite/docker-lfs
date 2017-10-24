#! /usr/bin/python

# If the ~/.m2 directory is not owned by group 1000, the container
# assumption that it can be written won't be met.  In that case, the
# directory is not used.  That will slow the initial builds on the machine,
# because they will need to populate the .m2 cache instead of using the
# existing cache.

import optparse
import os
import re
import socket
import subprocess
import shutil
import sys

import docker_build

jenkins_home_dir = os.path.expanduser("~/docker-jenkins-home")

#-----------------------------------------------------------------------

def is_home_network():
    if "hp-ux" in sys.platform:
        return False # No HP-UX on home networks
    from socket import socket, SOCK_DGRAM, AF_INET
    s = socket(AF_INET, SOCK_DGRAM)
    s.settimeout(1.0)
    try:
        s.connect(("google.com", 0))
    except:
        return True
    return s.getsockname()[0].startswith("172")

#-----------------------------------------------------------------------

def volume_available(lhs):
    stat_info = os.stat(lhs)
    gid = stat_info.st_gid
    if gid != 1000:
        return False
    return True

#-----------------------------------------------------------------------

def get_maven_volume_map():
    lhs = os.path.expanduser("~/.m2")
    rhs = os.path.expanduser("/var/jenkins_home/.m2/")
    return lhs + ":" + rhs

#-----------------------------------------------------------------------

def get_user_content_volume_map():
    lhs = os.path.expanduser("~/public_html")
    rhs = os.path.expanduser("/var/jenkins_home/userContent/")
    return lhs + ":" + rhs

#-----------------------------------------------------------------------

def get_jenkins_home_volume_map():
    if not os.path.exists(jenkins_home_dir):
        os.mkdir(jenkins_home_dir)
    lhs = jenkins_home_dir
    if not volume_available(lhs):
        return None
    rhs = os.path.expanduser("/var/jenkins_home")
    return lhs + ":" + rhs

#-----------------------------------------------------------------------

def get_git_reference_repo_volume_map():
    lhs = os.path.expanduser("~/git/bare/")
    rhs = os.path.expanduser("/var/lib/git/mwaite")
    return lhs + ":" + rhs

#-----------------------------------------------------------------------

def get_dns_server():
    if is_home_network():
	return "172.16.16.253"
    return "8.8.8.8"

#-----------------------------------------------------------------------

def docker_execute(docker_tag, http_port=8080, jnlp_port=50000, ssh_port=18022, debug_port=None):
    dns_server = get_dns_server()
    maven_volume_map = get_maven_volume_map()
    user_content_volume_map = get_user_content_volume_map()
    git_reference_repo_volume_map = get_git_reference_repo_volume_map()
    jenkins_home_volume_map = get_jenkins_home_volume_map()
    docker_command = [
                       "docker", "run", "-i", "--rm",
                       "--dns", dns_server,
                       "--publish", str(http_port) + ":8080",
                       "--publish", str(jnlp_port) + ":50000",
                       "--publish", str(ssh_port)  + ":18022",
                     ]
    if debug_port != None:
        docker_command.extend(["--publish", str(ssh_port)  + ":5678"])
        java_debug_opts="-Xdebug -Xrunjdwp:transport=dt_socket,server=y,suspend=y,address=5678 "
    else:
        java_debug_opts=""
    if jenkins_home_volume_map != None and http_port == 8080:
        docker_command.extend(["--volume", jenkins_home_volume_map])
    if git_reference_repo_volume_map != None:
        docker_command.extend(["--volume", git_reference_repo_volume_map])
    if maven_volume_map != None:
        docker_command.extend(["--volume", maven_volume_map])
    if user_content_volume_map != None:
        docker_command.extend(["--volume", user_content_volume_map])
    docker_command.extend([
                       "--env", 'JAVA_OPTS="' + java_debug_opts + '"-Dorg.jenkinsci.plugins.gitclient.Git.timeOut=11 -Dorg.jenkinsci.plugins.gitclient.CliGitAPIImpl.useSETSID=true -Duser.timezone=America/Denver -XX:+UseConcMarkSweepGC"',
                       # "--env", 'JENKINS_OPTS=',
                       "--env", "JENKINS_HOSTNAME=" + get_fqdn(),
                       "--env", "LANG=en_US.utf8",
                       "--env", "TZ=America/Boise",
                       "--env", "DOCKER_FIX=refer-to-docker-issues-14203-for-description",
                       "-t", docker_tag,
                     ])
    print(" ".join(map(str, docker_command)))
    subprocess.check_call(docker_command)

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

def docker_run(args = []):
    help_text = """%prog [options] [host(s)]
Run a docker image.   Use -h for help."""
    parser = optparse.OptionParser(usage=help_text)

    # keep at optparse for 2.6. compatibility
    parser.add_option("-c", "--clean", action="store_true", default=False, help="clean prior file system image")
    parser.add_option("-p", "--port", action="store", dest='http_port', default=8080, type="int", help="http port")
    parser.add_option("-j", "--jnlp", action="store", dest='jnlp_port', default=50000, type="int", help="jnlp port")
    parser.add_option("-s", "--ssh",  action="store", dest='ssh_port',  default=18022,  type="int", help="ssh port")
    parser.add_option("-d", "--debug",  action="store", dest='debug_port',  default=None,  type="int", help="debug port")

    options, arg_hosts = parser.parse_args()

    if options.clean:
        shutil.rmtree(jenkins_home_dir)
        os.mkdir(jenkins_home_dir)

    current_branch = docker_build.get_current_branch()
    docker_tag = docker_build.compute_tag(current_branch)
    docker_execute(docker_tag, options.http_port, options.jnlp_port, options.ssh_port, options.debug_port)

#-----------------------------------------------------------------------

if __name__ == "__main__": docker_run(sys.argv[1:])
