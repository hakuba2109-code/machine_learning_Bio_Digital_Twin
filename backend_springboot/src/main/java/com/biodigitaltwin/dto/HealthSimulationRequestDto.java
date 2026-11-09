package com.biodigitaltwin.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotNull;

/**
 * Body of {@code POST /api/v1/simulation/predict}: the 21 BRFSS 2015
 * indicators of one respondent, plus the optional {@code userId} owner of the
 * stored record.
 *
 * <p>The JSON keys are the raw BRFSS column names ({@code HighBP}, {@code BMI},
 * ...) so the same payload can be forwarded verbatim to the FastAPI
 * {@code SimulationRequest}, whose Pydantic fields are case-sensitive.
 *
 * <p>Ranges mirror {@code SimulationRequest} in {@code ml_service/main_api.py}
 * exactly: an out-of-range profile is rejected with 400 here instead of
 * surfacing as a 422/502 round-trip through the Python service.
 */
public class HealthSimulationRequestDto {

    @NotNull
    @JsonProperty("HighBP")
    @DecimalMin("0.0")
    @DecimalMax("1.0")
    private Double highBP;

    @JsonProperty("HighChol")
    @NotNull
    @DecimalMin("0.0")
    @DecimalMax("1.0")
    private Double highChol;

    @JsonProperty("CholCheck")
    @NotNull
    @DecimalMin("0.0")
    @DecimalMax("1.0")
    private Double cholCheck;

    @JsonProperty("BMI")
    @NotNull
    @DecimalMin(value = "0.0", inclusive = false)
    private Double bmi;

    @JsonProperty("Smoker")
    @NotNull
    @DecimalMin("0.0")
    @DecimalMax("1.0")
    private Double smoker;

    @JsonProperty("Stroke")
    @NotNull
    @DecimalMin("0.0")
    @DecimalMax("1.0")
    private Double stroke;

    @JsonProperty("HeartDiseaseorAttack")
    @NotNull
    @DecimalMin("0.0")
    @DecimalMax("1.0")
    private Double heartDiseaseorAttack;

    @JsonProperty("PhysActivity")
    @NotNull
    @DecimalMin("0.0")
    @DecimalMax("1.0")
    private Double physActivity;

    @JsonProperty("Fruits")
    @NotNull
    @DecimalMin("0.0")
    @DecimalMax("1.0")
    private Double fruits;

    @JsonProperty("Veggies")
    @NotNull
    @DecimalMin("0.0")
    @DecimalMax("1.0")
    private Double veggies;

    @JsonProperty("HvyAlcoholConsump")
    @NotNull
    @DecimalMin("0.0")
    @DecimalMax("1.0")
    private Double hvyAlcoholConsump;

    @JsonProperty("AnyHealthcare")
    @NotNull
    @DecimalMin("0.0")
    @DecimalMax("1.0")
    private Double anyHealthcare;

    @JsonProperty("NoDocbcCost")
    @NotNull
    @DecimalMin("0.0")
    @DecimalMax("1.0")
    private Double noDocbcCost;

    @JsonProperty("GenHlth")
    @NotNull
    @DecimalMin("1.0")
    @DecimalMax("5.0")
    private Double genHlth;

    @JsonProperty("MentHlth")
    @NotNull
    @DecimalMin("0.0")
    @DecimalMax("30.0")
    private Double mentHlth;

    @JsonProperty("PhysHlth")
    @NotNull
    @DecimalMin("0.0")
    @DecimalMax("30.0")
    private Double physHlth;

    @JsonProperty("DiffWalk")
    @NotNull
    @DecimalMin("0.0")
    @DecimalMax("1.0")
    private Double diffWalk;

    @JsonProperty("Sex")
    @NotNull
    @DecimalMin("0.0")
    @DecimalMax("1.0")
    private Double sex;

    @JsonProperty("Age")
    @NotNull
    @DecimalMin("1.0")
    @DecimalMax("13.0")
    private Double age;

    @JsonProperty("Education")
    @NotNull
    @DecimalMin("1.0")
    @DecimalMax("6.0")
    private Double education;

    @JsonProperty("Income")
    @NotNull
    @DecimalMin("1.0")
    @DecimalMax("8.0")
    private Double income;

    private Long userId;

    public Double getHighBP() {
        return highBP;
    }

    public void setHighBP(Double highBP) {
        this.highBP = highBP;
    }

    public Double getHighChol() {
        return highChol;
    }

    public void setHighChol(Double highChol) {
        this.highChol = highChol;
    }

    public Double getCholCheck() {
        return cholCheck;
    }

    public void setCholCheck(Double cholCheck) {
        this.cholCheck = cholCheck;
    }

    public Double getBmi() {
        return bmi;
    }

    public void setBmi(Double bmi) {
        this.bmi = bmi;
    }

    public Double getSmoker() {
        return smoker;
    }

    public void setSmoker(Double smoker) {
        this.smoker = smoker;
    }

    public Double getStroke() {
        return stroke;
    }

    public void setStroke(Double stroke) {
        this.stroke = stroke;
    }

    public Double getHeartDiseaseorAttack() {
        return heartDiseaseorAttack;
    }

    public void setHeartDiseaseorAttack(Double heartDiseaseorAttack) {
        this.heartDiseaseorAttack = heartDiseaseorAttack;
    }

    public Double getPhysActivity() {
        return physActivity;
    }

    public void setPhysActivity(Double physActivity) {
        this.physActivity = physActivity;
    }

    public Double getFruits() {
        return fruits;
    }

    public void setFruits(Double fruits) {
        this.fruits = fruits;
    }

    public Double getVeggies() {
        return veggies;
    }

    public void setVeggies(Double veggies) {
        this.veggies = veggies;
    }

    public Double getHvyAlcoholConsump() {
        return hvyAlcoholConsump;
    }

    public void setHvyAlcoholConsump(Double hvyAlcoholConsump) {
        this.hvyAlcoholConsump = hvyAlcoholConsump;
    }

    public Double getAnyHealthcare() {
        return anyHealthcare;
    }

    public void setAnyHealthcare(Double anyHealthcare) {
        this.anyHealthcare = anyHealthcare;
    }

    public Double getNoDocbcCost() {
        return noDocbcCost;
    }

    public void setNoDocbcCost(Double noDocbcCost) {
        this.noDocbcCost = noDocbcCost;
    }

    public Double getGenHlth() {
        return genHlth;
    }

    public void setGenHlth(Double genHlth) {
        this.genHlth = genHlth;
    }

    public Double getMentHlth() {
        return mentHlth;
    }

    public void setMentHlth(Double mentHlth) {
        this.mentHlth = mentHlth;
    }

    public Double getPhysHlth() {
        return physHlth;
    }

    public void setPhysHlth(Double physHlth) {
        this.physHlth = physHlth;
    }

    public Double getDiffWalk() {
        return diffWalk;
    }

    public void setDiffWalk(Double diffWalk) {
        this.diffWalk = diffWalk;
    }

    public Double getSex() {
        return sex;
    }

    public void setSex(Double sex) {
        this.sex = sex;
    }

    public Double getAge() {
        return age;
    }

    public void setAge(Double age) {
        this.age = age;
    }

    public Double getEducation() {
        return education;
    }

    public void setEducation(Double education) {
        this.education = education;
    }

    public Double getIncome() {
        return income;
    }

    public void setIncome(Double income) {
        this.income = income;
    }

    public Long getUserId() {
        return userId;
    }

    public void setUserId(Long userId) {
        this.userId = userId;
    }
}
