import boto3
import json
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    code = event['pathParameters']['code']
    response = table.get_item(Key={'short_code': code})

    if 'Item' not in response:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Short URL not found'})
        }
    
    item = response['Item']
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'short_code': code,
            'original_url': item['original_url'],
            'clicks': int(item['clicks']),
            'created_at': item['created_at']
        })
    }