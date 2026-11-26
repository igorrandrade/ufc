# Conclusão e respostas à Fase 1

## Resposta à pergunta central

Sim, liderar em golpes significativos conectados foi um indicador associado à vitória nas decisões analisadas. O líder venceu 514 das 660 lutas classificáveis (77,88%) e perdeu 146 (22,12%). Portanto, a liderança acompanhou a vitória na maioria dos casos, mas não garantiu o resultado. Esta conclusão descreve o UFC de 2022–2024, com três rounds completos e decisão unânime ou dividida.

## H1 recebe apoio descritivo

A concordância de 77,88% superou em 27,88 pontos percentuais a referência de 50% definida na Fase 1. Escolher o líder em golpes acertou mais resultados históricos que a referência de escolher aleatoriamente um dos dois atletas. A inferência exploratória complementar é apresentada separadamente e não muda o critério descritivo planejado.

## H2 recebe apoio descritivo

Nas decisões unânimes, o líder venceu 424/518 lutas (81,85%); nas divididas, 90/142 (63,38%). A diferença foi de 18,47 pontos percentuais a favor das unânimes. A mesma direção apareceu em 2022, 2023 e 2024: 16,39, 24,56, 16,25 pontos percentuais, respectivamente. A contagem, assim, acompanhou menos frequentemente o vencedor nas decisões divididas.

## Empates e robustez

As 665 lutas válidas incluem 5 empates em golpes, mantidos no painel e retirados apenas do denominador da concordância. A cobertura classificável foi 99,25%. Atribuir todos os empates aos extremos produz 77,29% a 78,05% de concordância no total válido, ainda acima de 50%. A direção de H2 também permanece nas atribuições extremas. Esses limites são uma análise de sensibilidade, não intervalos de confiança.

## Inferência complementar e seus limites

Sob o modelo de independência, o IC de 95% de Wilson global é 74,56%–80,88%. O teste binomial bilateral resulta em p=6.41e-49, e o teste exato de Fisher bilateral em p=6.87e-06, com razão de chances 2,61. O recorte reúne todos os confrontos elegíveis do snapshot, não uma amostra aleatória. Há atletas repetidos entre lutas; os testes não ajustam essa dependência nem fatores de confusão. ICs e p-valores são condicionais ao modelo de independência, não validação causal ou garantia de generalização.

## O que significa fazer diferença

Os resultados mostram utilidade da liderança em golpes para interpretar o resultado histórico. Não quantificam o efeito causal de um golpe adicional, o peso isolado da contagem no voto de cada juiz ou a probabilidade de uma luta futura. A base não contém os votos individuais por round; as divergências não demonstram erro ou viés de arbitragem. Também não se conclui que vencer a contagem de um round equivale a vencê-lo nos cartões.

## Aplicação para o analista de cobertura esportiva

Usar a contagem como evidência contextual, informando período, tipo de decisão e denominador. Nas divididas, 52/142 lutas (36,62%) tiveram vitória do atleta com menos golpes, o que exige cuidado ao interpretar apenas o total. O caso Holland × Della Maddalena ilustra uma dessas divergências; a conclusão provém do conjunto de lutas, não desse exemplo.

## Cumprimento dos objetivos da Fase 1

A base relacional foi integrada; concordâncias, divergências, empates e denominadores foram calculados; as decisões foram comparadas no conjunto e em cada ano; o painel permite consultar luta e rounds. O quarto objetivo específico permanece parcialmente atendido: as consultas foram reconciliadas internamente, mas a conferência dos campos das 12 fichas oficiais segue pendente por bloqueio de acesso. Os resultados referem-se ao espelho versionado e devem ser revistos se essa conferência identificar discrepâncias.

## Papel complementar do Analytics

O modelo com sete variáveis acrescenta uma análise preditiva retrospectiva exigida na Fase 2. Sua melhora agregada sobre a regra de escolher o líder não mede a contribuição isolada dos golpes significativos e não é a evidência usada para responder a H1 e H2. As hipóteses são respondidas pelas contagens e proporções acima.

## Previsão do mês seguinte

A extensão temporal prevê a taxa de concordância mensal antes de observar o mês-alvo. No teste de 2024, o erro absoluto médio foi 7,96 pontos percentuais no Ridge e 6,76 na referência histórica. A referência simples foi melhor, inclusive na validação de 2023. Não se recomenda substituir essa referência pelo Ridge com a evidência disponível. Esta previsão serve ao planejamento editorial e não identifica o vencedor individual de uma luta.