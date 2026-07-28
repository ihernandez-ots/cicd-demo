pipeline {
    agent any

    stages {

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