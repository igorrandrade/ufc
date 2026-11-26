-- =============================================================================
-- Esquema relacional do projeto UFC BI & Analytics (SQLite 3)
-- -----------------------------------------------------------------------------
-- Modelo relacional analítico com duas granularidades:
--
--   dim_fighter (1) ----< fact_round >---- (1) fact_bout
--
--   * fact_bout  : granularidade = 1 linha por LUTA            (chave: bout_id)
--   * fact_round : granularidade = 1 linha por ATLETA x ROUND  (chave composta)
--   * dim_fighter: dimensão de atletas                         (chave: fighter_id)
--
-- Regras de integridade são aplicadas no banco (PK, FK, UNIQUE, CHECK), e não
-- apenas no código Python. Assim, dados inválidos não entram mesmo se o
-- pipeline for alterado no futuro.
-- Executado por src/pipeline.py (função create_database).
-- =============================================================================

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------------
-- Dimensão: atletas
-- ---------------------------------------------------------------------------
CREATE TABLE dim_fighter (
    fighter_id  INTEGER PRIMARY KEY,
    fighter     TEXT    NOT NULL UNIQUE
);

-- ---------------------------------------------------------------------------
-- Fato: luta (uma linha por luta classificada no recorte do projeto)
--   status: C = líder em golpes venceu; D = líder perdeu; E = empate na contagem
--   *_margin: sempre "líder menos adversário" (insumo do modelo preditivo)
-- ---------------------------------------------------------------------------
CREATE TABLE fact_bout (
    bout_id                 TEXT    PRIMARY KEY,
    date                    TEXT    NOT NULL CHECK (date GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'),
    year                    INTEGER NOT NULL CHECK (year BETWEEN 2022 AND 2024),
    event                   TEXT    NOT NULL,
    method                  TEXT    NOT NULL CHECK (method IN ('Unânime', 'Dividida')),
    weightclass             TEXT,
    fighter_a               TEXT    NOT NULL,
    fighter_b               TEXT    NOT NULL,
    winner                  TEXT    NOT NULL,
    status                  TEXT    NOT NULL CHECK (status IN ('C', 'D', 'E')),
    leader                  TEXT,
    other                   TEXT,
    sig_a                   INTEGER NOT NULL CHECK (sig_a >= 0),
    sig_b                   INTEGER NOT NULL CHECK (sig_b >= 0),
    url                     TEXT    NOT NULL,
    sig_margin              INTEGER,
    attempt_margin          INTEGER,
    accuracy_margin         REAL,
    round_margin            INTEGER CHECK (round_margin BETWEEN -3 AND 3),
    td_landed_margin        REAL,
    kd_margin               REAL,
    control_seconds_margin  REAL,
    CHECK (fighter_a <> fighter_b),
    CHECK (winner IN (fighter_a, fighter_b)),
    -- Empate na contagem <=> placares iguais (consistência com o KPI)
    CHECK ((status = 'E') = (sig_a = sig_b))
);

-- ---------------------------------------------------------------------------
-- Fato: estatística por atleta e round
-- ---------------------------------------------------------------------------
CREATE TABLE fact_round (
    bout_id          TEXT    NOT NULL REFERENCES fact_bout (bout_id) ON DELETE CASCADE,
    fighter_id       INTEGER NOT NULL REFERENCES dim_fighter (fighter_id),
    round            INTEGER NOT NULL CHECK (round BETWEEN 1 AND 3),
    sig_landed       INTEGER NOT NULL CHECK (sig_landed >= 0),
    sig_attempted    INTEGER NOT NULL CHECK (sig_attempted >= sig_landed),
    td_landed        REAL    CHECK (td_landed IS NULL OR td_landed >= 0),
    kd               REAL    CHECK (kd IS NULL OR kd >= 0),
    control_seconds  REAL    CHECK (control_seconds IS NULL OR control_seconds BETWEEN 0 AND 300),
    PRIMARY KEY (bout_id, fighter_id, round)
) WITHOUT ROWID;

-- ---------------------------------------------------------------------------
-- Índices de apoio às consultas do painel (filtros por ano/método/status)
-- ---------------------------------------------------------------------------
CREATE INDEX ix_bout_year_method ON fact_bout (year, method);
CREATE INDEX ix_bout_status      ON fact_bout (status);
CREATE INDEX ix_round_fighter    ON fact_round (fighter_id);

-- ---------------------------------------------------------------------------
-- Visões analíticas (camada semântica de BI)
-- ---------------------------------------------------------------------------

-- KPI de concordância por ano e método (NULLIF evita divisão por zero:
-- denominador nulo => KPI "não calculável", nunca 0%).
CREATE VIEW vw_bout_kpis AS
SELECT year,
       method,
       COUNT(*)                                   AS n,
       SUM(status = 'C')                          AS concordances,
       SUM(status = 'D')                          AS divergences,
       SUM(status = 'E')                          AS ties,
       100.0 * SUM(status = 'C')
             / NULLIF(SUM(status IN ('C', 'D')), 0) AS concordance_pct
FROM fact_bout
GROUP BY year, method;

-- Lutas em que o líder em golpes perdeu (insumo da aba "Conferir uma luta").
CREATE VIEW vw_divergences AS
SELECT bout_id, date, event, method, leader, other, winner,
       MAX(sig_a, sig_b) AS leader_sig,
       MIN(sig_a, sig_b) AS other_sig,
       url
FROM fact_bout
WHERE status = 'D';

-- Estatística por round com o nome do atleta (junção já resolvida).
CREATE VIEW vw_round_detail AS
SELECT r.bout_id, b.date, b.event, f.fighter, r.round,
       r.sig_landed, r.sig_attempted, r.td_landed, r.kd, r.control_seconds
FROM fact_round r
JOIN fact_bout   b USING (bout_id)
JOIN dim_fighter f USING (fighter_id);
