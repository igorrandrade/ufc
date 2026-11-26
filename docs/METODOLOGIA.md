# Metodologia e critérios

## CRISP-DM

1. Negócio: apoiar a conferência editorial de estatísticas de UFC.
2. Compreensão: eventos, resultados e estatísticas por atleta/round no espelho público.
3. Preparação: verificar hashes, conciliar aliases por URL, padronizar textos e tipos, aplicar filtros e validar a grade completa de rounds.
4. Modelagem: KPIs em SQLite/Python e regressão logística com sete diferenças entre líder e adversário.
5. Avaliação: reconciliação SQL/Python, 27 testes, comparação temporal contra baseline e interpretação por tipo de decisão.
6. Implantação: notebook Colab e painel exportado. Código, notebook e painel disponíveis em https://github.com/igorrandrade/ufc. A execução hospedada no Colab foi concluída em 25/11/2026, com oito células sem erro e 27 testes aprovados (`outputs/colab_validation.json`).

## KPIs de negócio

A unidade de análise é a luta. C = líder venceu; D = líder perdeu; E = empate na contagem. N = C + D + E.

| Indicador | Fórmula | Uso editorial |
|---|---|---|
| Concordância | 100 C/(C+D) | Quantificar a frequência em que a contagem acompanha o resultado |
| Divergência | 100 D/(C+D) | Dimensionar casos que exigem análise contextual |
| Diferença entre decisões | Concordância unânimes menos divididas | Evitar aplicar a mesma leitura aos dois grupos |
| Cobertura classificável | 100(C+D)/N | Mostrar quanto do conjunto tem líder único |
| Volume analisado | N e contagens C, D, E | Tornar visíveis o tamanho do recorte e os denominadores |

Denominador zero é não calculável, nunca 0%. Os filtros recalculam numerador e denominador. A frequência dos empates é 100E/N. As taxas descrevem o período; não se define meta de aumentar concordância, pois o projeto não controla o resultado esportivo.

H1: concordância global acima de 50%, usada como referência aleatória. H2: taxa nas unânimes maior que nas divididas, contraste principal. São hipóteses descritivas; a inferência adicional é exploratória e não substitui esse critério. Os limites 100C/N e 100(C+E)/N mostram sensibilidade às duas atribuições extremas dos empates, não incerteza amostral.

## Predição

Alvo 1: concordância. Alvo 0: divergência. Momento informacional: após os três rounds completos. Variáveis explicativas, sempre líder menos adversário: acertos significativos, tentativas, precisão (acertos/tentativas), saldo de rounds em que cada um liderou a contagem, quedas conectadas, knockdowns e segundos de controle. Saldo de rounds de golpes não equivale a rounds vencidos nos cartões.

Método da decisão, vencedor, placares, URL e nomes não são entradas do classificador. O método é usado apenas para descrever a população e estratificar os resultados depois da previsão. A seleção retrospectiva restringe a validade aos combates elegíveis; não valida uso prospectivo antes de conhecer o tipo de encerramento.

Treino inicial: 204 lutas de 2022. Validação: 209 de 2023. Valores de C: 0,1; 1; 10. Menor log loss de validação selecionou C = 0,1. Treino final: 413 lutas de 2022–2023. Teste final: 247 lutas de 2024, sem ajuste posterior. Limiar 0,5. Pipeline: imputação mediana, padronização e regressão logística; estatísticas de transformação são ajustadas só no treino. Os campos utilizados não tiveram ausências no recorte, mas o procedimento evita usar informações do teste em futuras execuções.

A baseline usa probabilidade constante igual à taxa de concordância do treino final (316/413 = 76,51%). No limiar de 0,5, prevê vitória do líder em todos os casos. Métricas: acurácia, acurácia balanceada, precisão/recall/F1 da classe concordância, recall das divergências, ROC-AUC, log loss, Brier e matriz de confusão. A baseline foi comparada nos mesmos 247 registros do modelo.

O modelo acertou 211/247, contra 198/247 da baseline. Identificou 25/49 divergências e marcou outras 12 lutas como divergências incorretamente. Nas 59 decisões divididas, ambos acertaram 40/59. O ganho agregado não autoriza alegar superioridade em todos os segmentos.

## Operação e manutenção

Responsável proposto: autor/analista editorial. Atualização por lote quando houver novo período de estudo. A versão de 2022–2024 é congelada e não depende de atualização diária. Para outro período: registrar novo commit, revisar filtros e hashes, reexecutar testes e separar novo teste temporal. Não misturar dados novos no teste histórico sem informar a mudança de protocolo.

Antes de publicação de uma afirmação editorial, conferir a ficha e o resultado oficial. Sugestão de uso: consultar divergências, examinar rounds e contexto e redigir com denominador e período. Não há mensuração real de redução de tempo, aumento de audiência ou retorno financeiro neste projeto.

Referências técnicas: Aulas 6 a 10 fornecidas pela disciplina; Google Colab FAQ; scikit-learn LogisticRegression e Common pitfalls. Fonte esportiva: UFCStats via snapshot Greco1899 indicado no README.

## Respostas à Fase 1

A conclusão em [CONCLUSAO.md](CONCLUSAO.md) responde à pergunta central, H1, H2, robustez e objetivos. Ela é gerada por `src/conclusions.py` a partir dos KPIs efetivamente calculados. O projeto mantém o recorte e o delineamento observacional da Fase 1. A substituição do Streamlit pelo Colab atende às plataformas permitidas na Fase 2; o modelo preditivo é uma extensão exigida nesta fase e não altera as hipóteses originais.

## Inferência exploratória complementar

`src/inference.py` calcula Wilson a 95%, teste binomial bilateral contra 50% e Fisher bilateral para a tabela [[424,94],[90,52]]. O notebook executa esta etapa antes das visualizações. Os testes assumem independência, não ajustam atletas repetidos e não transformam o censo do recorte em amostra aleatória. Os valores e pressupostos ficam em `outputs/inference.json`. Fontes: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binomtest.html e https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.fisher_exact.html.
