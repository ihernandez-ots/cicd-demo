pipeline {
    agent any

    environment{
        TARGET_KEYCLOAK_USERNAME = 'vvallejo'
        TARGET_KEYCLOAK_PASSWORD = 'Asdf!234'
        TARGET_KEYCLOAK_CLIENT_ID = 'tokengen'
        TARGET_KEYCLOAK_CLIENT_SECRET = 'gEXWygCsf1TrtzOp7ZA2F90LY9PygEh2'
        FILE_STORAGE_NAMESPACE = 'sandbox_vvallejo'

        HARBOR_URL='https://k8s.onetoolapps.com/pas/api/service-repository/docker/image'
        FILE_STORAGE_BASE_URL = 'https://k8s.onetoolapps.com/pas/api/file-storage/files'
        XUML_URL='https://k8s.onetoolapps.com/pas/api/service-repository/xuml'

        RUNTIME_VERSION='xuml-service-base:2025.12'
        VERIFY_SSL=false

    }

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