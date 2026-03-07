package com.eventmanagement.eventservice;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Clase principal de Spring Boot.
 * 
 * @SpringBootApplication es como el "interruptor maestro" que:
 * 1. Escanea todas las clases del proyecto
 * 2. Conecta automáticamente las dependencias
 * 3. Inicia el servidor web en el puerto 8080
 */
@SpringBootApplication
public class EventServiceApplication {

    public static void main(String[] args) {
        // Esto enciende Spring Boot
        SpringApplication.run(EventServiceApplication.class, args);
    }
}
