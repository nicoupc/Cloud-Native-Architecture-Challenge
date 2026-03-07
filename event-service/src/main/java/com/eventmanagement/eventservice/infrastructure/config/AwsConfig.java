package com.eventmanagement.eventservice.infrastructure.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.eventbridge.EventBridgeClient;

import java.net.URI;

/**
 * AwsConfig - Configuración de clientes AWS SDK.
 * 
 * ¿Qué hace esta clase?
 * - Crea el cliente de EventBridge
 * - Configura el endpoint para LocalStack
 * - Configura credenciales dummy para LocalStack
 * 
 * LocalStack vs AWS Real:
 * - LocalStack: endpoint = http://localhost:4566
 * - AWS Real: endpoint = null (usa el endpoint por defecto)
 * 
 * Analogía:
 * - Es como configurar tu teléfono:
 *   - LocalStack = Llamar a un número local
 *   - AWS Real = Llamar a un número internacional
 */
@Configuration
public class AwsConfig {
    
    @Value("${aws.endpoint-url:}")
    private String endpointUrl;
    
    @Value("${aws.region}")
    private String region;
    
    @Value("${aws.access-key-id}")
    private String accessKeyId;
    
    @Value("${aws.secret-access-key}")
    private String secretAccessKey;
    
    /**
     * Crea el cliente de EventBridge.
     * 
     * Si endpointUrl está configurado (LocalStack):
     * - Usa http://localhost:4566
     * - Usa credenciales dummy
     * 
     * Si endpointUrl está vacío (AWS Real):
     * - Usa el endpoint por defecto de AWS
     * - Usa credenciales del perfil de AWS CLI
     */
    @Bean
    public EventBridgeClient eventBridgeClient() {
        var builder = EventBridgeClient.builder()
            .region(Region.of(region));
        
        // Configuración para LocalStack
        if (endpointUrl != null && !endpointUrl.isEmpty()) {
            builder.endpointOverride(URI.create(endpointUrl))
                .credentialsProvider(
                    StaticCredentialsProvider.create(
                        AwsBasicCredentials.create(accessKeyId, secretAccessKey)
                    )
                );
        }
        
        return builder.build();
    }
}
