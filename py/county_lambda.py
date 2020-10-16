import json
import boto3
import tempfile
import os
import ast

def lambda_handler(event, context):

    params = event['queryStringParameters']
    
    #-----------------------------------
    # World
    #-----------------------------------
    if 'iso-a3' in params:
        ISO_A3 = params['iso-a3']
        try:
            s3 = boto3.client('s3')
            with tempfile.TemporaryDirectory() as tmpdir:
                path = os.path.join(tmpdir, 'world_features.json')
                s3.download_file('phoenix-technical-services.com', ISO_A3 + '.json', path)
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
        
    if 'fips' in params:
        fips = params['fips']
        
        #-------------------------------------
        # County map
        #-------------------------------------
        if len(fips) == 2:
            try:
                s3 = boto3.client('s3')
                with tempfile.TemporaryDirectory() as tmpdir:
                    path = os.path.join(tmpdir, 'scratch.json')
                    s3.download_file('phoenix-technical-services.com', fips + '.json', path)
                    with open(path, 'r') as f:
                        obj = f.read()
                    os.remove(path)
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

    #--------------------------------------------
    # County time series vs US
    #-------------------------------------------
        if len(fips) == 5:
            try:
                s3 = boto3.client('s3')
                with tempfile.TemporaryDirectory() as tmpdir:
                    path = os.path.join(tmpdir, 'scratch.json')
                    s3.download_file('phoenix-technical-services.com', 'all_counties.json', path)
                    with open(path, 'r') as f:
                        all_counties = json.load(f)
                os.remove(path)
                county_ts = all_counties[fips]

            except Exception as inst:
                resp = {
                    'statusCode': 404,
                    'headers': {
                    "Access-Control-Allow-Origin": "*"
                    },
                    'body': f'{inst}'
                }
                return resp
    
            try:
                s3 = boto3.client('s3')
                with tempfile.TemporaryDirectory() as tmpdir:
                    path = os.path.join(tmpdir, 'scratch.json')
                    s3.download_file('phoenix-technical-services.com', 'us-time-series.json', path)
                    with open(path, 'r') as f:
                        us_ts = f.read()
                    os.remove(path)
            except Exception as inst:
                resp = {
                    'statusCode': 404,
                    'headers': {
                    "Access-Control-Allow-Origin": "*"
                    },
                    'body': f'{inst}'
                }
                return resp
            us_county = '{ "us": ' + us_ts + ', "county": ' + county_ts + '}'
            resp= {
                'statusCode': 200,
                'headers': {
                    "Access-Control-Allow-Origin": "*"
                },
                'body': us_county
                }
            return resp

            try:
                s3 = boto3.client('s3')
                with tempfile.TemporaryDirectory() as tmpdir:
                    path = os.path.join(tmpdir, 'scratch.json')
                    s3.download_file('phoenix-technical-services.com', fips + '.json', path)
                    with open(path, 'r') as f:
                        obj = f.read()
                    os.remove(path)
            except Exception as inst:
                resp = {
                    'statusCode': 404,
                    'headers': {
                    "Access-Control-Allow-Origin": "*"
                    },
                    'body': f'{inst}'
                }
                return resp
    
            try:
                s3 = boto3.client('s3')
                with tempfile.TemporaryDirectory() as tmpdir:
                    path = os.path.join(tmpdir, 'scratch.json')
                    s3.download_file('phoenix-technical-services.com', fips + '.json', path)
                    with open(path, 'r') as f:
                        us_ts = f.read()
                    os.remove(path)
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
import json
import boto3
import tempfile
import os
import ast

def lambda_handler(event, context):

    params = event['queryStringParameters']
    
    #-----------------------------------
    # World map geojson
    #-----------------------------------
    if 'all' in params:
        try:
            s3 = boto3.client('s3')
            with tempfile.TemporaryDirectory() as tmpdir:
                path = os.path.join(tmpdir, 'world_features.json')
                s3.download_file('phoenix-technical-services.com', 'all.json', path)
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
        
    #-----------------------------------
    # National time series
    #-----------------------------------
    if 'iso-a3' in params:
        ISO_A3 = params['iso-a3']
        try:
            s3 = boto3.client('s3')
            with tempfile.TemporaryDirectory() as tmpdir:
                path = os.path.join(tmpdir, 'world_features.json')
                s3.download_file('phoenix-technical-services.com', ISO_A3 + '.json', path)
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
        
    if 'fips' in params:
        fips = params['fips']
        
        #-------------------------------------
        # County map
        #-------------------------------------
        if len(fips) == 2:
            try:
                s3 = boto3.client('s3')
                with tempfile.TemporaryDirectory() as tmpdir:
                    path = os.path.join(tmpdir, 'scratch.json')
                    s3.download_file('phoenix-technical-services.com', fips + '.json', path)
                    with open(path, 'r') as f:
                        obj = f.read()
                    os.remove(path)
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

    #--------------------------------------------
    # County time series vs US
    #-------------------------------------------
        if len(fips) == 5:
            try:
                s3 = boto3.client('s3')
                with tempfile.TemporaryDirectory() as tmpdir:
                    path = os.path.join(tmpdir, 'scratch.json')
                    s3.download_file('phoenix-technical-services.com', 'all_counties.json', path)
                    county_ts=""
                    with open(path, 'r') as f:
                        all_counties = json.load(f)
                county_ts = all_counties[fips]
                county_ts_json = json.dumps(county_ts)

            except Exception as inst:
                resp = {
                    'statusCode': 404,
                    'headers': {
                    "Access-Control-Allow-Origin": "*"
                    },
                    'body': f'{inst}'
                }
                return resp
    
            try:
                s3 = boto3.client('s3')
                with tempfile.TemporaryDirectory() as tmpdir:
                    path = os.path.join(tmpdir, 'scratch.json')
                    s3.download_file('phoenix-technical-services.com', 'USA.json', path)
                    with open(path, 'r') as f:
                        us_ts = f.read()
                    os.remove(path)
            except Exception as inst:
                resp = {
                    'statusCode': 404,
                    'headers': {
                    "Access-Control-Allow-Origin": "*"
                    },
                    'body': f'{inst}'
                }
                return resp
            us_county = '{ "us": ' + us_ts + ', "county": ' + county_ts_json + '}'
            resp= {
                'statusCode': 200,
                'headers': {
                    "Access-Control-Allow-Origin": "*"
                },
                'body': us_county
                }
            return resp

            try:
                s3 = boto3.client('s3')
                with tempfile.TemporaryDirectory() as tmpdir:
                    path = os.path.join(tmpdir, 'scratch.json')
                    s3.download_file('phoenix-technical-services.com', fips + '.json', path)
                    with open(path, 'r') as f:
                        obj = f.read()
                    os.remove(path)
            except Exception as inst:
                resp = {
                    'statusCode': 404,
                    'headers': {
                    "Access-Control-Allow-Origin": "*"
                    },
                    'body': f'{inst}'
                }
                return resp
    
            try:
                s3 = boto3.client('s3')
                with tempfile.TemporaryDirectory() as tmpdir:
                    path = os.path.join(tmpdir, 'scratch.json')
                    s3.download_file('phoenix-technical-services.com', fips + '.json', path)
                    with open(path, 'r') as f:
                        us_ts = f.read()
                    os.remove(path)
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
