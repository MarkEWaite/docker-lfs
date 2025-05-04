pipeline {
    agent none
    stages {
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
    }
}
