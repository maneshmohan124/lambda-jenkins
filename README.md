# Hello World Lambda — Jenkins CI/CD

A simple AWS Lambda function (Python) deployed via a **Jenkins pipeline** from a GitHub repository.

## 📁 Project Structure

```
lambdajenkins/
├── Jenkinsfile              # Jenkins pipeline definition
├── lambda_function.py       # Lambda handler (Hello World)
├── requirements.txt         # Python dependencies
├── tests/
│   └── test_lambda_function.py   # Unit tests
├── .gitignore
└── README.md
```

## 🚀 Quick Start

### 1. Push to GitHub

```bash
cd /Users/maneshmohan/Documents/Zoom/vibecoding/lambdajenkins
git init
git add .
git commit -m "Initial commit: Hello World Lambda with Jenkins pipeline"
git remote add origin https://github.com/<YOUR_USERNAME>/<YOUR_REPO>.git
git branch -M main
git push -u origin main
```

### 2. Configure Jenkins

#### Prerequisites
- **Jenkins plugins** (install via *Manage Jenkins → Plugins*):
  - [Pipeline](https://plugins.jenkins.io/workflow-aggregator/)
  - [AWS Credentials](https://plugins.jenkins.io/aws-credentials/)
  - [Git](https://plugins.jenkins.io/git/)
- **AWS CLI** installed on the Jenkins agent (`aws --version`)
- **Python 3** installed on the Jenkins agent (`python3 --version`)
- **pytest** installed on the Jenkins agent (`pip3 install pytest`)

#### Add AWS Credentials
1. Go to **Jenkins → Manage Jenkins → Manage Credentials**.
2. Add a new credential of type **AWS Credentials**.
3. Set the **ID** to `aws-credentials` (must match `AWS_CREDENTIALS_ID` in the Jenkinsfile).
4. Enter your **Access Key ID** and **Secret Access Key**.

#### Create the Pipeline Job
1. Go to **Jenkins → New Item**.
2. Enter a name (e.g., `hello-world-lambda`) and select **Pipeline**.
3. Under **Pipeline**:
   - **Definition**: Pipeline script from SCM
   - **SCM**: Git
   - **Repository URL**: `https://github.com/<YOUR_USERNAME>/<YOUR_REPO>.git`
   - **Branch Specifier**: `*/main`
   - **Script Path**: `Jenkinsfile`
4. (Optional) Under **Build Triggers**, enable:
   - **GitHub hook trigger for GITScm polling** — for automatic builds on push.
5. Click **Save**.

#### Set the IAM Role ARN
Update the `LAMBDA_ROLE` environment variable in the [Jenkinsfile](./Jenkinsfile) with your IAM execution role ARN:

```groovy
LAMBDA_ROLE = 'arn:aws:iam::123456789012:role/lambda-execution-role'
```

> The IAM role needs `AWSLambdaBasicExecutionRole` at a minimum.

### 3. Run the Pipeline

Click **Build Now** in Jenkins or push a commit to trigger the pipeline.

## 🧪 Run Tests Locally

```bash
python3 -m pytest tests/ -v
```

## 📋 Pipeline Stages

| Stage                  | Description                                       |
|------------------------|---------------------------------------------------|
| **Checkout**           | Pulls code from GitHub                            |
| **Run Tests**          | Runs unit tests with pytest                       |
| **Install Dependencies** | Installs Python packages from `requirements.txt` |
| **Package Lambda**     | Zips the code into a deployment package            |
| **Deploy to AWS Lambda** | Creates or updates the Lambda function via AWS CLI |
| **Verify Deployment**  | Invokes the function with a test payload           |

## ⚙️ Configuration

All configuration is in the `environment` block of the [Jenkinsfile](./Jenkinsfile):

| Variable             | Default                            | Description                  |
|----------------------|------------------------------------|------------------------------|
| `AWS_REGION`         | `us-east-1`                        | AWS region                   |
| `LAMBDA_FUNCTION`    | `hello-world-lambda`               | Lambda function name         |
| `LAMBDA_RUNTIME`     | `python3.12`                       | Python runtime version       |
| `LAMBDA_HANDLER`     | `lambda_function.lambda_handler`   | Handler entry point          |
| `LAMBDA_ROLE`        | *(empty — must be set)*            | IAM execution role ARN       |
| `LAMBDA_TIMEOUT`     | `30`                               | Timeout in seconds           |
| `LAMBDA_MEMORY`      | `128`                              | Memory in MB                 |
| `AWS_CREDENTIALS_ID` | `aws-credentials`                  | Jenkins credential ID        |
