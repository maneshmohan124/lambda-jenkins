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
        LAMBDA_ROLE        = 'arn:aws:iam::180273188642:role/lambda_jenkins_role'  // IAM Role ARN
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

        // ── 3. Setup & Install Dependencies ────────
        stage('Setup & Install Dependencies') {
            steps {
                echo '📦 Setting up tools and dependencies...'
                sh '''
                    # Install boto3 (needed for deploy.py) using python3 -m pip
                    python3 -m pip install --user boto3 2>/dev/null || \
                    python3 -m ensurepip --user 2>/dev/null && python3 -m pip install --user boto3 || \
                    echo "⚠️  Could not install boto3 via pip — checking if already available..."

                    # Verify boto3 is importable
                    python3 -c "import boto3; print('✅ boto3', boto3.__version__, 'is available')"

                    # Create a clean package directory
                    rm -rf package/
                    mkdir -p package/

                    # Install Lambda dependencies only if requirements.txt has real entries
                    if grep -qvE '^\\s*#|^\\s*$' requirements.txt 2>/dev/null; then
                        echo "📦 Found dependencies — installing..."
                        python3 -m pip install -r requirements.txt -t package/ --upgrade
                    else
                        echo "ℹ️  No Lambda dependencies to install — skipping."
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
                    python3 -c "
import zipfile, os
with zipfile.ZipFile('${ZIP_FILE}', 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk('package'):
        for f in files:
            full = os.path.join(root, f)
            arcname = os.path.relpath(full, 'package')
            zf.write(full, arcname)
"
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
                        python3 deploy.py --action deploy --zip-file ${ZIP_FILE}
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
                        python3 deploy.py --action verify
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
