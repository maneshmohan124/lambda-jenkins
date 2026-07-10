import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    Simple Hello World Lambda function.

    Parameters
    ----------
    event : dict
        The event payload passed to the Lambda function.
    context : LambdaContext
        Runtime information provided by AWS Lambda.

    Returns
    -------
    dict
        API Gateway-compatible response with statusCode and body.
    """
    logger.info("Lambda function invoked with event: %s", json.dumps(event))

    name = event.get("name", "World")

    response = {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": json.dumps({
            "message": f"Hello, {name}!",
            "event": event,
        }),
    }

    logger.info("Returning response: %s", json.dumps(response))
    return response
