pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/TenergyMX/SIA.git'
            }
        }
        stage('Deploy') {
            steps {
                script {
                    docker compose up --build -d
                }
            }
        }
    }
}