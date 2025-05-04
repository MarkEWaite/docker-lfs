pipeline {
    agent {
	dockerfile {
	    filename 'Dockerfile-alpine'
	}
    }
    stages {
        stage('Version Report') {
            steps {
                sh 'java --version; java -jar /usr/share/jenkins/jenkins.war --version'
            }
        }
    }
}
