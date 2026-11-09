package com.biodigitaltwin.entity;

import java.time.LocalDateTime;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.PrePersist;
import jakarta.persistence.Table;

/**
 * One survey simulation: the 21 BRFSS 2015 health indicators plus the ML
 * service verdict. Maps to the {@code health_records} table.
 *
 * <p>All 21 indicators are {@code Double} because the training CSV stores them
 * as floats and the FastAPI model consumes a double array; keeping one numeric
 * type avoids silent conversions between this table and the ML request body.
 */
@Entity
@Table(name = "health_records")
public class HealthRecord {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id")
    private Long userId;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "high_bp")
    private Double highBP;

    @Column(name = "high_chol")
    private Double highChol;

    @Column(name = "chol_check")
    private Double cholCheck;

    private Double bmi;

    private Double smoker;

    private Double stroke;

    @Column(name = "heart_disease_or_attack")
    private Double heartDiseaseorAttack;

    @Column(name = "phys_activity")
    private Double physActivity;

    private Double fruits;

    private Double veggies;

    @Column(name = "hvy_alcohol_consump")
    private Double hvyAlcoholConsump;

    @Column(name = "any_healthcare")
    private Double anyHealthcare;

    @Column(name = "no_doc_bc_cost")
    private Double noDocbcCost;

    @Column(name = "gen_hlth")
    private Double genHlth;

    @Column(name = "ment_hlth")
    private Double mentHlth;

    @Column(name = "phys_hlth")
    private Double physHlth;

    @Column(name = "diff_walk")
    private Double diffWalk;

    private Double sex;

    private Double age;

    private Double education;

    private Double income;

    @Column(name = "predicted_score")
    private Double predictedScore;

    @Column(name = "risk_level", length = 100)
    private String riskLevel;

    /** Sets {@code createdAt} on first persist so history queries never see null. */
    @PrePersist
    void onCreate() {
        if (createdAt == null) {
            createdAt = LocalDateTime.now();
        }
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getUserId() {
        return userId;
    }

    public void setUserId(Long userId) {
        this.userId = userId;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

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
