package com.biodigitaltwin.service;

import org.springframework.stereotype.Service;

import com.biodigitaltwin.dto.HealthSimulationRequestDto;
import com.biodigitaltwin.dto.MlPredictionResponseDto;
import com.biodigitaltwin.entity.HealthRecord;
import com.biodigitaltwin.repository.HealthRecordRepository;

/**
 * Use case behind {@code POST /api/v1/simulation/predict}: ask the Python
 * model for a verdict, then persist the profile and that verdict together.
 *
 * <p>The ML call runs first on purpose. Storing the row only after the score
 * is known keeps {@code predicted_score} and {@code risk_level} non-null, so
 * history read through
 * {@link HealthRecordRepository#findByUserIdOrderByCreatedAtDesc(Long)} never
 * returns a record without its result.
 */
@Service
public class HealthSimulationService {

    private final MlClientService mlClientService;

    private final HealthRecordRepository healthRecordRepository;

    public HealthSimulationService(MlClientService mlClientService,
            HealthRecordRepository healthRecordRepository) {
        this.mlClientService = mlClientService;
        this.healthRecordRepository = healthRecordRepository;
    }

    /**
     * Predict the diabetes-risk score for one profile and archive it.
     *
     * @param request the 21 validated BRFSS indicators, plus optional userId
     * @return the persisted record, including its generated id and timestamp
     */
    public HealthRecord simulate(HealthSimulationRequestDto request) {
        MlPredictionResponseDto prediction = mlClientService.predict(request);
        return healthRecordRepository.save(toRecord(request, prediction));
    }

    private HealthRecord toRecord(HealthSimulationRequestDto request, MlPredictionResponseDto prediction) {
        HealthRecord record = new HealthRecord();
        record.setUserId(request.getUserId());
        record.setHighBP(request.getHighBP());
        record.setHighChol(request.getHighChol());
        record.setCholCheck(request.getCholCheck());
        record.setBmi(request.getBmi());
        record.setSmoker(request.getSmoker());
        record.setStroke(request.getStroke());
        record.setHeartDiseaseorAttack(request.getHeartDiseaseorAttack());
        record.setPhysActivity(request.getPhysActivity());
        record.setFruits(request.getFruits());
        record.setVeggies(request.getVeggies());
        record.setHvyAlcoholConsump(request.getHvyAlcoholConsump());
        record.setAnyHealthcare(request.getAnyHealthcare());
        record.setNoDocbcCost(request.getNoDocbcCost());
        record.setGenHlth(request.getGenHlth());
        record.setMentHlth(request.getMentHlth());
        record.setPhysHlth(request.getPhysHlth());
        record.setDiffWalk(request.getDiffWalk());
        record.setSex(request.getSex());
        record.setAge(request.getAge());
        record.setEducation(request.getEducation());
        record.setIncome(request.getIncome());
        record.setPredictedScore(prediction.getPredictedScore());
        record.setRiskLevel(prediction.getRiskLevel());
        return record;
    }
}
