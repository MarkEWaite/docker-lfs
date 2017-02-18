#!/usr/bin/env groovy

properties([
    buildDiscarder(logRotator(numToKeepStr: '7', artifactNumToKeepStr: '7')),
])

node('docker') {
    deleteDir()

    stage('Checkout') {
        checkout scm
    }

    stage('Build') {
        docker.build('jenkins')
    }

}
