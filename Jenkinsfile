pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Extract Metadata') {
            steps {
                bat 'python scripts\\extract_metadata.py'
            }
        }

        stage('Upload File Storage') {
            steps {
                bat 'python scripts\\upload_filestorage.py'
            }
        }

        stage('Deploy PAS') {
            steps {
                bat 'python scripts\\deploy_pas.py'
            }
        }
    }

    post {
        success {
            echo "Deployment successful"
        }

        failure {
            echo "Deployment failed"
        }
    }
}