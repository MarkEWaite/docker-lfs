#!/usr/bin/env groovy

properties([
    buildDiscarder(logRotator(numToKeepStr: '7', artifactNumToKeepStr: '7')),
])

def docker_branch = 'lts-with-plugins'
def docker_repo = 'https://github.com/MarkEWaite/docker-lfs'

node('docker') {
    stage('Checkout') {
        checkout([$class: 'GitSCM',
                  userRemoteConfigs: [[name: 'public', url: docker_repo]]
                  branches: [[name: docker_branch]],
                  browser: [$class: 'GithubWeb', repoUrl: docker_repo],
                  extensions: [
                    [$class: 'AuthorInChangelog'],
                    [$class: 'CleanBeforeCheckout'],
                    [$class: 'CloneOption', noTags: true, shallow: true, depth: 1],
                    [$class: 'GitLFSPull'],
                    [$class: 'LocalBranch', localBranch: docker_branch],
                    [$class: 'PruneStaleBranch'],
                  ],
                  gitTool: 'Default',
                  doGenerateSubmoduleConfigurations: false,
                  submoduleCfg: [],
                ])
    }

    stage('Build') {
        docker.build('jenkins')
    }

}
