import boto3
import json
import sys

def stringify(num):
    return f'{num}'

def push_states_features(covid, json_str=None):
    table_name = 'state-features'
    dynamodb=boto3.resource('dynamodb')
    client = boto3.client('dynamodb')
    table = dynamodb.Table(table_name)

    if False:
        # Delete if exits
        tables = client.list_tables()['TableNames']
        if table_name in tables:
            table.delete()
        print('waiting for not')
        client.get_waiter('table_not_exists').wait(TableName=table_name)
        print('not')

    if False:
        # Create
        table = dynamodb.create_table(
            TableName = table_name,
            KeySchema = [
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )

        print('waiting')

        table.meta.client.get_waiter('table_exists')
    
    # with open('/home/anna_user2/projects/website-II/json/state-month-deaths.json', 'rt') as f:
    #     covid = f.read()
    # covid=json.loads(covid, parse_float=stringify, parse_int=stringify)
    #covid = json.loads(json_str, parse_float=stringify, parse_int=stringify)
    #covid = json.loads(json_str)
    for feature in covid['features']:
        id = feature['id']
        print(id)
        try :
            with table.batch_writer() as batch:
                batch.put_item(
                    Item={'id': id,
                        'feature': feature}
                    )
        except Exception as inst:
            print(inst)
            break