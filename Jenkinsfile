pipeline {
    agent any

    // ──────────────────────────────────────────────
    // CONFIGURATION — update these for your environment
    // ──────────────────────────────────────────────
    environment {
        AWS_REGION         = 'us-east-1'                        // AWS region where the Lambda lives
        LAMBDA_FUNCTION    = 'hello-world-lambda'               // Name of the Lambda function in AWS
        LAMBDA_RUNTIME     = 'python3.12'                       // Lambda runtime version
        LAMBDA_HANDLER     = 'lambda_function.lambda_handler'   // <file_name>.<function_name>
        LAMBDA_ROLE        = ''                                 // IAM Role ARN — set via Jenkins credentials or here
        LAMBDA_TIMEOUT     = '30'                               // Timeout in seconds
        LAMBDA_MEMORY      = '128'                              // Memory in MB
        ZIP_FILE           = 'lambda_function.zip'              // Deployment package name

        // Jenkins credential IDs (configure these in Jenkins → Manage Credentials)
        AWS_CREDENTIALS_ID = 'aws-credentials'                  // Jenkins credential ID for AWS access
    }

    options {
        timestamps()
        timeout(time: 15, unit: 'MINUTES')
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {

        // ── 1. Checkout ────────────────────────────
        stage('Checkout') {
            steps {
                echo '📥 Checking out source code...'
                checkout scm
            }
        }

        // ── 2. Unit Tests ──────────────────────────
        stage('Run Tests') {
            steps {
                echo '🧪 Running unit tests...'
                sh '''
                    python3 -m pytest tests/ -v --tb=short || \
                    python3 -m unittest discover -s tests -v
                '''
            }
        }

        // ── 3. Install Dependencies ────────────────
        stage('Install Dependencies') {
            steps {
                echo '📦 Installing Python dependencies...'
                sh '''
                    # Create a clean package directory
                    rm -rf package/
                    mkdir -p package/

                    # Install dependencies into the package directory
                    if [ -s requirements.txt ]; then
                        pip3 install -r requirements.txt -t package/ --upgrade
                    fi

                    # Copy Lambda source code into the package directory
                    cp lambda_function.py package/
                '''
            }
        }

        // ── 4. Package ────────────────────────────
        stage('Package Lambda') {
            steps {
                echo '📦 Creating deployment package...'
                sh '''
                    cd package/
                    zip -r9 ../${ZIP_FILE} .
                    cd ..
                    echo "✅ Package created: $(ls -lh ${ZIP_FILE})"
                '''
            }
        }

        // ── 5. Deploy ──────────────────────────────
        stage('Deploy to AWS Lambda') {
            steps {
                echo '🚀 Deploying to AWS Lambda...'
                withCredentials([
                    [
                        $class: 'AmazonWebServicesCredentialsBinding',
                        credentialsId: "${AWS_CREDENTIALS_ID}",
                        accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                        secretKeyVariable: 'AWS_SECRET_ACCESS_KEY'
                    ]
                ]) {
                    sh '''
                        # Check if the Lambda function already exists
                        if aws lambda get-function \
                            --function-name ${LAMBDA_FUNCTION} \
                            --region ${AWS_REGION} > /dev/null 2>&1; then

                            echo "🔄 Updating existing Lambda function..."
                            aws lambda update-function-code \
                                --function-name ${LAMBDA_FUNCTION} \
                                --zip-file fileb://${ZIP_FILE} \
                                --region ${AWS_REGION}

                            echo "⏳ Waiting for function update to complete..."
                            aws lambda wait function-updated-v2 \
                                --function-name ${LAMBDA_FUNCTION} \
                                --region ${AWS_REGION}

                            echo "🔧 Updating function configuration..."
                            aws lambda update-function-configuration \
                                --function-name ${LAMBDA_FUNCTION} \
                                --runtime ${LAMBDA_RUNTIME} \
                                --handler ${LAMBDA_HANDLER} \
                                --timeout ${LAMBDA_TIMEOUT} \
                                --memory-size ${LAMBDA_MEMORY} \
                                --region ${AWS_REGION}

                        else
                            echo "🆕 Creating new Lambda function..."
                            aws lambda create-function \
                                --function-name ${LAMBDA_FUNCTION} \
                                --runtime ${LAMBDA_RUNTIME} \
                                --handler ${LAMBDA_HANDLER} \
                                --role ${LAMBDA_ROLE} \
                                --zip-file fileb://${ZIP_FILE} \
                                --timeout ${LAMBDA_TIMEOUT} \
                                --memory-size ${LAMBDA_MEMORY} \
                                --region ${AWS_REGION}
                        fi

                        echo "✅ Deployment complete!"
                    '''
                }
            }
        }

        // ── 6. Verify Deployment ───────────────────
        stage('Verify Deployment') {
            steps {
                echo '✅ Verifying deployment...'
                withCredentials([
                    [
                        $class: 'AmazonWebServicesCredentialsBinding',
                        credentialsId: "${AWS_CREDENTIALS_ID}",
                        accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                        secretKeyVariable: 'AWS_SECRET_ACCESS_KEY'
                    ]
                ]) {
                    sh '''
                        # Invoke the Lambda function with a test payload
                        aws lambda invoke \
                            --function-name ${LAMBDA_FUNCTION} \
                            --payload '{"name": "Jenkins Pipeline"}' \
                            --cli-binary-format raw-in-base64-out \
                            --region ${AWS_REGION} \
                            response.json

                        echo "📋 Lambda response:"
                        cat response.json
                        echo ""

                        # Cleanup
                        rm -f response.json
                    '''
                }
            }
        }
    }

    post {
        success {
            echo '🎉 Pipeline completed successfully! Lambda function deployed.'
        }
        failure {
            echo '❌ Pipeline failed. Check the logs above for details.'
        }
        cleanup {
            echo '🧹 Cleaning up workspace...'
            sh 'rm -rf package/ ${ZIP_FILE} response.json 2>/dev/null || true'
        }
    }
}
