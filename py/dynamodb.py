class DynamoDB:
    def __init__(self, client):
        self._client = client
    
    def create_table(self, table_name,attribute_definitions, key_schema, iops ):
        print("creating table")
        return self._client.create_table(
            TableName=table_name,
            AttributeDefinitions=attribute_definitions,
            KeySchema=key_schema,
            ProvisionedThroughput=iops
        )
    