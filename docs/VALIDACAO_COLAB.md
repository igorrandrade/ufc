# Validação no Google Colab — 26/11/2026

Foi executado **Executar tudo** no notebook público do commit `1ff32a09546507c6a972350da32127155d1b6fb7`. A interface concluiu as nove células de código; a última registrou Python 3.13.18, **34 testes aprovados e zero erro**, em `2026-11-26T17:45:19.984002+00:00` (14h45 em Brasília).

| Verificação na interface hospedada | Resultado observado |
|---|---|
| Panorama completo | 665 lutas; 514/660 = 77,88%; 146 divergências; 5 empates |
| Filtros 2024 + Dividida | 60 lutas; 40/59 = 67,80%; 19 divergências; 1 empate |
| Limpar filtros | Retornou aos totais do período completo |
| Conferir uma luta | Holland × Della Maddalena: 127 × 105 acertos; três rounds apresentados |
| Busca sem correspondência | “Nenhuma luta encontrada.” |
| Classificação E | Cinco lutas listadas |
| Modelo preditivo | Teste com 247 lutas; 211 acertos; 85,43%; ganho de 5,26 p.p. |
| Previsão mensal | 12 meses de 2024; MAE Ridge 7,96 p.p.; referência 6,76 p.p.; tabela com datas de corte |
| Conclusão | Resposta central, H1/H2, sensibilidade e limites visíveis |
| Dados e critérios | Conferência externa explicitamente pendente: 0/12 fichas |

Todas as seis abas responderam à navegação. A inspeção identificou baixo contraste no título dentro do Colab; foi acrescentada cor branca explícita ao título. Essa correção cosmética e os textos de documentação são posteriores à execução registrada e não mudam cálculos ou lógica dos filtros.

## Alcance da evidência

Este documento transcreve observações da interface; não substitui uma certificação independente. Os 34 testes automatizados incluem integridade relacional, reconciliação SQL/Python, hipóteses de contagem, ausência de vazamento do alvo e sete verificações da previsão mensal. A inspeção manual cobre os controles listados, sem testar todas as combinações possíveis.

O comando Download .ipynb foi acionado, mas o mecanismo de captura não confirmou um arquivo. As saídas gravadas no notebook distribuído continuam provenientes da execução local, identificada no próprio notebook. A execução hospedada é documentada separadamente em `outputs/colab_validation.json`; não se declara que o arquivo foi baixado do Colab. Os downloads CSV também não foram confirmados em navegador. As tabelas equivalentes já estão entregues em `outputs/` e `data/processed/`.

Para repetir, abra o notebook, execute todas as células e confira a última saída. O código detecta Google Colab ou IPython local e grava a evidência do ambiente utilizado. Não requer GPU, serviços pagos ou montagem do Drive.
