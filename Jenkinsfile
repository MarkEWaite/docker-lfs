pipeline {
    agent {
	dockerfile {
	    filename 'Dockerfile-alpine'
	}
    }
    stages {
        stage('Version Report') {
            steps {
                sh 'java -jar /usr/share/jenkins/jenkins.war --version; java --version'
            }
        }
    }
}
