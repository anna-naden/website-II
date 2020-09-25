import json
import boto3
import tempfile
import os
import ast

def lambda_handler(event, context):

    fips = event['queryStringParameters']['fips']
    try:
        s3 = boto3.client('s3')
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, 'state_features.json')
            s3.download_file('phoenix-anna-web-content', fips + '.json', path)
            i=2
            with open(path, 'r') as f:
                obj = f.read()
    except Exception as inst:
        resp = {
            'statusCode': 404,
            'headers': {
            "Access-Control-Allow-Origin": "*"
            },
            'body': f'{i} {inst}'
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
