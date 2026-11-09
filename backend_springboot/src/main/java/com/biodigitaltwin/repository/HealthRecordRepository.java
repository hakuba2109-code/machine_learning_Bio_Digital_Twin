package com.biodigitaltwin.repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.biodigitaltwin.entity.HealthRecord;

/** Data access for {@link HealthRecord} survey simulations. */
@Repository
public interface HealthRecordRepository extends JpaRepository<HealthRecord, Long> {

    /**
     * Loads one user's simulation history, newest first.
     *
     * @param userId owner of the records
     * @return matching records ordered by {@code createdAt} descending; empty
     *         list when the user has no simulation yet
     */
    List<HealthRecord> findByUserIdOrderByCreatedAtDesc(Long userId);
}
