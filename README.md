# UFC — Golpes significativos e decisões

Análise de BI e Analytics sobre a relação entre golpes significativos e resultados por decisão no UFC. Autor: Igor de Andrade Albuquerque.

[![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/igorrandrade/ufc/blob/main/notebooks/UFC_BI_Analytics.ipynb)

## Pergunta e resultados

Com que frequência o líder em golpes significativos vence a decisão? Como a concordância muda entre decisões unânimes e divididas?

O recorte reúne 665 lutas de 2022–2024, com três rounds completos. Entre as 660 lutas com líder único, ele venceu 514: **77,88%**. A concordância foi **81,85%** nas unânimes e **63,38%** nas divididas. Os cinco empates na contagem permanecem visíveis no painel.

A associação histórica não demonstra causalidade nem erro dos juízes. O painel apoia a consulta por luta e round e a interpretação contextual dos números.

## Executar no Google Colab

Abra o notebook pelo botão acima e selecione **Ambiente de execução → Executar tudo**. O notebook contém os módulos necessários, baixa três CSVs públicos do snapshot fixado e apresenta os painéis. Não requer GPU, chave de API ou montagem do Google Drive.

As saídas gravadas no arquivo vêm de execução local. Ao executar, a última célula registra o ambiente utilizado e o resultado dos testes.

## Executar localmente

Ambiente de referência: Python 3.12. Na raiz do repositório:

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux ou macOS:
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m src.run_all
```

Execute apenas o comando de ativação correspondente ao seu sistema.

O fluxo coleta e valida os dados, prepara o SQLite, calcula indicadores, treina os modelos, gera visualizações e executa os testes. Na primeira execução, requer internet para baixar o snapshot. Os arquivos brutos e o banco são gerados localmente.

Abra **docs/index.html** no navegador para usar o painel. O HTML contém os dados e funciona sem servidor. Links para fichas oficiais exigem internet. No GitHub, use o Colab para interagir com o painel ou baixe o HTML.

Para executar somente os testes, após preparar os dados:

```bash
python -m unittest discover -s tests -v
```

## Estrutura

| Caminho | Conteúdo |
|---|---|
| `notebooks/UFC_BI_Analytics.ipynb` | Notebook autocontido, com resultados e painéis |
| `src/pipeline.py` | Coleta, hashes, limpeza, integração, SQLite e KPIs |
| `src/analytics.py` | Regressão logística com validação e teste temporal |
| `src/forecast.py` | Previsão mensal e comparação com referência histórica |
| `src/inference.py` | Intervalos e testes estatísticos exploratórios |
| `src/visuals.py`, `src/dashboard_template.html` | Gráficos e painel interativo |
| `src/conclusions.py` | Conclusões geradas a partir dos indicadores |
| `src/source_check.py` | Verificação de acesso à amostra de fichas oficiais |
| `src/run_all.py` | Execução completa e testes |
| `sql/` | Esquema, restrições, visões e consultas |
| `data/processed/` | Dados tratados e tabelas de auditoria |
| `outputs/` | Indicadores, previsões, gráficos e registros técnicos |
| `docs/` | Painel, metodologia, dicionário, modelo de dados e conclusão |
| `tests/` | Testes de integridade, cálculos e separação temporal |

## Dados e reprodutibilidade

Fonte primária: [UFCStats](http://ufcstats.com/statistics/events/completed?page=all). A execução utiliza o espelho não oficial [Greco1899/scrape_ufc_stats](https://github.com/Greco1899/scrape_ufc_stats/tree/c742842f29466758fedc3906dbad28d6d320a8da), no commit `c742842f29466758fedc3906dbad28d6d320a8da`.

Os hashes esperados estão no pipeline. `outputs/manifest.json` registra URLs, tamanhos e hashes. Os dados de terceiros permanecem sujeitos às condições de suas fontes.

A conferência dos campos de 12 fichas oficiais permanece pendente por indisponibilidade de acesso. A validação interna verifica hashes, chaves, regras de domínio e reconciliação SQL/Python. O resultado da tentativa de acesso fica em `outputs/source_checks.json`.

## Analytics e limites

A regressão logística usa estatísticas de combates já concluídos. No teste reservado de 2024, acertou 211/247 lutas (**85,43%**), contra 198/247 (**80,16%**) da regra de escolher o líder. Identificou 25 das 49 divergências e não superou a regra simples nas decisões divididas. Não é previsão pré-luta.

A previsão mensal usa apenas meses anteriores. No teste de 2024, o Ridge apresentou MAE de **7,96 p.p.**, contra **6,76 p.p.** da referência histórica, que também foi melhor na validação. A recomendação é manter a referência simples para planejamento exploratório.

Os testes estatísticos não ajustam a dependência entre lutas com atletas repetidos. Não foram medidos ganhos de produtividade ou retorno financeiro. Quando o resultado oficial estiver disponível, as divergências reais podem ser consultadas diretamente no painel.

## Documentação técnica

- [Metodologia e ETL](docs/METODOLOGIA.md)
- [Dicionário de dados](docs/DICIONARIO.md)
- [Modelo de dados e consultas SQL](docs/MODELO_DADOS.md)
- [Conclusão e limites](docs/CONCLUSAO.md)
