# Guia de uso

COMO USAR E ENTREGAR O PROJETO UFC
Revisão de 25/11/2026 — Igor de Andrade Albuquerque

COMECE AQUI
1. Extraia o ZIP completo antes de abrir os arquivos.
2. Para ler o trabalho: relatorio/Fase2_UFC_Relatorio.pdf.
3. Para apresentar: apresentacao/Fase2_UFC_Apresentacao.pptx.
4. Para ver os filtros sem executar Python: painel/Painel_UFC.html (abra no navegador).
5. Para reproduzir cálculos e modelo: abra somente repositorio/notebooks/UFC_BI_Analytics.ipynb no Colab e execute todas as células.
6. Para entregar à disciplina: envie o ZIP completo corrigido. Ele contém o relatório PDF e a apresentação exigidos, além da solução e suas evidências.

O QUE EXISTE EM CADA PASTA
relatorio/ — Relatório acadêmico em PDF (entrega/leitura) e DOCX (edição). Não executar nem enviar ao Colab.
apresentacao/ — Slides em PPTX (apresentar/editar) e PDF (consulta). Não enviar ao Colab.
painel/ — Painel_UFC.html, cópia pronta do dashboard. Basta abrir no navegador; funciona localmente sem servidor. Os links às fichas oficiais exigem internet.
repositorio/ — Projeto técnico para reprodução e publicação no GitHub. O README explica o método e o comando de execução.
repositorio/notebooks/ — Notebook .ipynb autocontido, único arquivo necessário para começar no Colab.
repositorio/src/ — Código Python de coleta, limpeza, KPIs, modelo, inferência complementar, conclusão, gráficos e painel. run_all.py coordena as etapas.
repositorio/data/raw/ — Três CSVs originais e congelados, conferidos por SHA-256. Não editar. São dados de entrada, não programas.
repositorio/data/processed/ — CSVs tratados, banco ufc.sqlite, amostra de fichas e registros de exclusões. Gerados pelo código; não executar nem alterar manualmente.
repositorio/outputs/ — KPIs, previsões, parâmetros, inferência, gráficos e registros de validação. São resultados, não scripts. O diagrama architecture.png é documental.
repositorio/docs/ — index.html (dashboard), dicionário, método, conclusão, guia e conferência da rubrica. Abrir .html no navegador; ler .md no GitHub/editor.
repositorio/tests/ — Testes automatizados. São executados pelo notebook ou pelo comando único local; não é necessário rodá-los separadamente no Colab.

COLAB — NÃO ENVIE O ZIP NEM TODAS AS PASTAS
Opção A: abra o link do notebook:
https://colab.research.google.com/github/igorrandrade/ufc/blob/main/notebooks/UFC_BI_Analytics.ipynb
Opção B: em https://colab.research.google.com, use Arquivo > Fazer upload de notebook e escolha:
repositorio/notebooks/UFC_BI_Analytics.ipynb

Depois:
1. Conecte o ambiente e selecione Ambiente de execução > Executar tudo.
2. Use CPU; não precisa de GPU, chave de API ou Drive montado.
3. O notebook cria as pastas, reconstitui os módulos e baixa os três CSVs da versão fixada. Ele verifica os hashes antes de calcular.
4. Aguarde as oito células de código. Confirme a conclusão dos 20 testes, sem erros, e os resultados: 665 lutas; 514 concordâncias; 146 divergências; 5 empates; 77,88% de concordância.
5. Na seção de painéis, use as cinco abas. A aba Conclusão responde a H1 e H2. A seção 3.1 reproduz a inferência exploratória.
6. Salve uma cópia no Drive se quiser conservar a execução. O ambiente temporário do Colab pode ser apagado; salvar o notebook não guarda automaticamente todos os arquivos gerados.

Se houver erro no download, não altere os hashes: os mesmos CSVs já estão em repositorio/data/raw/. No painel de arquivos do Colab, crie/abra /content/ufc_bi/data/raw, envie somente os três CSVs e execute novamente a partir da coleta. Se o painel interativo não aparecer, abra painel/Painel_UFC.html no seu computador; isso não substitui conferir a execução do notebook no Colab.

GITHUB — ENVIE O CONTEÚDO DE repositorio/, NÃO A PASTA EXTERNA
Os caminhos esperados na raiz do projeto são:
README.md, requirements.txt, .gitignore, PUBLICACAO.md, src/, notebooks/, data/, outputs/ e docs/, tests/.
Assim, o notebook fica em notebooks/UFC_BI_Analytics.ipynb, e não em repositorio/notebooks/UFC_BI_Analytics.ipynb.

Para publicar manualmente ou em outro repositório:
1. Abra o repositório e escolha Add file > Upload files.
2. Abra repositorio/ no seu computador. Arraste seus arquivos e subpastas para a área de upload, mantendo a estrutura interna.
3. Confira os caminhos antes de confirmar o commit. O ZIP do trabalho é para a disciplina; subir apenas esse ZIP não publica o código e o notebook como arquivos navegáveis.
4. Não envie __pycache__, .pyc, .venv, .ipynb_checkpoints ou páginas temporárias de validação. Esses itens foram retirados do pacote e constam no .gitignore.
5. Confirme o commit e abra README.md e notebooks/UFC_BI_Analytics.ipynb para conferir. Se mudar usuário ou nome do repositório, atualize os links no relatório e nos slides.
6. O GitHub permite visualizar o notebook, mas o HTML listado no repositório aparece como código. Para usar o dashboard, execute o notebook no Colab ou baixe e abra docs/index.html.
7. Opcionalmente, publique docs/ via GitHub Pages: Settings > Pages > Deploy from a branch > main > /docs > Save. Use somente o endereço que o GitHub mostrar após a publicação; não presuma que Pages já está ativo.

Relatório e slides ficam fora de repositorio/ para separar a entrega acadêmica do código. É opcional colocá-los em uma pasta entrega/ do GitHub. Não são necessários para executar o notebook.

EXECUÇÃO LOCAL OPCIONAL
Se preferir Colab, ignore esta etapa. No terminal, entre na pasta repositorio/ e execute:
python -m pip install -r requirements.txt
python -m src.run_all

Esse comando refaz o pipeline, os modelos, os testes estatísticos, o painel e os 20 testes. Depois, abra docs/index.html. Não execute os .py dando dois cliques: eles usam importações de pacote. Para rodar apenas uma etapa, a ordem está no README.

CONFERÊNCIAS QUE AINDA EXIGEM ATENÇÃO
A revisão foi executada localmente. Ainda é necessário conferir esta versão no Colab hospedado e fazer a revisão visual do painel no seu navegador. As 12 fichas oficiais continuaram sem tabelas acessíveis em 25/11/2026; seus campos não foram declarados validados. Essas limitações estão registradas no relatório.

FONTES DAS INSTRUÇÕES
Google Colab FAQ: https://research.google.com/colaboratory/intl/pt-BR/faq.html
GitHub Upload: https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository
