pipeline {
    agent any

    stages {
        stage('Stop Existing Containers') {
            steps {
                sh 'cd /mnt/ebs_volume/home/ubuntu/il8-v1/il8-aws-deployment/backend && sudo docker-compose down'
            }
        }

        stage('Clean Docker System') {
            steps {
                sh 'sudo docker system prune -a -f'
            }
        }

        stage('Build Docker Images') {
            steps {
                sh 'cd /mnt/ebs_volume/home/ubuntu/il8-v1/il8-aws-deployment/backend && sudo docker-compose build --no-cache'
            }
        }

        stage('Start Containers') {
            steps {
                sh 'cd /mnt/ebs_volume/home/ubuntu/il8-v1/il8-aws-deployment/backend && sudo docker-compose up -d'
            }
        }
    }
}
