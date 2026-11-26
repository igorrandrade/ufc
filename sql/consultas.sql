-- =============================================================================
-- Consultas analíticas de referência (SQLite). Cada uma reproduz um KPI do
-- relatório e é conferida por tests/test_project.py contra o cálculo em Python.
-- Uso:  sqlite3 data/processed/ufc.sqlite < sql/consultas.sql
-- =============================================================================

-- Q1. KPI global: concordância, divergência e cobertura classificável.
SELECT SUM(status = 'C')                                   AS c,
       SUM(status = 'D')                                   AS d,
       SUM(status = 'E')                                   AS e,
       ROUND(100.0 * SUM(status = 'C') / SUM(status IN ('C','D')), 2) AS concordancia_pct,
       ROUND(100.0 * SUM(status = 'D') / SUM(status IN ('C','D')), 2) AS divergencia_pct,
       ROUND(100.0 * SUM(status IN ('C','D')) / COUNT(*), 2)          AS cobertura_pct
FROM fact_bout;

-- Q2. H2: concordância por tipo de decisão (unânime x dividida).
SELECT method,
       SUM(status = 'C') AS c,
       SUM(status = 'D') AS d,
       ROUND(100.0 * SUM(status = 'C') / SUM(status IN ('C','D')), 2) AS concordancia_pct
FROM fact_bout
GROUP BY method;

-- Q3. Estabilidade temporal: concordância por ano e método (view pronta).
SELECT * FROM vw_bout_kpis ORDER BY year, method;

-- Q4. Maiores divergências: líder com maior vantagem em golpes que perdeu.
SELECT date, event, leader, other, winner, leader_sig, other_sig,
       leader_sig - other_sig AS vantagem
FROM vw_divergences
ORDER BY vantagem DESC
LIMIT 10;

-- Q5. Caso ilustrativo (Holland x Della Maddalena): golpes por round.
SELECT fighter, round, sig_landed
FROM vw_round_detail
WHERE bout_id = '697efaf0d162e877'
ORDER BY round, fighter;

-- Q6. Atletas com mais lutas no recorte (ranking com função de janela).
SELECT fighter, lutas,
       RANK() OVER (ORDER BY lutas DESC) AS posicao
FROM (SELECT f.fighter, COUNT(DISTINCT r.bout_id) AS lutas
      FROM fact_round r JOIN dim_fighter f USING (fighter_id)
      GROUP BY f.fighter)
ORDER BY posicao, fighter
LIMIT 10;

-- Q7. Auditoria de integridade (deve retornar zero linhas em cada bloco).
SELECT 'luta sem 6 linhas de round' AS problema, bout_id
FROM fact_round GROUP BY bout_id HAVING COUNT(*) <> 6;
