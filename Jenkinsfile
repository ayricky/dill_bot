pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'git@github.com:ayricky/dill_do_bot.git', credentialsId: 'jenkins-git-ssh'
            }
        }

        stage('Lint with Ruff') {
            steps {
                sh 'docker run --rm ayricky/dill_do_bot poetry run ruff check .'
            }
        }
        
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t ayricky/dill_do_bot .'
            }
        }

        stage('Deploy') {
            steps {
                sh 'mkdir -p /var/lib/jenkins/discord_bots'
                sh 'docker cp $(docker create --rm ayricky/dill_do_bot):/app /var/lib/jenkins/discord_bots/dill_do_bot'
            }
        }
    }
}
