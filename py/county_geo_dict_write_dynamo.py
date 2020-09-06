import boto3
import time
import json
from decimal import Decimal

def stringify(num):
    return f'{num}'

if __name__ == '__main__':
    table_name = 'county-geo-dict'
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
                    'AttributeName': 'type',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'type',
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
    with open('/home/anna_user2/projects/website/py/test.json', 'rt') as f:
        covid = f.read()

    #string to object
    table = dynamodb.Table(table_name)
    x=json.loads(covid, parse_float=stringify)
    covid=x
    
    try :
        with table.batch_writer() as batch:
            batch.put_item(
                Item=covid
                )
    except Exception as inst:
        print(inst)
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