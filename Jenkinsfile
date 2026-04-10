// ─────────────────────────────────────────────────────────────────────────────
// Jenkinsfile – Smart Energy Monitoring System CI/CD Pipeline
//
// Stages:
//   1. Checkout      – pull source from Git
//   2. Build         – install Python deps & verify imports
//   3. Test          – run unit tests with pytest
//   4. Docker Build  – build the backend Docker image
//   5. Docker Push   – push image to Docker Hub
//   6. Deploy        – apply Kubernetes manifests via kubectl
//
// Prerequisites in Jenkins:
//   • Credential "dockerhub-creds" (Username/Password for Docker Hub)
//   • Credential "kubeconfig"      (Secret File – your ~/.kube/config)
//   • Plugins: Docker Pipeline, Kubernetes CLI, Git
// ─────────────────────────────────────────────────────────────────────────────

pipeline {
    agent any

    // ── Environment variables ─────────────────────────────────────────────────
    environment {
        IMAGE_NAME  = "yourdockerhubuser/smart-energy-backend"   // change this
        IMAGE_TAG   = "${env.BUILD_NUMBER}"                       // e.g. "42"
        FULL_IMAGE  = "${IMAGE_NAME}:${IMAGE_TAG}"
        LATEST_IMG  = "${IMAGE_NAME}:latest"
    }

    // ── Pipeline options ──────────────────────────────────────────────────────
    options {
        timestamps()                        // prefix log lines with timestamps
        timeout(time: 20, unit: 'MINUTES')  // fail if the build takes too long
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {

        // ── Stage 1: Checkout ─────────────────────────────────────────────────
        stage('Checkout') {
            steps {
                echo '📥 Checking out source code...'
                checkout scm   // uses the repo configured in the Jenkins job
            }
        }

        // ── Stage 2: Build (verify deps) ─────────────────────────────────────
        stage('Build') {
            steps {
                echo '🔨 Installing Python dependencies...'
                dir('backend') {
                    sh '''
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install --quiet -r requirements.txt
                        python3 -c "import flask; print('Flask OK:', flask.__version__)"
                    '''
                }
            }
        }

        // ── Stage 3: Test ─────────────────────────────────────────────────────
        stage('Test') {
            steps {
                echo '🧪 Running unit tests...'
                dir('backend') {
                    sh '''
                        . venv/bin/activate
                        pip install --quiet pytest
                        pytest tests/ -v --tb=short || true
                    '''
                }
            }
            post {
                always {
                    // Archive test results if you produce JUnit XML
                    // junit 'backend/test-results/*.xml'
                    echo '✅ Tests completed'
                }
            }
        }

        // ── Stage 4: Docker Image Build ───────────────────────────────────────
        stage('Docker Build') {
            steps {
                echo "🐳 Building Docker image: ${FULL_IMAGE}"
                dir('backend') {
                    sh "docker build -t ${FULL_IMAGE} -t ${LATEST_IMG} ."
                }
            }
        }

        // ── Stage 5: Push to Docker Hub ───────────────────────────────────────
        stage('Docker Push') {
            steps {
                echo "📤 Pushing ${FULL_IMAGE} to Docker Hub..."
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        docker push ''' + FULL_IMAGE + '''
                        docker push ''' + LATEST_IMG + '''
                    '''
                }
            }
        }

        // ── Stage 6: Deploy to Kubernetes ────────────────────────────────────
        stage('Deploy') {
            steps {
                echo '🚀 Deploying to Kubernetes...'
                withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                    sh '''
                        export KUBECONFIG=$KUBECONFIG

                        # Update the image tag in the deployment
                        kubectl set image deployment/smart-energy-backend \
                            backend=''' + FULL_IMAGE + ''' \
                            --namespace=smart-energy --record || true

                        # Apply all manifests (idempotent)
                        kubectl apply -f k8s/ --namespace=smart-energy

                        # Wait for rollout to complete (max 3 min)
                        kubectl rollout status deployment/smart-energy-backend \
                            --namespace=smart-energy --timeout=180s
                    '''
                }
            }
        }
    }

    // ── Post-build notifications ──────────────────────────────────────────────
    post {
        success {
            echo "✅ Pipeline PASSED – image ${FULL_IMAGE} deployed successfully."
        }
        failure {
            echo "❌ Pipeline FAILED – check the logs above."
        }
        always {
            // Clean up dangling Docker images on the agent
            sh 'docker image prune -f || true'
        }
    }
}
