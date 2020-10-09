import json
import boto3
import tempfile
import os
import ast

def lambda_handler(event, context):

    params = event['queryStringParameters']
    fips = params['fips']
    try:
        s3 = boto3.client('s3')
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, 'state_features.json')
            s3.download_file('phoenix-technical-services.com', fips + '.json', path)
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
    return resp
