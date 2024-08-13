package com.task02;
 
import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.APIGatewayV2HTTPEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayV2HTTPResponse;
import com.syndicate.deployment.annotations.lambda.LambdaHandler;
import com.syndicate.deployment.model.RetentionSetting;
import com.syndicate.deployment.annotations.lambda.LambdaUrlConfig;
import com.syndicate.deployment.model.lambda.url.AuthType;
import com.syndicate.deployment.model.lambda.url.InvokeMode;
 
 
import java.util.HashMap;
import java.util.Map;
 
@LambdaHandler(lambdaName = "hello_world",
       roleName = "hello_world-role",
       isPublishVersion = false,
       logsExpiration = RetentionSetting.SYNDICATE_ALIASES_SPECIFIED
)
@LambdaUrlConfig(
       authType = AuthType.NONE,
       invokeMode = InvokeMode.BUFFERED
)
public class HelloWorld implements RequestHandler<APIGatewayV2HTTPEvent, APIGatewayV2HTTPResponse> {
 
    @Override
    public APIGatewayV2HTTPResponse handleRequest(APIGatewayV2HTTPEvent event, Context context) {
       // Initialize default response
       APIGatewayV2HTTPResponse response;
 
       try {
          String path = event.getRawPath();
          String method = event.getRequestContext() != null
                ? event.getRequestContext().getHttp() != null
                ? event.getRequestContext().getHttp().getMethod()
                : null
                : null;
 
          if ("/hello".equals(path) && "GET".equalsIgnoreCase(method)) {
             return APIGatewayV2HTTPResponse.builder()
                   .withStatusCode(200)
                   .withBody("{\"statusCode\": 200, \"message\": \"Hello from Lambda\"}")
                   .build();
          } else {
             return APIGatewayV2HTTPResponse.builder()
                   .withStatusCode(400)
                   .withBody("{\"statusCode\": 400, \"message\": \"Bad request syntax or unsupported method. Request path: " + (path != null ? path : "null") + ". HTTP method: " + (method != null ? method : "null") + "\"}")
                   .build();
          }
       } catch (Exception e) {
          // Log exception and return an error response
          context.getLogger().log("Exception: " + e.getMessage());
          response = APIGatewayV2HTTPResponse.builder()
                .withStatusCode(500)
                .withBody("{\"statusCode\": 500, \"message\": \"Internal Server Error\"}")
                .build();
       }
 
       return response;
    }
}