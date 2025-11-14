pipeline {
    agent any

    environment {
        DOCKER_CREDENTIALS_ID = 'roseaw-dockerhub'
        DOCKER_IMAGE = 'cithit/hibbarkm'       
        IMAGE_TAG = "build-${BUILD_NUMBER}"
        GITHUB_URL = 'https://github.com/Hibbarkm/225-lab5-1.git'
        KUBECONFIG = credentials('hibbarkm-225')
        POD_LABEL = 'app=flask-dev'
        CONTAINER_NAME = 'flask-dev'
        BASE_URL = 'http://flask-dev-service:5000'
    }

    stages {
        stage('Code Checkout') {
            steps {
                cleanWs()
                checkout([$class: 'GitSCM', 
                          branches: [[name: '*/main']],
                          userRemoteConfigs: [[url: "${GITHUB_URL}"]]])
            }
        }

        stage('Lint HTML') {
            steps {
                sh 'npm install htmlhint --save-dev'
                sh 'npx htmlhint *.html'
            }
        }

        stage('Build & Push Docker Image') {
            steps {
                script {
                    docker.withRegistry('https://registry.hub.docker.com', "${DOCKER_CREDENTIALS_ID}") {
                        def app = docker.build("${DOCKER_IMAGE}:${IMAGE_TAG}", "-f Dockerfile.build .")
                        app.push()
                    }
                }
            }
        }

        stage('Deploy to Dev Environment') {
            steps {
                script {
                    sh "kubectl delete --all deployments --namespace=default || true"
                    sh "sed -i 's|${DOCKER_IMAGE}:latest|${DOCKER_IMAGE}:${IMAGE_TAG}|' deployment-dev.yaml"
                    sh "kubectl apply -f deployment-dev.yaml"
                }
            }
        }

        stage('Run Security Checks') {
            steps {
                sh 'docker pull public.ecr.aws/portswigger/dastardly:latest'
                sh '''
                    docker run --user $(id -u) -v ${WORKSPACE}:${WORKSPACE}:rw \
                    -e HOME=${WORKSPACE} \
                    -e BURP_START_URL=http://10.48.229.148 \
                    -e BURP_REPORT_FILE_PATH=${WORKSPACE}/dastardly-report.xml \
                    public.ecr.aws/portswigger/dastardly:latest
                '''
            }
        }

        stage('Reset DB After Security Checks') {
            steps {
                script {
                    def appPod = sh(script: 
                        "kubectl get pods -l ${POD_LABEL} -o jsonpath='{.items[0].metadata.name}'",
                        returnStdout: true).trim()

                    sh """
                    kubectl exec ${appPod} -c ${CONTAINER_NAME} -- python3 - <<'PY'
import sqlite3
DB_PATH = '/nfs/demo.db'
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute('DELETE FROM parts')
conn.commit()
conn.close()
PY
                    """
                }
            }
        }

        stage('Generate Test Data') {
            steps {
                script {
                    def appPod = sh(script:
                        "kubectl get pods -l ${POD_LABEL} -o jsonpath='{.items[0].metadata.name}'",
                        returnStdout: true).trim()

                    sh "sleep 15"
                    sh "kubectl exec ${appPod} -c ${CONTAINER_NAME} -- python3 data-gen.py"
                }
            }
        }

        stage('Run Acceptance Tests') {
            steps {
                script {

                    // Clean old container safely
                    sh 'docker stop qa-tests || true'
                    sh 'docker rm qa-tests || true'

                    // Build the Firefox/Selenium Test Image
                    sh 'docker build -t qa-tests -f Dockerfile.test .'

                    // Run tests inside Xvfb-enabled container
                    sh """
                        docker run \
                        -e BASE_URL=${BASE_URL} \
                        --name qa-tests \
                        qa-tests
                    """
                }
            }
        }

        stage('Remove Test Data') {
            steps {
                script {
                    def appPod = sh(script:
                        "kubectl get pods -l ${POD_LABEL} -o jsonpath='{.items[0].metadata.name}'",
                        returnStdout: true).trim()

                    sh "kubectl exec ${appPod} -c ${CONTAINER_NAME} -- python3 data-clear.py"
                }
            }
        }

        stage('Deploy to Prod Environment') {
            steps {
                script {
                    sh "sed -i 's|${DOCKER_IMAGE}:latest|${DOCKER_IMAGE}:${IMAGE_TAG}|' deployment-prod.yaml"
                    sh "kubectl apply -f deployment-prod.yaml"
                }
            }
        }

        stage('Check Kubernetes Cluster') {
            steps {
                sh "kubectl get all"
            }
        }
    }

    post {
        success {
            slackSend color: "good", message: "Build Completed: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
        }
        unstable {
            slackSend color: "warning", message: "Build Completed: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
        }
        failure {
            slackSend color: "danger", message: "Build Completed: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
        }
    }
}
