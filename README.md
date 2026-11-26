# UFC — Golpes significativos e decisões

Projeto de Igor de Andrade Albuquerque para a Fase 2 de Business Intelligence e Analytics.

[![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/igorrandrade/ufc/blob/main/notebooks/UFC_BI_Analytics.ipynb)

## Resposta à pesquisa da Fase 1

**Sim, liderar em golpes significativos esteve associado à vitória nas decisões deste recorte:** 514/660 = **77,88%**. A liderança não garantiu a vitória: houve 146 divergências (22,12%).

**H1 recebe apoio descritivo:** 27,88 pontos percentuais acima da referência de 50%. **H2 recebe apoio descritivo:** 81,85% nas unânimes e 63,38% nas divididas, diferença de 18,47 pontos percentuais, na mesma direção nos três anos.

A associação histórica não demonstra o efeito causal dos golpes nem o peso da contagem no voto dos juízes. Leia [a conclusão completa e o cumprimento dos objetivos](docs/CONCLUSAO.md). A quarta meta da Fase 1, de conferência contra fichas oficiais, permanece parcialmente atendida por bloqueio de acesso.

## O problema e o usuário

Um analista de cobertura esportiva precisa verificar quando o líder em golpes significativos também é o vencedor oficial. A contagem bruta não substitui o julgamento round a round. A solução ajuda a conferir afirmações editoriais e localizar casos para análise individual. Não mede erro de arbitragem nem estima retorno financeiro.

## Resultados executados

- 665 lutas válidas em 2022–2024, 3.990 registros por atleta e round.
- 514 concordâncias, 146 divergências e 5 empates na contagem.
- Concordância: 514/660 = 77,88%.
- Unânimes: 424/518 = 81,85%; divididas: 90/142 = 63,38%.
- Diferença de 18,47 pontos percentuais. A direção se mantém nos três anos.
- Modelo no teste de 2024: 211/247 acertos = 85,43%, versus 198/247 = 80,16% da baseline.
- O modelo identificou 25 das 49 divergências. Nas decisões divididas não superou a baseline em acurácia.

## Pacote completo

[Baixar todos os arquivos da entrega](https://github.com/igorrandrade/ufc/raw/refs/heads/main/entrega/Fase2_UFC_Final.zip): relatório PDF/Word, apresentação PPTX/PDF, painel, dados e projeto técnico.

[Mapa de arquivos e explicação do ETL](docs/GUIA_ARQUIVOS_ETL.md).

## Guia rápido

No Colab, abra apenas `notebooks/UFC_BI_Analytics.ipynb` e execute tudo. No GitHub, publique o conteúdo desta pasta na raiz, mantendo `src/`, `notebooks/`, `data/`, `outputs/`, `docs/`, `sql/` e `tests/`. Não envie a pasta externa `repositorio/` como um nível adicional. Consulte [o guia completo](docs/GUIA_DE_USO.md).

## Executar

Python 3.12 é o ambiente de referência. Na raiz do repositório:

```bash
python -m pip install -r requirements.txt
python -m src.run_all
```

Abra `docs/index.html` no navegador. Os dados estão incorporados ao HTML e os filtros funcionam sem servidor ou conexão externa. As fichas oficiais exigem conexão.

### Google Colab

O notebook `notebooks/UFC_BI_Analytics.ipynb` é autocontido: use Arquivo → Fazer upload do notebook e Ambiente de execução → Executar tudo. A primeira célula reconstitui os módulos; os CSVs ausentes são baixados do commit fixado. O notebook apresenta gráficos, painéis interativos, métricas e testes. Não exige GPU, chave de API ou serviço pago. Foi executado localmente em IPython e no Google Colab em 26/11/2026: nove células de código, zero erro e 34 testes aprovados. O registro da execução hospedada está em `outputs/colab_validation.json`.

O Colab também permite abrir o notebook pela aba GitHub ou pelo link abaixo. O GitHub exibe resultados estáticos, mas a interação deve ocorrer no Colab ou no HTML. O diretório `docs/` pode ser publicado pelo GitHub Pages como alternativa de acesso ao painel, sem substituir o notebook da plataforma escolhida.

## Organização

- `src/pipeline.py`: coleta, hashes, limpeza, integração, SQLite e indicadores.
- `sql/schema.sql` e `sql/consultas.sql`: esquema relacional (PK/FK/CHECK, índices, visões) e consultas analíticas. Ver [modelo de dados](docs/MODELO_DADOS.md).
- `src/inference.py`: IC de Wilson, teste binomial (H1) e teste de Fisher (H2), de caráter exploratório.
- `src/run_all.py`: executa todo o fluxo e os testes com um comando.
- `src/analytics.py`: treinamento, seleção, teste e exportação de probabilidades.
- `src/visuals.py`: gráficos e painel HTML incorporável ao notebook.
- `src/source_check.py`: acessibilidade das fichas da amostra; acesso não equivale a validação dos campos.
- `data/raw/`: criado pela coleta do snapshot fixado; arquivos conferidos por SHA-256. Os CSVs brutos também acompanham o ZIP da entrega.
- `data/processed/`: lutas, rounds, exclusões, datas não resolvidas e amostra. O SQLite é gerado pelo pipeline e também acompanha o ZIP da entrega.
- `outputs/`: KPIs, métricas, previsões, parâmetros do modelo, manifesto e registros de validação.
- `docs/`: painel e documentação metodológica.
- `tests/`: 34 testes (casos limites, reconciliação, restrições do banco e consultas SQL).

## Fonte e período

Fonte primária: UFCStats. Fonte utilizada: espelho não oficial [Greco1899/scrape_ufc_stats](https://github.com/Greco1899/scrape_ufc_stats/tree/c742842f29466758fedc3906dbad28d6d320a8da), commit `c742842f29466758fedc3906dbad28d6d320a8da`. O snapshot foi identificado na Fase 1 e mantido nesta execução. `outputs/manifest.json` contém URLs, tamanhos e hashes completos. O período de análise é 2022–2024, independentemente da atualização do espelho em 2026.

Não altere os arquivos brutos. Dados de terceiros permanecem sujeitos aos direitos e condições de suas fontes; este projeto acadêmico não atribui licença própria a esses dados.

## Escopo e qualidade

Inclusão: data identificada entre 2022 e 2024, `3 Rnd (5-5-5)`, round final 3, tempo 5:00, `Decision - Unanimous` ou `Decision - Split`, resultado `W/L` ou `L/W`. Cada luta exige seis linhas válidas. Os cinco empates em golpes são válidos nos KPIs e excluídos apenas do classificador.

Aliases de evento produziram 669 linhas elegíveis de resultados para 665 URLs e 4.014 linhas de estatísticas antes da deduplicação. Removeram-se quatro resultados repetidos e 24 registros repetidos por atleta/round, sem excluir lutas. Duas linhas do arquivo global ficaram sem data identificável e estão separadas em `unresolved_dates.csv`; não se atribuiu ano artificial a elas.

A conferência externa de 12 fichas ficou pendente: as respostas retornaram bloqueio/verificação de navegador ou erro de acesso, sem tabelas de estatísticas. Não se declarou validação externa concluída. A validação interna abrange as chaves, regras, contagens, hashes e igualdade SQL/Python.

## Modelo preditivo

Ver `docs/METODOLOGIA.md`. O modelo estima a concordância com base nas estatísticas do próprio combate já concluído, em uma avaliação retrospectiva de decisões. Não é previsão pré-luta nem serviço de classificação ao vivo. O recorte é condicionado ao tipo de encerramento observado; não se generaliza a nocautes, finalizações, decisões majoritárias ou lutas de cinco rounds.

## Acesso

Repositório: https://github.com/igorrandrade/ufc

Notebook no Colab: https://colab.research.google.com/github/igorrandrade/ufc/blob/main/notebooks/UFC_BI_Analytics.ipynb

O notebook foi executado localmente e no Colab hospedado, com nove células sem erro e 34 testes aprovados. A amostra externa de 12 fichas segue pendente.

## Etapas individuais e inferência complementar

Ordem: `python -m src.pipeline`, `python -m src.analytics`, `python -m src.inference`, `python -m src.visuals`, `python -m unittest discover -s tests -v`. O comando `src.run_all` já executa todas. A inferência de Wilson/binomial/Fisher é exploratória: há atletas repetidos e o recorte não é uma amostra aleatória; os p-valores não comprovam causalidade.

## Previsão mensal anterior ao período previsto

A aba Previsão mensal complementa a classificação retrospectiva. O Ridge prevê C/(C+D) do mês seguinte usando os três meses anteriores, sem estatísticas do mês-alvo. Treino inicial: nove meses de 2022; validação: 2023; reajuste: 21 meses até 2023; teste: 12 previsões móveis de um passo em 2024, com coeficientes congelados. A referência é a concordância acumulada até o mês anterior. MAE no teste: Ridge 7,96 p.p.; referência 6,76 p.p. A referência também teve menor erro na validação. Não há evidência para substituí-la pelo Ridge. A série curta e a ausência de intervalo de previsão calibrado limitam o uso a planejamento exploratório. Código e previsões estão em `src/forecast.py` e `outputs/forecast_2024.csv`.
