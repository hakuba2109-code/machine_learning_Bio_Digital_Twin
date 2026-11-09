package com.biodigitaltwin.controller;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestClientException;

import com.biodigitaltwin.dto.ApiResponse;
import com.biodigitaltwin.dto.HealthSimulationRequestDto;
import com.biodigitaltwin.entity.HealthRecord;
import com.biodigitaltwin.service.HealthSimulationService;

import jakarta.validation.Valid;

/**
 * Public entry point of the simulation feature: JSON in, ML verdict plus
 * persisted record out.
 *
 * <p>Returns the {@link HealthRecord} entity directly, as required by the
 * feature spec. That breaks the "controllers never return an entity" rule in
 * QODER.md: the response exposes the database row (id and timestamp included).
 * Swap in a response DTO if the public contract hardens.
 *
 * <p>{@code @CrossOrigin(origins = "*")} is a dev-time allowance for the React
 * client; the React rule in QODER.md prefers a Vite proxy over open CORS.
 */
@RestController
@CrossOrigin(origins = "*")
@RequestMapping("/api/v1/simulation")
public class HealthSimulationController {

    private static final Logger log = LoggerFactory.getLogger(HealthSimulationController.class);

    private final HealthSimulationService healthSimulationService;

    public HealthSimulationController(HealthSimulationService healthSimulationService) {
        this.healthSimulationService = healthSimulationService;
    }

    /**
     * Score 21 health indicators with the Python model and store the result.
     *
     * @param request the 21 BRFSS indicators, validated by bean validation
     * @return 200 with the saved record inside the standard envelope
     */
    @PostMapping("/predict")
    public ApiResponse<HealthRecord> predict(@Valid @RequestBody HealthSimulationRequestDto request) {
        HealthRecord saved = healthSimulationService.simulate(request);
        return ApiResponse.success(saved, "Đã lưu kết quả dự đoán: " + saved.getRiskLevel());
    }

    /**
     * Translate ML service failures into a 502 instead of a raw 500.
     *
     * @param ex connection error or non-2xx answer from FastAPI
     * @return 502 envelope telling the client the Python service is unavailable
     */
    @ExceptionHandler(RestClientException.class)
    public ResponseEntity<ApiResponse<HealthRecord>> onMlServiceFailure(RestClientException ex) {
        log.error("Không gọi được ML service", ex);
        return ResponseEntity.status(HttpStatus.BAD_GATEWAY)
                .body(ApiResponse.error(HttpStatus.BAD_GATEWAY.value(),
                        "Không kết nối được với ML service"));
    }
}
