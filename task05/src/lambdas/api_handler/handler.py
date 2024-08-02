import json
import uuid
from datetime import datetime
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Events')

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        principal_id = body['principalId']
        content = body['content']

        event_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()

        response = table.put_item(
            Item={
                'id': event_id,
                'principalId': principal_id,
                'createdAt': created_at,
                'body': content
            }
        )

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
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
