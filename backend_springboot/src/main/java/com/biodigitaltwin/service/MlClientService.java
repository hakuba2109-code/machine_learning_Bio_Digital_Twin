package com.biodigitaltwin.service;

import java.util.LinkedHashMap;
import java.util.Map;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import com.biodigitaltwin.dto.HealthSimulationRequestDto;
import com.biodigitaltwin.dto.MlPredictionResponseDto;

/**
 * HTTP bridge to the FastAPI ML service ({@code ml_service/main_api.py}).
 *
 * <p>Sends the 21 BRFSS indicators as JSON to
 * {@code POST {ml.service.url}/api/v1/predict-glucose} and binds the Python
 * {@code SimulationResponse} back into {@link MlPredictionResponseDto}.
 *
 * <p>The body is written as an explicit name/value map instead of serialising
 * the DTO, because Pydantic matches fields case-sensitively on the raw BRFSS
 * names ({@code HighBP}, {@code BMI}, ...) while Java bean naming would produce
 * {@code highBP} and {@code bmi}.
 */
@Service
public class MlClientService {

    private static final String PREDICT_PATH = "/api/v1/predict-glucose";

    private final RestTemplate restTemplate;

    private final String predictUrl;

    /**
     * @param restTemplate HTTP client used for the ML call
     * @param mlServiceUrl base URL of the FastAPI service, without the path
     */
    public MlClientService(RestTemplate restTemplate, @Value("${ml.service.url}") String mlServiceUrl) {
        this.restTemplate = restTemplate;
        this.predictUrl = stripTrailingSlash(mlServiceUrl) + PREDICT_PATH;
    }

    /**
     * Ask the Python model to score one health profile.
     *
     * @param request the 21 validated BRFSS indicators
     * @return predicted Diabetes_012 score and its Vietnamese risk label
     * @throws org.springframework.web.client.RestClientException when the ML
     *         service is unreachable or rejects the payload
     */
    public MlPredictionResponseDto predict(HealthSimulationRequestDto request) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<Map<String, Double>> entity = new HttpEntity<>(toFeaturePayload(request), headers);
        return restTemplate.postForObject(predictUrl, entity, MlPredictionResponseDto.class);
    }

    /**
     * Builds the request body keyed by the exact Pydantic field names.
     *
     * @param request the 21 indicators
     * @return insertion-ordered map of BRFSS column name to value
     */
    private Map<String, Double> toFeaturePayload(HealthSimulationRequestDto request) {
        Map<String, Double> payload = new LinkedHashMap<>();
        payload.put("HighBP", request.getHighBP());
        payload.put("HighChol", request.getHighChol());
        payload.put("CholCheck", request.getCholCheck());
        payload.put("BMI", request.getBmi());
        payload.put("Smoker", request.getSmoker());
        payload.put("Stroke", request.getStroke());
        payload.put("HeartDiseaseorAttack", request.getHeartDiseaseorAttack());
        payload.put("PhysActivity", request.getPhysActivity());
        payload.put("Fruits", request.getFruits());
        payload.put("Veggies", request.getVeggies());
        payload.put("HvyAlcoholConsump", request.getHvyAlcoholConsump());
        payload.put("AnyHealthcare", request.getAnyHealthcare());
        payload.put("NoDocbcCost", request.getNoDocbcCost());
        payload.put("GenHlth", request.getGenHlth());
        payload.put("MentHlth", request.getMentHlth());
        payload.put("PhysHlth", request.getPhysHlth());
        payload.put("DiffWalk", request.getDiffWalk());
        payload.put("Sex", request.getSex());
        payload.put("Age", request.getAge());
        payload.put("Education", request.getEducation());
        payload.put("Income", request.getIncome());
        return payload;
    }

    private static String stripTrailingSlash(String url) {
        return url.endsWith("/") ? url.substring(0, url.length() - 1) : url;
    }
}
