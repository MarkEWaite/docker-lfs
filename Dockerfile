FROM jenkins/jenkins:2.294

LABEL maintainer="mark.earl.waite@gmail.com"

# Check that expected utilities are available in the image
RUN ps -ef | grep UID && git lfs version | grep git-lfs/ && wget -V 2>&1 | grep -i free

# jenkins.war checksum, download will be validated using it
ARG JENKINS_SHA=075fb3ad4e9d8839e9998e189499279504535616a0d839846aa96eb1aa3e14a0

ARG JENKINS_URL=https://home.markwaite.net/~mwaite/jenkins-builds/2.294-fix-submit-event/jenkins.war

# could use ADD but this one does not check Last-Modified header neither does it allow to control checksum
# see https://github.com/docker/docker/issues/8331
USER root
RUN curl -fsSL ${JENKINS_URL} -o /usr/share/jenkins/jenkins.war \
  && echo "${JENKINS_SHA}  /usr/share/jenkins/jenkins.war" | sha256sum -c -
USER jenkins

# $REF (defaults to `/usr/share/jenkins/ref/`) contains all reference configuration we want
# to set on a fresh new installation. Use it to bundle additional plugins
# or config file with your custom jenkins Docker image.
COPY --chown=jenkins:jenkins ref /usr/share/jenkins/ref/

ENV CASC_JENKINS_CONFIG ${JENKINS_HOME}/jenkins.yaml
