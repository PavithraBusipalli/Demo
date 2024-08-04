import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    for record in event['Records']:
        message_body = record['body']
        logger.info(f"SQS Message Body: {message_body}")
    return {
        'statusCode': 200,
        'body': json.dumps('Message logged successfully!')
    }
