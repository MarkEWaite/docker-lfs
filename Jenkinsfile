pipeline {
    agent none
    stages {
	stage('Parallel') {
	    parallel {
		stage('Alpine') {
		    agent {
			dockerfile {
			    filename 'Dockerfile-alpine'
			}
		    }
		    steps {
			sh 'java -jar /usr/share/jenkins/jenkins.war --version; java --version'
		    }
		}
		stage('Slim') {
		    agent {
			dockerfile {
			    filename 'Dockerfile-slim'
			}
		    }
		    steps {
			sh 'java -jar /usr/share/jenkins/jenkins.war --version; java --version'
		    }
		}
	    }
	}
    }
}
