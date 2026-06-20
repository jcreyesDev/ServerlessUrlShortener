import json
import boto3
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
    original_url = item['original_url']

    table.update_item(Key={'short_code': code},
                      UpdateExpression='ADD clicks :inc',
                      ExpressionAttributeValues={':inc': 1}
    )

    return {
        'statusCode': 301,
        'headers': {'Location': original_url}
    }