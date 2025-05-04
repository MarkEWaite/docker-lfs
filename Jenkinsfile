pipeline {
    agent {
	dockerfile {
	    filename 'Dockerfile-alpine'
	    additionalBuildArgs '-u 1000:1000'
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
