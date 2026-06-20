import json
import boto3
import os
import secrets
import string
from datetime import datetime, timezone

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def generate_code(table, length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    
    while True:
        code = ''.join(secrets.choice(chars) for _ in range(length))
        response = table.get_item(Key={'short_code': code})
        
        if 'Item' not in response:
            return code

def lambda_handler(event, context):
    body = json.loads(event['body'])
    url = body['url']
    code = generate_code(table)

    table.put_item(Item={
        'short_code': code,
        'original_url': url,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'clicks': 0
    })

    domain = event['headers']['Host']
    stage = event['requestContext']['stage']
    short_url = f'https://{domain}/{stage}/{code}'

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'short_code': code,
            'short_url': short_url,
            'original_url': url
        })
    }