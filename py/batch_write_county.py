import boto3
import json

dyamodb = boto3.resource('dynamodb')

table_name = 'counties_with_deaths'

table = dyamodb.Table(table_name)

with open('../json/temp_county.json', 'r') as f:
    features=json.load(f)

num_features = len(features)
i=0
while(i<num_features):
    print(i)
    features1 = features[i:i+25]
    i += 25
    with table.batch_writer() as batch:
        for feature in features1:
            fips = feature['id']
            print(f'fips: {fips}')
            item = {
                'state_fips': fips[:2],
                'county_fips': fips[2:],
                'feature': feature
            }
            batch.put_item(Item=item)