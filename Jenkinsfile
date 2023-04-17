pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'git@github.com:ayricky/dill_do_bot.git', credentialsId: 'jenkins-git-ssh'
                sh 'cp /home/ayrickypi/secret/dill_do_bot.env .env'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker-compose build'
            }
        }

        stage('Deploy') {
            steps {
                sh 'mkdir -p /var/lib/jenkins/discord_bots'
                sh 'docker-compose down -v'
                sh 'docker-compose up -d'
            }
        }
    }
}
