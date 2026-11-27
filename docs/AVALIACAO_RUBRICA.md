# Conferência pelos critérios de avaliação

Revisão final da versão 4, concluída em 26/11/2026. A nota é atribuída pelo professor.

| Critério | Máximo | Evidência |
|---|---:|---|
| KPIs estratégicos | 1,0 | Relatório 1–1.2: cliente editorial, finalidade, fórmulas, fonte, unidade de análise, tratamento dos empates, responsável e atualização. Cálculos em outputs/kpis.json. |
| Arquitetura e plataforma | 1,0 | Relatório 2: diagrama de componentes e modelo ER, coleta versionada, SQLite com PK/FK/CHECK, CSV/JSON, Colab e painel. O painel lê arquivos, sem consultar diretamente as visões SQL. |
| Implementação | 1,5 | Código, SQL, notebook, painel e documentação publicados em https://github.com/igorrandrade/ufc. Pipeline executado, 34 testes, nove células de código, classificação retrospectiva e previsão mensal, ambas com teste temporal de 2024. |
| Apresentação executiva | 0,5 | Slides com indicadores, comparação por decisão e ano, utilidade editorial, resultados do classificador e da previsão mensal, comparação com referências e limitações. |

## Correções finais

- Descrição da arquitetura alinhada à leitura de CSV/JSON feita pelo painel.
- Slide 12 apresenta H1/H2, IC de Wilson e p-valores exploratórios do agregado, com ressalva de independência; não sugere testes por ano. O slide 11 apresenta a previsão mensal, a comparação de erros e a decisão recomendada.
- Paginação do relatório revisada, preservando o template.
- SQL, funções documentadas, modelo ER e 34 testes da versão 4 preservados.
- Fontes incorporadas ao notebook sincronizadas com o repositório. A última célula registra a execução e distingue IPython local de Colab.
- Guia de cada arquivo e explicação do ETL em docs/GUIA_ARQUIVOS_ETL.md.
- Pacote completo acessível na pasta entrega/ do GitHub.

## Limites registrados

Em 26/11/2026, o Colab hospedado executou nove células, sem erro, com 34 testes aprovados. Foram observadas as seis abas, o filtro 2024/Dividida, a restauração dos totais, o caso Holland, uma busca sem resultados e os cinco empates. A exportação pela interface não foi confirmada; as saídas gravadas no notebook distribuído são locais. O registro hospedado está em outputs/colab_validation.json e docs/VALIDACAO_COLAB.md. A conferência externa das 12 fichas do UFCStats permanece pendente por bloqueio de acesso. Os testes estatísticos são exploratórios, sem ajuste de dependência por atletas repetidos ou confundidores. A regressão logística classifica retrospectivamente após os três rounds. A extensão Ridge prevê a taxa de concordância do mês seguinte usando somente o passado; não prevê vencedores individuais. Não foram medidos ganhos financeiros ou de produtividade de um cliente real. Não se garante nota máxima.
