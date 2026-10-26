
SELECT
    s.tissue_source_site,
    p.stage,
    COUNT(DISTINCT p.patient_id) AS n_patients
FROM patients p
LEFT JOIN samples s
    ON s.patient_id = p.patient_id
GROUP BY s.tissue_source_site, p.stage
ORDER BY s.tissue_source_site, p.stage;