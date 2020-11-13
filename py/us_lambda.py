import json
import boto3
import tempfile
import os

def lambda_handler(event, context):
    try:
        s3 = boto3.client('s3')
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, 'scratch.json')
            s3.download_file('phoenix-technical-services.com', 'all-states.json', path)
            with open(path, 'r') as f:
                obj = f.read()
    except Exception as inst:
        resp = {
            'statusCode': 404,
            'headers': {
            "Access-Control-Allow-Origin": "*"
            },
            'body': f'{inst}'
        }
        return resp

    resp= {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": "*"
        },
        'body': obj
        }
    # os.remove(path)
    return resp
    
    # table_name = 'state-features'
    # dynamodb=boto3.resource('dynamodb')
    # client = boto3.client('dynamodb')
    # table = dynamodb.Table(table_name)
    
    # try :
    #     response = table.scan()
    #     items = response['Items']
    # except Exception as inst:
    #     resp = {
    #         'statusCode': 404,
    #         'body': f'{inst}'
    #     }
    #     return resp
    
    # features = []
    # for item in items:
    #     features.append(item['feature'])
        
    # obj={'type': 'FeatureCollection', 'features': features}

    # resp= {
    #     'statusCode': 200,
    #     'headers': {
    #         "Access-Control-Allow-Origin": "*"
    #     },
    #     'body': json.dumps(obj)
    #     }
    # return resp
