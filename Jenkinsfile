pipeline {
    agent none
    stages {
	stage('Containers') {
	    parallel {
		stage('Alpine') {
		    agent {
			dockerfile {
			    filename 'Dockerfile-alpine'
			}
		    }
		    steps {
			sh 'java -jar /usr/share/jenkins/jenkins.war --version; cat /etc/os-release; java --version'
		    }
		}
		stage('Slim') {
		    agent {
			dockerfile {
			    filename 'Dockerfile-slim'
			}
		    }
		    steps {
			sh 'java -jar /usr/share/jenkins/jenkins.war --version; cat /etc/os-release; java --version'
		    }
		}
		stage('jdk17') {
		    agent {
			dockerfile {
			    filename 'Dockerfile-jdk17'
			}
		    }
		    steps {
			sh 'java -jar /usr/share/jenkins/jenkins.war --version; cat /etc/os-release; java --version'
		    }
		}
		stage('jdk21') {
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
