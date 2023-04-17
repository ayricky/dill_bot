pipeline {
    agent any

    environment {
        GITHUB_TOKEN = credentials('ayricky-github')
    }

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

        stage('Create Release') {
            steps {
                script {
                    // Calculate the release version
                    def releaseVersion = "v0.${env.BUILD_NUMBER}"

                    // Create the release using the GitHub REST API
                    sh(script: """
                        curl -s -X POST \
                        -H "Authorization: token ${GITHUB_TOKEN}" \
                        -H "Content-Type: application/json" \
                        -d '{ "tag_name": "${releaseVersion}", "name": "${releaseVersion}", "body": "Release ${releaseVersion}", "target_commitish": "main" }' \
                        https://api.github.com/repos/ayricky/dill_do_bot/releases
                    """)
                }
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
