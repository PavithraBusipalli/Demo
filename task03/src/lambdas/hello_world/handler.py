from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda

_LOG = get_logger('HelloWorld-handler')

class HelloWorld(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass
        
    def handle_request(self, event, context):
        """
        Handle the incoming event and return the correct response.
        """
        # You might want to log the event or perform other operations here.
        
        # Return the expected response
        response = {
            "statusCode": 200,
            "message": "Hello from Lambda"
        }
    
        return response
    

HANDLER = HelloWorld()

def lambda_handler(event, context):
    # Ensure that lambda_handler calls handle_request and returns the result.
    return HANDLER.handle_request(event, context)
