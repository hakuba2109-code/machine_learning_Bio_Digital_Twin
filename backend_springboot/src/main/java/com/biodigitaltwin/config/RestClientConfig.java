package com.biodigitaltwin.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;

/**
 * HTTP client used by {@link com.biodigitaltwin.service.MlClientService} to
 * reach the FastAPI ML service.
 */
@Configuration
public class RestClientConfig {

    /**
     * @return a default RestTemplate; the ML base URL itself lives in
     *         {@code ml.service.url} so it stays configurable per environment
     */
    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
}
