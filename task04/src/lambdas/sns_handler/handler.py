import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    for record in event['Records']:
        sns_message = record['Sns']['Message']
        logger.info(f"SNS Message: {sns_message}")
    return {
        'statusCode': 200,
        'body': json.dumps('Message logged successfully!')
    }
