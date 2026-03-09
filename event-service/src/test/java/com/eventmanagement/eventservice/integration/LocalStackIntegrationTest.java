package com.eventmanagement.eventservice.integration;

import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.condition.EnabledIf;

import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.eventbridge.EventBridgeClient;
import software.amazon.awssdk.services.eventbridge.model.*;

import java.net.HttpURLConnection;
import java.net.URI;
import java.net.URL;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Integration tests that require LocalStack to be running.
 * Automatically skipped if LocalStack is not available.
 */
@EnabledIf("isLocalStackAvailable")
class LocalStackIntegrationTest {

    private static final String LOCALSTACK_ENDPOINT = "http://localhost:4566";
    private static final String TEST_BUS_NAME = "event-service-integration-test-bus";

    private static EventBridgeClient eventBridgeClient;

    static boolean isLocalStackAvailable() {
        try {
            URL url = new URL(LOCALSTACK_ENDPOINT + "/_localstack/health");
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setConnectTimeout(2000);
            conn.setReadTimeout(2000);
            conn.setRequestMethod("GET");
            int responseCode = conn.getResponseCode();
            conn.disconnect();
            return responseCode == 200;
        } catch (Exception e) {
            return false;
        }
    }

    @BeforeAll
    static void setUp() {
        AwsBasicCredentials credentials = AwsBasicCredentials.create("test", "test");

        eventBridgeClient = EventBridgeClient.builder()
                .endpointOverride(URI.create(LOCALSTACK_ENDPOINT))
                .region(Region.US_EAST_1)
                .credentialsProvider(StaticCredentialsProvider.create(credentials))
                .build();

        // Create test event bus (ignore if already exists)
        try {
            eventBridgeClient.createEventBus(
                    CreateEventBusRequest.builder()
                            .name(TEST_BUS_NAME)
                            .build()
            );
        } catch (ResourceAlreadyExistsException e) {
            // Bus already exists, that's fine
        }
    }

    @Test
    void shouldConnectToLocalStack() {
        assertTrue(isLocalStackAvailable(), "LocalStack should be running");
    }

    @Test
    void shouldCreateAndDescribeEventBridgeBus() {
        DescribeEventBusResponse response = eventBridgeClient.describeEventBus(
                DescribeEventBusRequest.builder()
                        .name(TEST_BUS_NAME)
                        .build()
        );

        assertNotNull(response.name());
        assertEquals(TEST_BUS_NAME, response.name());
        assertNotNull(response.arn());
    }

    @Test
    void shouldPublishEventToEventBridge() {
        PutEventsResponse response = eventBridgeClient.putEvents(
                PutEventsRequest.builder()
                        .entries(
                                PutEventsRequestEntry.builder()
                                        .eventBusName(TEST_BUS_NAME)
                                        .source("event-service")
                                        .detailType("EventPublished")
                                        .detail("{\"eventId\":\"evt-int-001\",\"name\":\"Integration Test Event\"}")
                                        .build()
                        )
                        .build()
        );

        assertEquals(0, response.failedEntryCount(),
                "Event should be published without failures");
        assertNotNull(response.entries());
        assertFalse(response.entries().isEmpty());
    }
}
