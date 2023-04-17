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

        stage('Create Tag and Push') {
            steps {
                script {
                    // Get the current commit hash
                    def commitHash = sh(returnStdout: true, script: 'git rev-parse HEAD').trim()

                    // Get the Jenkins build number
                    def buildNumber = env.BUILD_NUMBER

                    // Set your Git user and email (replace with your actual user and email)
                    sh 'git config user.name "Ricardo Mariano"'
                    sh 'git config user.email "marianoricardo97@gmail.com"'

                    // Create the tag
                    sh "git tag -a -f -m 'Jenkins Build #${buildNumber}' jenkins-dill_do_bot-${buildNumber} ${commitHash}"
                    
                    // Push the tag to the remote repository
                    sh "git push origin jenkins-dill_do_bot-${buildNumber}"
                }
            } // Missing closing brace added here
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
