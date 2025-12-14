
pipeline {
    agent any

   test stages {
        stage('Build') {
            steps{
                sh 'python3 -m venv venv'
                sh './venv/bin/python -m pip install -r requirements.txt'
            }
        }
        stage('Test') {
            steps {
                sh 'rm -rf test-reports/'
                sh './venv/bin/python -m xmlrunner -o test-reports/'
            }
            post {
                always {
                    junit '**/test-reports/*.xml' 
                }
            }
        }
    }
}

