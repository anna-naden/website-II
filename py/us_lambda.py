import json
import boto3

def lambda_handler(event, context):
    import boto3

    table_name = 'state-features'
    dynamodb=boto3.resource('dynamodb')
    client = boto3.client('dynamodb')
    table = dynamodb.Table(table_name)
    
    try :
        response = table.scan()
        items = response['Items']
    except Exception as inst:
        resp = {
            'statusCode': 404,
            'body': f'{inst}'
        }
        return resp
    
    features = []
    for item in items:
        features.append(item['feature'])
        
    obj={'type': 'FeatureCollection', 'features': features}

    resp= {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": "*"
        },
        'body': json.dumps(obj)
        }
    return resp
