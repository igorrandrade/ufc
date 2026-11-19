# Dicionário de dados

## Fontes brutas

- `ufc_event_details.csv`: EVENT, URL do evento, DATE e LOCATION. Uma linha de catálogo de evento.
- `ufc_fight_results.csv`: EVENT, BOUT, OUTCOME, WEIGHTCLASS, METHOD, ROUND, TIME, TIME FORMAT, REFEREE, DETAILS e URL da luta. Pode conter aliases/duplicatas.
- `ufc_fight_stats.csv`: EVENT, BOUT, ROUND, FIGHTER, KD, SIG.STR., SIG.STR. %, TOTAL STR., TD, TD %, SUB.ATT, REV., CTRL, HEAD, BODY, LEG, DISTANCE, CLINCH e GROUND. Uma linha por atleta e round, sujeita a duplicatas.

## `bouts.csv` e `fact_bout` — uma linha por luta

| Campo | Tipo | Definição |
|---|---|---|
| bout_id | texto | Identificador final da URL oficial, chave única |
| date / year | data ISO / inteiro | Data e ano do evento |
| event / weightclass | texto | Nome do evento e categoria |
| method | categoria | Unânime ou Dividida |
| fighter_a / fighter_b | texto | Atletas na ordem do BOUT original |
| winner | texto | Vencedor conforme OUTCOME e ordem do BOUT |
| status | categoria | C concordância; D divergência; E empate na contagem |
| leader / other | texto anulável | Líder único e adversário; vazios em empates |
| sig_a / sig_b | inteiro | Acertos significativos nos três rounds |
| url | URL | Ficha oficial para conferência |
| sig_margin | inteiro | Diferença de acertos, líder menos adversário |
| attempt_margin | inteiro | Diferença de tentativas |
| accuracy_margin | decimal | Diferença das precisões, em proporção, não em porcentagem |
| round_margin | inteiro de -3 a 3 | Rounds liderados em golpes pelo líder menos rounds liderados pelo adversário |
| td_landed_margin | inteiro | Diferença de quedas conectadas |
| kd_margin | inteiro | Diferença de knockdowns |
| control_seconds_margin | inteiro | Diferença de tempo de controle, em segundos |

As diferenças em linhas E não têm orientação de líder único e não são usadas pelo modelo.

## `rounds.csv` — uma linha por atleta, luta e round

| Campo | Tipo | Definição |
|---|---|---|
| bout_id | texto | Referência à luta |
| fighter | texto | Atleta |
| round | inteiro | 1, 2 ou 3 |
| sig_landed / sig_attempted | inteiro | Acertos / tentativas extraídos de SIG.STR. |
| td_landed | inteiro anulável | Quedas conectadas |
| kd | inteiro anulável | Knockdowns |
| control_seconds | inteiro anulável | Controle no round, de 0 a 300 segundos |

No SQLite, `dim_fighter` relaciona fighter_id e fighter; `fact_round` armazena fighter_id e possui índice único (bout_id, fighter_id, round). `fact_bout` possui índice único de bout_id. As relações são verificadas no processo de junção e nos testes. A view `vw_bout_kpis` agrupa contagens e taxas por ano e método.

## Previsões e auditoria

`outputs/predictions_2024.csv`: identificação da luta, data, método (avaliação), leader, other, winner, status, target (1=C, 0=D), probability (P(C)), predicted (probability >=0,5) e baseline_probability.

`exclusions.csv`: URL e motivo de exclusão por qualidade no recorte; sem linhas nesta execução. `unresolved_dates.csv`: registros globais sem data conciliável. `source_check_sample.csv`: amostra de 12 URLs, duas por ano e tipo de decisão, em ordem de URL. `source_checks.json`: data/hora da tentativa, status de acesso e situação da validação de campos. `manifest.json`: arquivo, bytes, SHA-256 e URL versionada.
