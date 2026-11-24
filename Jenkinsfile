pipeline {
    agent any

    // Webhook: a push to GitHub starts this pipeline automatically
    triggers { githubPush() }

    // We do the checkout ourselves in the "Checkout" stage
    options { skipDefaultCheckout() }

    environment {
        APP_IMAGE   = "cicd-site:${BUILD_NUMBER}"
        TEST_IMAGE  = "cicd-site-tests:${BUILD_NUMBER}"
        NET         = "cicd-net"
        STAGING     = "site-staging-${BUILD_NUMBER}"
        TEST_CTR    = "site-tests-${BUILD_NUMBER}"
        PROD        = "site-prod"
        PROD_PORT   = "8081"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Package') {
            steps {
                sh 'docker build -t $APP_IMAGE .'
                sh 'docker build -t $TEST_IMAGE tests'
            }
        }

        stage('Start Staging') {
            steps {
                sh '''
                    docker network inspect $NET >/dev/null 2>&1 || docker network create $NET
                    docker rm -f $STAGING >/dev/null 2>&1 || true
                    docker run -d --name $STAGING --network $NET $APP_IMAGE
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    rm -rf test-results && mkdir -p test-results
                    set +e
                    docker run --name $TEST_CTR --network $NET \
                        -e BASE_URL=http://$STAGING $TEST_IMAGE
                    STATUS=$?
                    set -e
                    docker cp $TEST_CTR:/tests/results/. test-results/ || true
                    docker rm -f $TEST_CTR >/dev/null 2>&1 || true
                    exit $STATUS
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'test-results/*.xml'
                    archiveArtifacts artifacts: 'test-results/*.png', allowEmptyArchive: true
                }
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    docker rm -f $PROD >/dev/null 2>&1 || true
                    docker run -d --name $PROD -p $PROD_PORT:80 --restart unless-stopped $APP_IMAGE
                '''
                echo "Deployed: open http://localhost:${PROD_PORT}"
            }
        }
    }

    post {
        always {
            sh 'docker rm -f $STAGING >/dev/null 2>&1 || true'
        }
        failure {
            echo 'Pipeline failed - Deploy was skipped, live site is unchanged.'
        }
    }
}
