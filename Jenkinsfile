pipeline {
    agent none
    stages {
        stage('Launch') {
            agent {
                label '!windows'
            }
            steps {
                sh 'echo Branch is ${GIT_LOCAL_BRANCH}'
            }
        }
        stage('Containers') {
            parallel {
                stage('Alpine JDK 17') {
                    agent {
                        dockerfile {
                            filename 'Dockerfile-alpine'
                        }
                    }
                    steps {
                        sh 'java -jar /usr/share/jenkins/jenkins.war --version; cat /etc/os-release; java --version'
                    }
                }
            }
        }
    }
}
