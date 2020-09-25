import json
import boto3
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    table_name = 'counties_with_deaths'
    dynamodb=boto3.resource('dynamodb')
    client = boto3.client('dynamodb')
    table = dynamodb.Table(table_name)
    fips = event['queryStringParameters']['fips']
    try :
        response = table.query(KeyConditionExpression=Key('state_fips').eq(fips))
        items = response['Items']
    except Exception as inst:
        resp = {
            'statusCode': 404,
            'body': f'{event.keys()}'
        }
        return resp
    
    features = []
    for item in items:
        features.append(item['feature'])
        
    obj={'type': 'FeatureCollection', 'features': features}
    json_str = json.dumps(obj)
    resp= {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": "*"
        },
        'body': json_str,
        'len': len(json_str),
        'num_features': len(features)
        }
    return resp
