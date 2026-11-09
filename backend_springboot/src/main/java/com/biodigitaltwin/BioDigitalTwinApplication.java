package com.biodigitaltwin;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Entry point of the Bio-Digital Twin backend.
 *
 * <p>Serves {@code POST /api/v1/simulation/predict} on port 3000: validate the
 * 21 BRFSS indicators, ask the FastAPI SVR service on port 8000 for a score,
 * then archive profile and verdict together in {@code health_records}.
 */
@SpringBootApplication
public class BioDigitalTwinApplication {

    public static void main(String[] args) {
        SpringApplication.run(BioDigitalTwinApplication.class, args);
    }
}