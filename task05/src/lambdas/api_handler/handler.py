import json
import uuid
import boto3
from datetime import datetime
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Events')

def lambda_handler(event, context):
    logger.info("Received event: %s", event)
    
    try:
        # Check if 'body' exists in the event and parse it
        if 'body' not in event:
            raise ValueError("Missing 'body' in event")

        body = json.loads(event['body'])
        
        if 'principalId' not in body or 'content' not in body:
            raise ValueError("Missing 'principalId' or 'content' in body")

        principal_id = body['principalId']
        content = body['content']
        
        # Generate a unique event ID and timestamp
        event_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()
        
        # Save to DynamoDB
        response = table.put_item(Item={
            'id': event_id,
            'principalId': principal_id,
            'createdAt': created_at,
            'body': content
        })
        
        logger.info("DynamoDB response: %s", response)
        
        # Return the response
        return {
            'statusCode': 201,
            'body': json.dumps({
                'id': event_id,
                'principalId': principal_id,
                'createdAt': created_at,
                'body': content
            })
        }
    
    except Exception as e:
        logger.error("Error processing request: %s", e)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
