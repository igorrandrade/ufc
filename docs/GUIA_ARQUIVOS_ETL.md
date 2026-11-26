# Arquivos do projeto e preparação dos dados

## O que abrir ou executar

- Entrega acadêmica: ZIP completo, relatório PDF e apresentação PPTX.
- Colab: abra somente `repositorio/notebooks/UFC_BI_Analytics.ipynb` e execute todas as células. As pastas são criadas pelo próprio notebook; ele incorpora o código e o SQL e baixa os CSVs ausentes da versão fixada.
- GitHub: publique o conteúdo de `repositorio/` na raiz. Nesta revisão, o pacote completo também fica em `entrega/Fase2_UFC_Final.zip` para download.
- Consulta sem Python: abra `painel/Painel_UFC.html` no navegador.
- Execução local: na pasta `repositorio/`, instale `requirements.txt` e execute `python -m src.run_all`. Não é necessário executar cada arquivo separadamente.

Arquivos `.md` e `.txt` são documentação; `.csv` são tabelas; `.json` guardam resultados e configurações; `.png` são imagens; `.sql` contém comandos de banco. Dados e resultados não são programas a executar.

## Mapa completo

Caminhos abaixo são relativos à pasta Fase2_UFC do ZIP. No GitHub, o prefixo repositorio/ não existe.

| Arquivo | Conteúdo e finalidade |
|---|---|
| `CONFERENCIA_DOS_CRITERIOS.md` | Relaciona os quatro critérios de avaliação às evidências presentes na entrega. |
| `LEIA_PRIMEIRO.txt` | Instruções de entrega, abertura do painel, Colab e GitHub. |
| `relatorio/Fase2_UFC_Relatorio.pdf` | Relatório acadêmico final para leitura e entrega. |
| `relatorio/Fase2_UFC_Relatorio.docx` | Versão editável do relatório no template da disciplina. |
| `apresentacao/Fase2_UFC_Apresentacao.pptx` | Apresentação executiva editável para exposição do projeto. |
| `apresentacao/Fase2_UFC_Apresentacao.pdf` | Cópia dos slides para consulta. |
| `painel/Painel_UFC.html` | Dashboard pronto para abrir no navegador; contém os dados e os filtros. |
| `repositorio/.gitignore` | Regras para não publicar caches, ambientes e páginas temporárias. |
| `repositorio/README.md` | Página inicial do projeto: problema, resultados, instalação e links. |
| `repositorio/PUBLICACAO.md` | Orientações de acesso e conferências finais. |
| `repositorio/requirements.txt` | Dependências e versões para reproduzir o ambiente Python de referência. |
| `repositorio/notebooks/UFC_BI_Analytics.ipynb` | Notebook autocontido do Colab com oito células de código e resultados. É o único arquivo que precisa ser enviado ao Colab. |
| `repositorio/src/__init__.py` | Identifica src como pacote Python. |
| `repositorio/src/pipeline.py` | Coleta os CSVs, verifica hashes, integra, limpa, seleciona lutas, cria SQLite e calcula KPIs. |
| `repositorio/src/analytics.py` | Treina e avalia a regressão logística, compara a baseline e exporta probabilidades. |
| `repositorio/src/inference.py` | Calcula intervalos de Wilson e testes bilaterais binomial e de Fisher, como complemento exploratório. |
| `repositorio/src/conclusions.py` | Gera a conclusão em Markdown e HTML a partir dos KPIs calculados. |
| `repositorio/src/visuals.py` | Gera quatro gráficos e o painel HTML a partir dos CSVs e JSONs. |
| `repositorio/src/dashboard_template.html` | Modelo do painel com CSS, JavaScript e espaços preenchidos por visuals.py; não é o painel final. |
| `repositorio/src/run_all.py` | Executa preparação, modelo, inferência, visualizações e 27 testes em sequência. |
| `repositorio/src/source_check.py` | Tenta acessar as 12 fichas oficiais e registra a situação. Não valida automaticamente os campos da página. |
| `repositorio/sql/schema.sql` | Cria tabelas, chaves primárias e estrangeiras, CHECKs, índices e três visões analíticas. |
| `repositorio/sql/consultas.sql` | Sete consultas de KPIs, diferenças, estabilidade, casos, ranking e auditoria. |
| `repositorio/tests/test_project.py` | 27 testes automatizados de regras, reconciliação, separação temporal e integridade do banco. |
| `repositorio/data/raw/ufc_event_details.csv` | Catálogo original de eventos: nome, data, localização e URL. |
| `repositorio/data/raw/ufc_fight_results.csv` | Resultados originais: atletas, vencedor, método, formato, round final e URL. |
| `repositorio/data/raw/ufc_fight_stats.csv` | Estatísticas originais por atleta e round: golpes, tentativas, quedas, knockdowns e controle, entre outros. |
| `repositorio/data/processed/bouts.csv` | 665 lutas tratadas; uma linha por luta, com C/D/E, totais e variáveis do modelo. |
| `repositorio/data/processed/rounds.csv` | 3.990 linhas tratadas por atleta, luta e round. |
| `repositorio/data/processed/ufc.sqlite` | Banco relacional com dim_fighter, fact_bout, fact_round e três visões. |
| `repositorio/data/processed/exclusions.csv` | Registro de exclusões por qualidade no recorte; nesta execução contém apenas o cabeçalho, porque nenhuma luta elegível falhou. |
| `repositorio/data/processed/unresolved_dates.csv` | Duas linhas do arquivo global cuja data não foi identificada; não receberam um ano inventado. |
| `repositorio/data/processed/source_check_sample.csv` | As 12 URLs selecionadas para conferência externa: duas por ano e método. |
| `repositorio/docs/index.html` | Painel final publicado; cópia de painel/Painel_UFC.html no ZIP. |
| `repositorio/docs/CONCLUSAO.md` | Resposta à pergunta central, H1, H2, limites e cumprimento dos objetivos. |
| `repositorio/docs/METODOLOGIA.md` | Protocolo de preparação, métricas, modelo, avaliação e limites. |
| `repositorio/docs/DICIONARIO.md` | Definição, unidade e interpretação dos campos de dados. |
| `repositorio/docs/MODELO_DADOS.md` | Tabelas, granularidades, chaves, restrições, visões e consultas SQL. |
| `repositorio/docs/modelo_er.mmd` | Código Mermaid do diagrama entidade-relacionamento. |
| `repositorio/docs/GUIA_DE_USO.md` | Passo a passo de uso e reprodução. |
| `repositorio/docs/AVALIACAO_RUBRICA.md` | Matriz de evidências dos critérios, igual à conferência da raiz. |
| `repositorio/docs/GUIA_ARQUIVOS_ETL.md` | Este guia de arquivos e do processo de extração, transformação e carga. |
| `repositorio/outputs/architecture.png` | Diagrama dos componentes e do fluxo da solução. |
| `repositorio/outputs/modelo_er.png` | Diagrama entidade-relacionamento para leitura e relatório. |
| `repositorio/outputs/concordance.png` | Gráfico de concordância nas decisões unânimes e divididas. |
| `repositorio/outputs/years.png` | Comparação de concordância por ano e tipo de decisão. |
| `repositorio/outputs/holland.png` | Golpes por round do caso Holland × Della Maddalena. |
| `repositorio/outputs/confusion.png` | Matriz de confusão das previsões de teste de 2024. |
| `repositorio/outputs/manifest.json` | URLs fixadas, tamanhos e SHA-256 dos três arquivos originais. |
| `repositorio/outputs/quality.json` | Contagens de origem, conciliação de datas, duplicatas, completude e ausências. |
| `repositorio/outputs/kpis.json` | KPIs globais e por ano/método, H1, H2 e sensibilidade aos empates. |
| `repositorio/outputs/model.json` | Variáveis, medianas, médias, escalas e coeficientes necessários para reproduzir o modelo. |
| `repositorio/outputs/model_metrics.json` | Treino/validação/teste, configuração escolhida e métricas do modelo e da baseline. |
| `repositorio/outputs/predictions_2024.csv` | 247 previsões individuais do teste, com probabilidade e resultado observado. |
| `repositorio/outputs/inference.json` | Intervalos de confiança, p-valores, razão de chances e limites da inferência exploratória. |
| `repositorio/outputs/source_checks.json` | Registro das tentativas de acesso às fichas oficiais; validação dos campos pendente. |
| `repositorio/outputs/execution_validation.json` | Ambiente e resultado dos 27 testes do comando run_all. |
| `repositorio/outputs/notebook_execution.json` | Evidência da execução das oito células e dos testes no notebook. |
| `repositorio/outputs/dashboard_tests.json` | Verificações da lógica do painel com DOM/JavaScript; não equivale a uma inspeção visual em navegador. |

## Como foi feita a extração

A execução usa três arquivos CSV de uma versão fixa do repositório público Greco1899/scrape_ufc_stats, um espelho não oficial do UFCStats. Ela não realiza uma raspagem nova de todo o site oficial. O commit usado é `c742842f29466758fedc3906dbad28d6d320a8da`.

A função `collect()` baixa apenas os arquivos que ainda não existem em `data/raw/`, por URLs que incluem esse commit. Para cada arquivo, calcula SHA-256 e compara com o valor esperado; qualquer diferença interrompe a execução. Origem, tamanho e hash são registrados em `outputs/manifest.json`. Os dados brutos não são alterados.

O snapshot completo contém 796 linhas de eventos, 9.015 de resultados e 42.356 de estatísticas. Esses totais não são o tamanho da amostra final.

## Transformação e limpeza

1. **Leitura e espaços:** os campos são lidos inicialmente como texto, preservando vazios, e os espaços nas extremidades são removidos.
2. **Datas e integração:** as datas são convertidas para o tipo data. Os resultados recebem a data do catálogo por nome de evento, com verificação da cardinalidade da junção. Nomes alternativos são conciliados pela URL da mesma luta. URLs com datas conhecidas conflitantes interrompem o processo. As linhas sem data caem de 27 para duas; as duas restantes são isoladas, sem atribuir ano artificial.
3. **Seleção do recorte:** entram somente lutas de 2022–2024, previstas para três rounds de cinco minutos, encerradas no terceiro round em 5:00, por decisão unânime ou dividida, com vencedor identificável. Das 1.548 URLs com data no período, 665 atendem ao recorte; as outras 883 ficam fora por escopo, não por serem necessariamente dados defeituosos.
4. **Duplicatas:** há 669 linhas elegíveis de resultados para 665 lutas. As quatro repetições são removidas por URL depois da verificação de consistência. Nas estatísticas, a chave é URL + atleta + round: 4.014 linhas passam a 3.990 após a remoção de 24 repetições. Duplicatas conflitantes são sinalizadas, não escolhidas arbitrariamente.
5. **Completude:** cada luta precisa ter os dois atletas nos rounds 1, 2 e 3, totalizando seis linhas. Dados essenciais ausentes, malformados ou inconsistentes geram exclusão com motivo. Nesta execução, nenhuma das 665 lutas elegíveis foi excluída por qualidade.
6. **Conversão numérica:** `SIG.STR.` como `12 of 30` vira 12 acertos e 30 tentativas. Acertos e tentativas precisam ser inteiros não negativos, com acertos menores ou iguais às tentativas. Controle `m:ss` vira segundos de 0 a 300. Campos opcionais inválidos viram ausência, nunca zero. Não houve ausência nos campos opcionais do recorte final.
7. **Agregação:** os três rounds são somados separadamente por atleta. O vencedor vem de W/L ou L/W, respeitando a ordem dos nomes. Cada luta recebe C (líder venceu), D (líder perdeu) ou E (empate em golpes). Empate em golpes não é empate no resultado oficial.
8. **Indicadores:** N = C + D + E. O resultado é 514 C, 146 D e 5 E. A concordância usa somente lutas com líder único: 514/(514+146) = 77,88%. Os cinco empates continuam no total de 665 e no painel, mas ficam fora desse denominador e do classificador.

## Carga e banco de dados

Os arquivos tratados são gravados em `data/processed/`. O SQLite é criado a partir de `sql/schema.sql`, com uma tabela por luta, uma dimensão de atletas e uma tabela por atleta/round. Chaves primárias e estrangeiras, índices e CHECKs protegem a carga. Ao final são executados `integrity_check` e `foreign_key_check`.

As visões SQL apoiam consultas e auditoria, incluindo a comparação dos KPIs com Python. O painel lê CSVs/JSONs produzidos pelo mesmo pipeline e incorpora esses dados ao HTML; não consulta diretamente o banco pelo navegador.

## Preparação para Analytics

O modelo usa sete diferenças entre líder e adversário. Treino inicial: 2022; validação: 2023; teste reservado: 2024. Imputação por mediana e padronização são ajustadas somente com os dados de treino. Depois de escolher a configuração em 2023, o ajuste final usa 2022–2023. Os resultados de 2024 não são usados para escolher os parâmetros.

O alvo é a vitória ou derrota do líder em golpes. Estatísticas dos três rounds concluídos são entradas; o vencedor e o método da decisão não entram como variáveis preditoras. É classificação retrospectiva, não previsão antes da luta.

## Limite da validação

Hashes confirmam a versão dos arquivos e os testes confirmam sua consistência interna. Eles não comprovam que todos os dados do espelho reproduzem a fonte primária. A conferência dos campos das 12 fichas oficiais permanece pendente por bloqueio de acesso. A conclusão deve conservar essa ressalva.
