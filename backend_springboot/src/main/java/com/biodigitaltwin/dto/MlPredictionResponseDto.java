package com.biodigitaltwin.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * Verdict returned by the FastAPI ML service for one simulation.
 *
 * <p>Field names are remapped to the Python snake_case keys
 * ({@code predicted_score}, {@code risk_level}) so this DTO can be bound
 * directly from the {@code SimulationResponse} JSON body.
 */
public class MlPredictionResponseDto {

    @JsonProperty("predicted_score")
    private Double predictedScore;

    @JsonProperty("risk_level")
    private String riskLevel;

    public Double getPredictedScore() {
        return predictedScore;
    }

    public void setPredictedScore(Double predictedScore) {
        this.predictedScore = predictedScore;
    }

    public String getRiskLevel() {
        return riskLevel;
    }

    public void setRiskLevel(String riskLevel) {
        this.riskLevel = riskLevel;
    }
}
