pipeline {
    agent {
	dockerfile {
	    filename 'Dockerfile-alpine'
            label 'markewaite-ci/lts:2.504.1-alpine'
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
