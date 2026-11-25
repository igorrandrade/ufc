# Conferência pelos critérios de avaliação

Revisão do ZIP de 25/11/2026. A pontuação final é atribuída pelo professor.

| Critério | Máximo | Evidência no pacote revisado |
|---|---:|---|
| Métricas estratégicas | 1,0 | Relatório seções 1–1.2: usuário, uso editorial, fórmulas, fonte, numeradores, denominadores, empates, atualização e reprodução. KPIs em outputs/kpis.json. |
| Arquitetura e plataforma | 1,0 | Relatório seção 2 e Figura 1: coleta, qualidade, SQLite, Google Colab, análise e apresentação; dependências e comandos documentados. |
| Implementação de BI e Analytics | 1,5 | Pipeline completo, classificador com separação temporal, inferência complementar, cinco abas, arquivos de resultados, notebook executado localmente e código publicável. Ver registros de execução e links de publicação. |
| Apresentação executiva | 0,5 | Slides: conclusão, diferenças por tipo de decisão, casos, limites do modelo e aplicação editorial; mesmos números do relatório e dados. |

## Correções efetuadas

- Integração da inferência complementar ao notebook, à conclusão do painel e ao fluxo local.
- Explicitação dos testes bilaterais e do caráter exploratório dos ICs/p-valores, sem alegar causalidade ou independência garantida entre lutas.
- Precisão do quantil de Wilson corrigida; verificação contra SciPy e teste de denominador inválido.
- Comando único de execução, sincronização de fontes incorporadas e oito células executáveis.
- Vinte testes, incluindo integridade dos registros por atleta/luta; resultados reproduzidos.
- Documentação alinhada, PDF regenerado a partir do Word e slides revisados.
- Pastas de entrega separadas, remoção de caches, guia para Colab e GitHub.

## Limites relevantes

Não se garante nota máxima. A inferência é exploratória. A execução desta revisão no Colab hospedado e a inspeção visual do painel no navegador ainda precisam de conferência. A nova tentativa das 12 fichas em 25/11/2026 permaneceu bloqueada, sem validação dos campos. Reconciliação interna e hashes não substituem essa validação externa. O modelo estima resultados após os três rounds em avaliação retrospectiva; não prevê antes da luta. Não foram mensurados ganhos financeiros ou produtividade do cliente.
