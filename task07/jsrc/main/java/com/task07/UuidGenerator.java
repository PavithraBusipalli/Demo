package com.task07;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.ScheduledEvent;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.amazonaws.services.s3.model.PutObjectRequest;
import com.syndicate.deployment.annotations.environment.EnvironmentVariable;
import com.syndicate.deployment.annotations.environment.EnvironmentVariables;
import com.syndicate.deployment.annotations.events.RuleEventSource;
import com.syndicate.deployment.annotations.lambda.LambdaHandler;
import com.syndicate.deployment.annotations.resources.DependsOn;
import com.syndicate.deployment.model.ResourceType;
import com.syndicate.deployment.model.RetentionSetting;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@LambdaHandler(lambdaName = "uuid_generator",
                roleName = "uuid_generator-role",
                isPublishVersion = false,
                logsExpiration = RetentionSetting.SYNDICATE_ALIASES_SPECIFIED
)
@RuleEventSource(
        targetRule = "uuid_trigger"
)
@DependsOn(
        name = "uuid_trigger",
        resourceType = ResourceType.CLOUDWATCH_RULE
)
@EnvironmentVariables(value = {
        @EnvironmentVariable(key = "target_bucket", value = "${target_bucket}"),
        @EnvironmentVariable(key = "region", value = "${region}")
})
public class UuidGenerator implements RequestHandler<ScheduledEvent, Map<String, Object>> {

    private static final String BUCKET_NAME = System.getenv("target_bucket");

    @Override
    public Map<String, Object> handleRequest(ScheduledEvent event, Context context) {
        AmazonS3 s3Client = AmazonS3ClientBuilder.standard()
                .withRegion(System.getenv("region"))
                .build();
        List<String> uuids = new ArrayList<>();
        for (int i = 0; i < 10; i++) {
            uuids.add(UUID.randomUUID().toString());
        }
        String filename = "uuids_" + Instant.now().toString() + ".txt";

        File tempFile = new File(System.getProperty("java.io.tmpdir") + "/" + filename);
        try (FileWriter writer = new FileWriter(tempFile)) {
            writer.write(String.join("\n", uuids));
            context.getLogger().log("File written successfully: " + tempFile.getAbsolutePath());
        } catch (IOException e) {
            context.getLogger().log("Error writing to temporary file: " + e.getMessage());
            Map<String, Object> errorResponse = createErrorResponse(e.getMessage());
            return errorResponse;
        }

        try {
            s3Client.putObject(new PutObjectRequest(BUCKET_NAME, filename, tempFile));
            context.getLogger().log("Successfully uploaded UUIDs to S3: " + BUCKET_NAME + "/" + filename);
        } catch (Exception e) {
            context.getLogger().log("Error uploading file to S3: " + e.getMessage());
            Map<String, Object> errorResponse = createErrorResponse(e.getMessage());
            return errorResponse;
        } finally {
            tempFile.delete(); // Cleanup the temporary file after upload
        }

        Map<String, Object> successResponse = new HashMap<>();
        successResponse.put("statusCode", 200);
        successResponse.put("body", "UUIDs generated and stored successfully.");
        return successResponse;
    }

    private Map<String, Object> createErrorResponse(String errorMessage) {
        Map<String, Object> errorResponse = new HashMap<>();
        errorResponse.put("statusCode", 500);
        errorResponse.put("body", "Error: " + errorMessage);
        return errorResponse;
    }
}