import boto3
import time
import json
from decimal import Decimal

def stringify(num):
    return f'{num}'

if __name__ == '__main__':
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
    
    #Put
    with open('/home/anna_user2/projects/website-II/json/states-geometry.json', 'rt') as f:
        covid = f.read()

    #string to object
    covid=json.loads(covid, parse_float=stringify, parse_int=stringify)
    for feature in covid['features']:
        id = feature['id']
        if id == '33':
            print('here')
    
        try :
            with table.batch_writer() as batch:
                batch.put_item(
                    Item={'id': id,
                        'feature': feature}
                    )
        except Exception as inst:
            print(inst)
            break
    # except AmazonServiceException as ase:
    #     print("Could not complete operation")
    #     print("Error Message:  " + ase.getMessage())
    #     print("HTTP Status:    " + ase.getStatusCode())
    #     print("AWS Error Code: " + ase.getErrorCode())
    #     print("Error Type:     " + ase.getErrorType())
    #     print("Request ID:     " + ase.getRequestId())

    # except AmazonClientException as ace:
    #     print("Internal error occurred communicating with DynamoDB")
    #     print("Error Message:  " + ace.getMessage())