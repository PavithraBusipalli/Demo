import json
import uuid
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Events')

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        event_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()

        item = {
            'id': event_id,
            'principalId': body['principalId'],
            'createdAt': created_at,
            'body': body['content']
        }

        table.put_item(Item=item)

        response = {
            'statusCode': 201,
            'body': json.dumps(item)
        }

        return response

    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
