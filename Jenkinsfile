pipeline {
    agent none
    stages {
        stage('Launch') {
            steps {
                echo "Branch is ${env.GIT_BRANCH}"
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
                stage('Slim JDK 17') {
                    agent {
                        dockerfile {
                            filename 'Dockerfile-slim'
                        }
                    }
                    steps {
                        sh 'java -jar /usr/share/jenkins/jenkins.war --version; cat /etc/os-release; java --version'
                    }
                }
                stage('UBI-9 JDK 17') {
                    agent {
                        dockerfile {
                            filename 'Dockerfile-jdk17'
                        }
                    }
                    steps {
                        sh 'java -jar /usr/share/jenkins/jenkins.war --version; cat /etc/os-release; java --version'
                    }
                }
                stage('Debian JDK 21') {
                    agent {
                        dockerfile {
                            filename 'Dockerfile-jdk21'
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
