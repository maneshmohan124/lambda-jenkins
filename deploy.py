"""
Deploy script for AWS Lambda.

Usage:
    python3 deploy.py --action create|update|verify
"""

import argparse
import json
import os
import sys

try:
    import boto3
except ImportError:
    print("ERROR: boto3 is not installed. Run: python3 -m pip install boto3")
    sys.exit(1)


def get_env(name):
    """Get a required environment variable or exit."""
    value = os.environ.get(name, "").strip()
    if not value:
        print(f"ERROR: Environment variable '{name}' is not set.")
        sys.exit(1)
    return value


def create_function(client, config, zip_bytes):
    """Create a new Lambda function."""
    print(f"🆕 Creating new Lambda function '{config['function_name']}'...")
    response = client.create_function(
        FunctionName=config["function_name"],
        Runtime=config["runtime"],
        Handler=config["handler"],
        Role=config["role"],
        Code={"ZipFile": zip_bytes},
        Timeout=int(config["timeout"]),
        MemorySize=int(config["memory"]),
    )
    print(f"✅ Function created. ARN: {response['FunctionArn']}")
    return response


def update_function(client, config, zip_bytes):
    """Update an existing Lambda function's code and configuration."""
    print(f"🔄 Updating Lambda function '{config['function_name']}'...")

    # Update code
    client.update_function_code(
        FunctionName=config["function_name"],
        ZipFile=zip_bytes,
    )

    # Wait for the code update to finish
    print("⏳ Waiting for code update to complete...")
    waiter = client.get_waiter("function_updated_v2")
    waiter.wait(FunctionName=config["function_name"])

    # Update configuration
    print("🔧 Updating function configuration...")
    client.update_function_configuration(
        FunctionName=config["function_name"],
        Runtime=config["runtime"],
        Handler=config["handler"],
        Timeout=int(config["timeout"]),
        MemorySize=int(config["memory"]),
    )

    print("✅ Function updated successfully.")


def deploy(config, zip_path):
    """Create or update the Lambda function."""
    client = boto3.client("lambda", region_name=config["region"])

    with open(zip_path, "rb") as f:
        zip_bytes = f.read()

    # Check if the function already exists
    try:
        client.get_function(FunctionName=config["function_name"])
        exists = True
    except client.exceptions.ResourceNotFoundException:
        exists = False

    if exists:
        update_function(client, config, zip_bytes)
    else:
        create_function(client, config, zip_bytes)


def verify(config):
    """Invoke the Lambda function with a test payload."""
    client = boto3.client("lambda", region_name=config["region"])
    print(f"🧪 Invoking '{config['function_name']}' with test payload...")

    response = client.invoke(
        FunctionName=config["function_name"],
        Payload=json.dumps({"name": "Jenkins Pipeline"}),
    )

    payload = json.loads(response["Payload"].read())
    status = response["StatusCode"]

    print(f"📋 Status Code: {status}")
    print(f"📋 Response: {json.dumps(payload, indent=2)}")

    if status != 200:
        print("❌ Verification failed!")
        sys.exit(1)

    print("✅ Verification passed!")


def main():
    parser = argparse.ArgumentParser(description="Deploy Lambda function to AWS")
    parser.add_argument(
        "--action",
        choices=["deploy", "verify"],
        required=True,
        help="Action to perform",
    )
    parser.add_argument(
        "--zip-file",
        default="lambda_function.zip",
        help="Path to the deployment package",
    )
    args = parser.parse_args()

    config = {
        "region": get_env("AWS_REGION"),
        "function_name": get_env("LAMBDA_FUNCTION"),
        "runtime": get_env("LAMBDA_RUNTIME"),
        "handler": get_env("LAMBDA_HANDLER"),
        "role": get_env("LAMBDA_ROLE"),
        "timeout": get_env("LAMBDA_TIMEOUT"),
        "memory": get_env("LAMBDA_MEMORY"),
    }

    if args.action == "deploy":
        deploy(config, args.zip_file)
    elif args.action == "verify":
        verify(config)


if __name__ == "__main__":
    main()
