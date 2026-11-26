# Conferência pelos critérios de avaliação

Revisão final da versão 3, em 25/11/2026. A nota é atribuída pelo professor.

| Critério | Máximo | Evidência |
|---|---:|---|
| KPIs estratégicos | 1,0 | Relatório 1–1.2: cliente editorial, finalidade, fórmulas, fonte, unidade de análise, tratamento dos empates, responsável e atualização. Cálculos em outputs/kpis.json. |
| Arquitetura e plataforma | 1,0 | Relatório 2: diagrama de componentes e modelo ER, coleta versionada, SQLite com PK/FK/CHECK, CSV/JSON, Colab e painel. O painel lê arquivos, sem consultar diretamente as visões SQL. |
| Implementação | 1,5 | Código, SQL, notebook, painel e documentação publicados em https://github.com/igorrandrade/ufc. Pipeline executado, 27 testes, oito células de código e classificação com teste temporal de 2024. |
| Apresentação executiva | 0,5 | Slides com indicadores, comparação por decisão e ano, utilidade editorial, resultados do classificador e limitações. |

## Correções finais

- Descrição da arquitetura alinhada à leitura de CSV/JSON feita pelo painel.
- Hipóteses apresentadas descritivamente nos slides; p-valores exploratórios do agregado explicados no relatório e nas notas, sem sugerir testes por ano.
- Paginação do relatório revisada, preservando o template.
- SQL, funções documentadas, modelo ER e 27 testes da versão 3 preservados.
- Fontes incorporadas ao notebook sincronizadas com o repositório. A última célula registra a execução e distingue IPython local de Colab.
- Guia de cada arquivo e explicação do ETL em docs/GUIA_ARQUIVOS_ETL.md.
- Pacote completo acessível na pasta entrega/ do GitHub.

## Limites registrados

A execução local não comprova execução no Colab hospedado. A conferência externa das 12 fichas do UFCStats permanece pendente por bloqueio de acesso. Os testes estatísticos são exploratórios, sem ajuste de dependência por atletas repetidos ou confundidores. O modelo faz classificação retrospectiva após os três rounds, não previsão pré-luta. Não foram medidos ganhos financeiros ou de produtividade de um cliente real. Não se garante nota máxima.
