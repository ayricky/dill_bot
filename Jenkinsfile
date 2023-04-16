pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'git@github.com:ayricky/dill_do_bot.git', credentialsId: 'jenkins-git-ssh'
            }
        }

        stage('Setup Environment') {
            steps {
                script {
                    if (sh(script: 'command -v poetry', returnStatus: true) != 0) {
                        sh 'curl -sSL https://install.python-poetry.org | python3 -'
                    }
                }
                withEnv(["PATH+POETRY=${env.HOME}/.local/bin"]) {
                    sh 'poetry install'
                }
            }
        }

        stage('Lint with Ruff') {
            steps {
                withEnv(["PATH+POETRY=${env.HOME}/.local/bin"]) {
                    sh 'poetry run ruff check .'
                }
            }
        }

        stage('Deploy') {
            steps {
                sh 'mkdir -p /var/lib/jenkins/discord_bots'
                sh 'rsync -avz --delete --exclude ".git" --exclude "__pycache__" --exclude "venv" . /var/lib/jenkins/discord_bots/dill_do_bot'
            }
        }


        // stage('Run Bot') {
        //     steps {
        //         sh '''
        //             cd ~/discord_bots/dill_do_bot && \
        //             source ~/.poetry/env && \
        //             poetry install && \
        //             pkill -f your_bot_script.py || true && \
        //             nohup poetry run python your_bot_script.py > nohup.out 2>&1 &
        //         '''
        //     }
        // }
    }
}
