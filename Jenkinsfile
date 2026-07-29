pipeline {
    agent any

    stages {
        
        stage('Environment Check') {
            steps {
                bat '''
                    python --version
                    where python
                    cd
                    dir
                '''
            }
}
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Discover REP Files') {
            steps {
                bat 'python scripts\\list_changes.py'
            }
        }

        stage('Deploy') {
            steps {
                bat 'python scripts\\deploy.py'
            }
        }
    }
}