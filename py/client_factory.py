import boto3

class ClientFactory:
    def __init__(self, client):
        self.client = boto3.client(client, region_name='us-east-1')
    
    def get_client(self):
        return self.client
    
class DynamoDBClient(ClientFactory):
    def __init__(self):
        super().__init__('dynamodb')
