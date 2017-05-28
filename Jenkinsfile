#!/usr/bin/env groovy

properties([
    buildDiscarder(logRotator(numToKeepStr: '7', artifactNumToKeepStr: '7')),
])

node('docker') {
    stage('Checkout') {
        checkout([$class: 'GitSCM',
                  userRemoteConfigs: scm.userRemoteConfigs,
                  branches: scm.branches,
                  browser: scm.browser,
                  extensions: scm.extensions + [
                    [$class: 'GitLFSPull'],
                    [$class: 'LocalBranch', localBranch: '**'],
                  ],
                ])
    }

    if (!infra.isTrusted()) {

        stage('shellcheck') {
            docker.image('koalaman/shellcheck').inside() {
                // run shellcheck ignoring error SC1091
                // Not following: /usr/local/bin/jenkins-support was not specified as input
                sh "shellcheck -e SC1091 *.sh"
            }
        }

        /* Outside of the trusted.ci environment, we're building and testing
         * the Dockerfile in this repository, but not publishing to docker hub
         */
        stage('Build') {
            docker.build('jenkins')
        }

        stage('Test') {
            sh """
            git submodule update --init --recursive
            git clone https://github.com/sstephenson/bats.git
            bats/bin/bats tests
            """
        }
    } else {
        /* In our trusted.ci environment we only want to be publishing our
         * containers from artifacts
         */
        stage('Publish') {
            sh './publish.sh'
        }
    }

}
