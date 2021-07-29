FROM jenkins/jenkins:2.289.3-lts

LABEL maintainer="mark.earl.waite@gmail.com"

# Check that expected utilities are available in the image
RUN ps -ef | grep UID && git lfs version | grep git-lfs/ && wget -V 2>&1 | grep -i free

# $REF (defaults to `/usr/share/jenkins/ref/`) contains all reference configuration we want
# to set on a fresh new installation. Use it to bundle additional plugins
# or config file with your custom jenkins Docker image.
COPY --chown=jenkins:jenkins ref /usr/share/jenkins/ref/

ENV CASC_JENKINS_CONFIG ${JENKINS_HOME}/jenkins.yaml
