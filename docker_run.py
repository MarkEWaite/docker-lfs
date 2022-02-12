#! /usr/bin/python3

# If the ~/.m2 directory is not owned current user, the container
# assumption that it can be written won't be met.  In that case, the
# directory is not used.  That will slow the initial builds on the machine,
# because they will need to populate the .m2 cache instead of using the
# existing cache.

import optparse
import os
import re
import pipes
import socket
import subprocess
import shutil
import string
import sys

import psutil # Install from pip

import docker_build

jenkins_home_dir = os.path.expanduser("~/docker-jenkins-home")

#-----------------------------------------------------------------------

def is_home_network():
    from socket import socket, SOCK_DGRAM, AF_INET
    s = socket(AF_INET, SOCK_DGRAM)
    s.settimeout(1.0)
    try:
        s.connect(("google.com", 0))
    except:
        return True
    return s.getsockname()[0].startswith("172.16.16.")

#-----------------------------------------------------------------------

def volume_available(lhs):
    stat_info = os.stat(lhs)
    gid = stat_info.st_gid
    if gid not in os.getgroups():
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
        return "172.16.16.249"
    return "8.8.8.8"

#-----------------------------------------------------------------------

def get_windows_dir():
    return string.ascii_uppercase[hash(get_fqdn()) % len(string.ascii_uppercase)] + string.ascii_uppercase[hash(get_an_ip_address()) % len(string.ascii_uppercase)]

#-----------------------------------------------------------------------

def get_jagent_java_home():
    if "jdk8" in docker_build.get_current_branch():
        return "/home/jagent/tools/jdk8u322-b06"
    if "jdk17" in docker_build.get_current_branch():
        return "/home/jagent/tools/jdk-17.0.2+8"
    return "/home/jagent/tools/jdk-11.0.14.1+1"

#-----------------------------------------------------------------------

def memory_scale(upper_bound):
    mem = psutil.virtual_memory()
    eight_GB = 8 * 1024 * 1024 * 1024
    if mem.total < eight_GB:
        return str(int(upper_bound / 2))
    return str(upper_bound)

#-----------------------------------------------------------------------

def docker_execute(docker_tag, http_port=8080, jnlp_port=50000, ssh_port=18022, debug_port=None, detach=False, quiet=False, access_mode=None):
    dns_server = get_dns_server()
    maven_volume_map = get_maven_volume_map()
    user_content_volume_map = get_user_content_volume_map()
    git_reference_repo_volume_map = get_git_reference_repo_volume_map()
    jenkins_home_volume_map = get_jenkins_home_volume_map()
    docker_command = [
                       "docker", "run", "-i",
                       "--dns", dns_server,
                       "--publish", str(http_port) + ":8080",
                       "--publish", str(ssh_port) + ":18022",
                       "--publish", str(jnlp_port) + ":50000",
                       "--restart=always",
                     ]
    if debug_port != None:
        docker_command.extend(["--publish", str(debug_port)  + ":5678"])
    if jenkins_home_volume_map != None and http_port == 8080:
        docker_command.extend(["--volume", jenkins_home_volume_map])
    if git_reference_repo_volume_map != None:
        docker_command.extend(["--volume", git_reference_repo_volume_map])
    if maven_volume_map != None:
        docker_command.extend(["--volume", maven_volume_map])
    if user_content_volume_map != None:
        docker_command.extend(["--volume", user_content_volume_map])
    if (detach):
        docker_command.extend([ "--detach" ])
    java_opts = [
                  "-XX:+AlwaysPreTouch",
                  "-XX:+HeapDumpOnOutOfMemoryError",
                  "-XX:HeapDumpPath=/var/jenkins_home/logs",
                  "-XX:+UseG1GC",
                  "-verbose:gc",
                  "-XX:+UseStringDeduplication",
                  "-XX:+ParallelRefProcEnabled",
                  "-XX:+DisableExplicitGC",
                  "-XX:+UnlockDiagnosticVMOptions",
                  "-XX:+UnlockExperimentalVMOptions",
                  "-Xms" + memory_scale(3) + "g",
                  "-Xmx" + memory_scale(7) + "g",
                  "-XshowSettings:vm"
                  # "-Dhudson.model.DownloadService.noSignatureCheck=true",
                  "-Dhudson.lifecycle=hudson.lifecycle.ExitLifecycle", # Temp until https://github.com/jenkinsci/docker/pull/1268
                  "-Dhudson.model.ParametersAction.keepUndefinedParameters=false",
                  "-Dhudson.model.ParametersAction.safeParameters=DESCRIPTION_SETTER_DESCRIPTION",
                  "-Dhudson.TcpSlaveAgentListener.hostName=" + get_base_hostname(),
                  "-Djava.awt.headless=true",
                  "-Djenkins.install.runSetupWizard=false",
                  "-Djenkins.model.Jenkins.buildsDir='/var/jenkins_home/builds/${ITEM_FULL_NAME}'",
                  "-Djenkins.model.Jenkins.workspacesDir='/var/jenkins_home/workspace/${ITEM_FULL_NAME}'",
                  "-Dorg.jenkinsci.plugins.gitclient.CliGitAPIImpl.useSETSID=true",
                  "-Dorg.jenkinsci.plugins.gitclient.GitClient.quietRemoteBranches=true",
                  "-Dorg.jenkinsci.plugins.gitclient.Git.timeOut=11",
                ]
    if jnlp_port != None:
        java_opts.append("-Dhudson.TcpSlaveAgentListener.port=" + str(jnlp_port)) # NOT THE HTTP PORT
    if debug_port != None:
        java_opts.append("-Xdebug")
        java_opts.append("-Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=5678")
    if access_mode != None:
        java_opts.append("--illegal-access=" + access_mode)
    docker_command.extend([
                       "--env", 'CASC_YAML_MAX_ALIASES=100',
                       "--env", 'JAGENT_JAVA_HOME=' + get_jagent_java_home(),
                       "--env", 'JAVA_OPTS=' + pipes.quote(" ".join(java_opts)),
                       "--env", "JENKINS_ADVERTISED_HOSTNAME=" + get_fqdn(),
                       "--env", "JENKINS_EXTERNAL_URL=" + "http://" + get_fqdn() + ":" + str(http_port) + "/",
                       "--env", "JENKINS_HOSTNAME=" + get_fqdn(),
                       "--env", "JENKINS_WINDOWS_DIR=" + get_windows_dir(),
                       "--env", "LANG=C.UTF-8",
                       "--env", "START_QUIET=" + str(quiet),
                       "--env", "TZ=America/Boise",
                       "--env", "user.timezone=America/Denver",
                       "-t", docker_tag,
                     ])
    # Using shell=True and the single string form passes quoted args correctly.
    # Since input to command is program controlled, shell=True is safe (for now)
    str_command = " ".join(map(str, docker_command))
    print(str_command)
    subprocess.check_call(str_command, shell=True)

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

def get_base_hostname():
    base_hostname = get_fqdn()
    dot = base_hostname.find('.')
    if dot > 0:
        base_hostname = base_hostname[0:dot]
    return base_hostname

#-----------------------------------------------------------------------

def get_an_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((get_dns_server(), 80))
    return s.getsockname()[0]

#-----------------------------------------------------------------------

def docker_run(args = []):
    help_text = """%prog [options] [host(s)]
Run a docker image.   Use -h for help."""
    parser = optparse.OptionParser(usage=help_text)

    # keep at optparse for 2.6. compatibility
    parser.add_option("-c", "--clean",  action="store_true", default=False, help="clean prior file system image")
    parser.add_option("-d", "--detach", action="store_true", default=False, help="detach from typical stdin and stdout")
    parser.add_option("-q", "--quiet",  action="store_true", default=False, help="start in quiet down state, process no jobs until shutdown is cancelled")

    parser.add_option("-a", "--access",action="store", dest='access_mode',default=None,  type="string", help="report illegal accesses")
    parser.add_option("-g", "--debug", action="store", dest='debug_port', default=None,  type="int",    help="debug port")
    parser.add_option("-j", "--jnlp",  action="store", dest='jnlp_port',  default=50000, type="int",    help="jnlp port")
    parser.add_option("-p", "--port",  action="store", dest='http_port',  default=8080,  type="int",    help="http port")
    parser.add_option("-s", "--ssh",   action="store", dest='ssh_port',   default=18022, type="int",    help="ssh port")
    parser.add_option("-t", "--tag",   action="store", dest='docker_tag', default=None,  type="string", help="Docker tag")

    options, arg_hosts = parser.parse_args()

    if options.clean and os.path.exists(jenkins_home_dir):
        shutil.rmtree(jenkins_home_dir)
    if options.clean and not os.path.exists(jenkins_home_dir):
        os.mkdir(jenkins_home_dir)

    # Always detach, since --restart=always prevents --rm and causes Jenkins processes to fork and exec
    options.detach = True
    if options.detach:
        print("Detaching from stdin / stdout")

    if options.quiet:
        print("Job processing disabled")

    if options.docker_tag == None:
        current_branch = docker_build.get_current_branch()
        options.docker_tag = docker_build.compute_tag(current_branch)
    docker_execute(options.docker_tag, options.http_port, options.jnlp_port, options.ssh_port, options.debug_port, options.detach, options.quiet, options.access_mode)

#-----------------------------------------------------------------------

if __name__ == "__main__": docker_run(sys.argv[1:])
