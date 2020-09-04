from client_factory import DynamoDBClient
from dynamodb import DynamoDB

def create_dynamodb_table():
    dynamodb_client = DynamoDBClient().get_client()
    dynamodb=DynamoDB(dynamodb_client)

    table_name="States"

    #define attributes
    attribute_definitions = [
        {
            "AttributeName": 'fips',
            "AttributeType": 'S'
        },
        {
            "AttributeName": 'name',
            'AttributeType': 'S'

        }
    ]

    # key schema definitions
    key_schema = [
        {
            'AttributeName': 'fips',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'name',
            'KeyType': 'RANGE'
        }
    ]
    initial_iops = {
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }

    dynamodb_create_table_response = dynamodb.create_table(table_name, attribute_definitions, key_schema, initial_iops)
    print(('created table'))

if __name__ == '__main__':
    create_dynamodb_table()