from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda
import boto3
import json
import uuid
import os
from decimal import Decimal
from datetime import datetime

_LOG = get_logger('ApiHandler-handler')

client = boto3.client('cognito-idp')
user_pool_name = os.environ.get('USER_POOL')
client_app = 'client-app'

user_pool_id = None
response = client.list_user_pools(MaxResults=60)
for user_pool in response.get('UserPools', []):
    if user_pool.get('Name') == user_pool_name:
        user_pool_id = user_pool.get('Id')
        break
_LOG.info(f'user pool id: {user_pool_id}')

client_app_id = None
response = client.list_user_pool_clients(UserPoolId=user_pool_id)
for user_pool_client in response.get('UserPoolClients', []):
    if user_pool_client.get('ClientName') == client_app:
        client_app_id = user_pool_client.get('ClientId')
        break
_LOG.info(f'Client app id: {client_app_id}')

dynamodb = boto3.resource('dynamodb')
tables_name = dynamodb.Table(os.environ.get('TABLES'))
reservations_name = dynamodb.Table(os.environ.get('RESERVATIONS'))

def decimal_serializer(obj):
    if isinstance(obj, Decimal):
        return int(obj)
    raise TypeError("Type not serializable")

def lambda_handler(event, context):
    path = event.get('path', '')
    http_method = event.get('httpMethod', '')
    
    _LOG.info(f'{path} {http_method}')
    try:
        if path == '/signup' and http_method == 'POST':
            body = json.loads(event.get('body', '{}'))
            email = body.get('email')
            first_name = body.get('firstName')
            last_name = body.get('lastName')
            password = body.get('password')
            _LOG.info(f'{email}, {first_name}, {last_name}, {password}')

            response = client.admin_create_user(
                UserPoolId=user_pool_id,
                Username=email,
                UserAttributes=[
                    {'Name': 'email', 'Value': email},
                    {'Name': 'given_name', 'Value': first_name},
                    {'Name': 'family_name', 'Value': last_name}
                ],
                TemporaryPassword=password,
                MessageAction='SUPPRESS'
            )
            _LOG.info(f'Create User Response: {response}')

            response = client.admin_set_user_password(
                UserPoolId=user_pool_id,
                Username=email,
                Password=password,
                Permanent=True
            )
            _LOG.info(f'Set password Response: {response}')

            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': json.dumps({"message": "Sign-up process is successful"})
            }
            
        elif path == '/signin' and http_method == 'POST':
            body = json.loads(event.get('body', '{}'))
            email = body.get('email')
            password = body.get('password')
            _LOG.info(f'{email}, {password}')

            response = client.initiate_auth(
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': email,
                    'PASSWORD': password
                },
                ClientId=client_app_id
            )
            access_token = response['AuthenticationResult']['AccessToken']
            id_token = response['AuthenticationResult']['IdToken']
            _LOG.info(f'accessToken: {access_token}')
            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': json.dumps({'accessToken': id_token})
            }
        
        elif path == '/tables' and http_method == 'GET':
            response = tables_name.scan()
            _LOG.info(response)
            items = response.get('Items', [])
            tables = {'tables': sorted(items, key=lambda item: item.get('id'))}
            body = json.dumps(tables, default=decimal_serializer)
            _LOG.info(f"{body=}")
            
            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': body
            }
        
        elif path == '/tables' and http_method == 'POST':
            body = json.loads(event.get('body', '{}'))
            item = {
                "id": int(body.get('id', 0)),
                "number": body.get('number'),
                "places": body.get('places'),
                "isVip": body.get('isVip'),
                "minOrder": body.get('minOrder')
            }
            response = tables_name.put_item(Item=item)
            
            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': json.dumps({"id": body.get('id')})
            }
        
        elif path.startswith('/tables/') and http_method == 'GET':
            table_id = int(path.split('/')[-1])
            _LOG.info(f"table id {table_id}")
            item = tables_name.get_item(Key={'id': table_id})
            body = item.get("Item", {})
            _LOG.info(f"tablesid {body}")
            
            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': json.dumps(body, default=decimal_serializer)
            }
        
        elif path == '/reservations' and http_method == 'GET':
            _LOG.info("reservations get")
            response = reservations_name.scan()
            items = response.get('Items', [])
            _LOG.info(f'Reservation get {items}')
            for i in items:
                i.pop("id", None)
            _LOG.info(items)
            items = sorted(items, key=lambda item: item.get('tableNumber'))
            _LOG.info(items)
            reservations = {"reservations": items}
            _LOG.info(reservations)
            
            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': json.dumps(reservations, default=decimal_serializer)
            }
        
        elif path == '/reservations' and http_method == 'POST':
            item = json.loads(event.get('body', '{}'))
            _LOG.info(item)
            tables_response = tables_name.scan()
            tables = tables_response.get('Items', [])
            _LOG.info(f'reservattions post Tables {tables}')
            table_numbers = [table.get("number") for table in tables]
            if item.get('tableNumber') not in table_numbers:
                raise ValueError("No such table.")
                
            proposed_time_start = datetime.strptime(item.get("slotTimeStart"), "%H:%M").time()
            proposed_time_end = datetime.strptime(item.get("slotTimeEnd"), "%H:%M").time()

            reservations_response = reservations_name.scan()
            reservations = reservations_response.get('Items', [])
            _LOG.info(f'reservations table: {reservations}')

            for reserved in reservations:
                if reserved.get('tableNumber') != item.get('tableNumber'):
                    continue
                if reserved.get('date') != item.get('date'):
                    continue

                reserved_time_start = datetime.strptime(reserved.get("slotTimeStart"), "%H:%M").time()
                reserved_time_end = datetime.strptime(reserved.get("slotTimeEnd"), "%H:%M").time()
                if any([reserved_time_start <= proposed_time <= reserved_time_end for proposed_time in (proposed_time_start, proposed_time_end)]):
                    raise ValueError('Time already reserved')
            
            reservation_id = str(uuid.uuid4())
            response = reservations_name.put_item(Item={"id": reservation_id, **item})
            _LOG.info(response)
            
            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': json.dumps({"reservationId": reservation_id})
            }
    
    except Exception as e:
        _LOG.error(f'{e}')
        return {
            'statusCode': 400,
            'headers': cors_headers(),
            'body': json.dumps({'message': 'Something went wrong'})
        }

def cors_headers():
    return {
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': '*',
        'Accept-Version': '*'
    }
