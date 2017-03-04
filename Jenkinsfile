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

    stage('Build') {
        docker.build('jenkins')
    }

}
