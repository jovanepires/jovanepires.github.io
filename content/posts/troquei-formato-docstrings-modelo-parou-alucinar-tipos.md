---
title: "Docstring é input de modelo. E o formato importa."
date: 2026-03-19T00:00:00-03:00
description: "Troquei o formato das minhas docstrings. O modelo parou de alucinar tipos."
image: ""
draft: true
tags: ["ai-engineering", "rag", "tokenizacao", "python", "docstrings", "bpe", "data-quality", "context-window", "engenharia-de-dados"]
---

O modelo errava os tipos. O tempo todo.

Fui revisitar um módulo antigo de qualidade de dados — funções de completude, unicidade, validação de intervalo. Código que escrevi anos atrás, quando ainda estava aprendendo Python num ambiente científico. Resolvi usar um SLM local para ajudar na refatoração.

Ele sugeria parâmetros com tipos errados. Gerava retornos que não batiam com o contrato real. Propunha lógica que ignorava o que estava documentado ali na frente dele.

Reescrevi o prompt três vezes. Mesmo resultado.

Na quarta tentativa parei de culpar o prompt e fui olhar para o código.

## O problema estava nos traços

As docstrings seguiam o estilo NumPy. Faz sentido: quando aprendi Python, o ambiente era científico — NumPy, pandas, scikit-learn. Todo mundo usava esse formato. Copiei sem questionar, como a gente copia muita coisa no começo.

A função que mais me dava problema era uma regra de completude padrão:

```python
def calcular_completude(df, col_ref, col_valor):
    """
    Calcula a proporção de valores preenchidos em uma coluna,
    considerando apenas registros válidos com base em uma coluna de referência.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame de entrada contendo os dados a serem analisados.
    col_ref : str
        Nome da coluna de referência utilizada para filtrar registros válidos.
    col_valor : str
        Nome da coluna cuja completude será avaliada.

    Returns
    -------
    float
        Proporção de valores não nulos na coluna avaliada (0 a 1).
    """
```

Rodei o tiktoken com o `cl100k_base` e contei: 192 tokens.

Reescrevi a mesma função no estilo Google, seguindo o [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html):

```python
def calcular_completude(df, col_ref, col_valor):
    """
    Calcula a proporção de valores preenchidos em uma coluna,
    considerando registros válidos com base em uma coluna de referência.

    Args:
        df (pd.DataFrame): DataFrame de entrada com os dados.
        col_ref (str): Coluna usada para filtrar registros válidos.
        col_valor (str): Coluna cuja completude será avaliada.

    Returns:
        float: Proporção de valores não nulos (0 a 1).
    """
```

147 tokens. Mesma informação. 23% a menos.

Mas a contagem era a parte menos interessante do que estava acontecendo.

## Por que o formato muda o que o modelo entende

O `cl100k_base` usa Byte Pair Encoding — BPE. Philip Gage descreveu o algoritmo em 1994, e ele foi adaptado para os tokenizadores modernos. A ideia central é simples: o tokenizador aprende quais sequências de caracteres aparecem juntas com frequência no corpus de treinamento e as une em tokens únicos.

Na prática, tokenização é compressão estatística orientada por frequência.

É aí que o estilo NumPy começa a perder. As linhas `----------` e `-------` são ASCII decorativo. O próprio [numpydoc Style Guide](https://numpydoc.readthedocs.io) admite: o formato foi desenhado para legibilidade em terminal, não para densidade de informação.

Em termos de tokenização, o efeito é esse: `---` é um token único no `cl100k_base` — o tokenizador aprendeu esse merge porque sequências de três hífens são comuns em texto. Mas `----------` não tem merge aprendido para toda a sequência. O tokenizador a quebra em partes — `---`, `---`, `---`, `-` — quatro tokens no lugar de nenhuma informação semântica.

Tokens sem conteúdo. Espaço desperdiçado.

O estilo Google resolve isso de outra forma também. O formato é mais linear, mais próximo da prosa técnica que domina os corpora de treinamento. Tipo e parâmetro ficam na mesma linha: `col_ref (str):` é uma unidade coesa. No estilo NumPy, a mesma informação está espalhada — nome numa linha, tipo na outra, descrição na terceira. A relação semântica entre eles se fragmenta dentro da janela de contexto.

E modelos são sensíveis a isso.

Liu et al. (2023), em "[Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172)" (Stanford, UC Berkeley e Samaya AI), mostraram que o desempenho do modelo cai quando a informação relevante está dispersa no contexto. O efeito acontece até dentro de uma docstring — quando tipo, nome e descrição estão em linhas diferentes, o modelo precisa conectar fragmentos em vez de ler uma unidade.

## O que mudou quando converti

Converti as funções para o estilo Google à mão, função por função. Não queria fazer uma substituição cega — queria entender o que mudava em cada uma.

Voltei com o mesmo pedido de refatoração que tinha falhado antes.

O modelo acertou os tipos. Inferiu corretamente os casos de erro. Gerou código consistente com o contrato do módulo sem que eu precisasse explicar esse contrato no prompt.

O problema nunca foi o prompt.

## O problema em escala

Achei que era um detalhe pontual. Aí fiz a conta.

Um catálogo de data quality em produção tem dezenas, às vezes centenas de regras — cada uma com sua docstring. Quando você injeta esse módulo numa janela de contexto para gerar documentação, analisar cobertura ou sugerir novas regras, o conteúdo inteiro entra junto.

A diferença medida foi de 45 tokens por função. Em 100 funções, são 4.500 tokens a mais por chamada. Tokens que poderiam estar sendo usados por lógica de negócio, exemplos de uso ou contexto de domínio.

O impacto em RAG é ainda mais direto. Se você mantém um catálogo com busca semântica — padrão em plataformas de data quality — os embeddings gerados a partir de docstrings no estilo NumPy carregam ruído estrutural. Tokens sem conteúdo semântico contribuem para o vetor como ruído. A representação fica menos fiel ao significado real da função.

Testei no próprio módulo: gerei embeddings com docstrings no estilo NumPy, avaliei a recuperação, depois gerei de novo no estilo Google. A diferença de precisão foi clara o suficiente para mudar meu padrão de vez.

## O leitor que ninguém contou que ia aparecer

Quando aprendi a escrever docstrings, havia um único leitor: o humano que ia manter o código depois de mim.

Esse leitor ainda existe. Mas agora tem outro.

Cada vez que um pipeline de RAG recupera uma função para compor contexto, cada vez que um modelo lê o contrato de uma função para sugerir algo coerente, a docstring é consumida como dado. O formato que você escolheu lá atrás determina como esse dado vai ser tokenizado, vetorizado e recuperado.

Docstring não é mais só documentação. É payload do seu pipeline de IA.

O estilo NumPy tem elegância visual — é o padrão das bibliotecas científicas que admiro, faz sentido em notebooks, em ambientes científicos. Mas para código que alimenta pipelines de RAG e geração de contexto, o estilo Google não é preferência estética.

É uma decisão de engenharia.

## O que eu faria diferente

Instrumentar antes de experimentar.

Saí desse fim de semana com evidências qualitativas quando poderia ter saído com métricas. Taxa de acerto de tipo nas sugestões do modelo. Número de rejeições manuais. Precisão@K na recuperação vetorial com K fixo.

Não defini nenhuma dessas métricas antes de começar. O aprendizado ficou menos transferível do que poderia ter sido.

Aprendi o resultado. Não aprendi a medir o resultado.

Hoje todo projeto começa com o estilo Google. Não por estética — o estilo NumPy tem uma elegância que o Google não tem. Mas a docstring tem dois leitores agora.

Escrevo para os dois.

## Conclusões

- O estilo NumPy gerou 192 tokens contra 147 do estilo Google nas docstrings testadas — 23% a mais, sendo parte desse overhead tokens de separadores que não carregam nenhum conteúdo semântico. A diferença exata varia com o conteúdo, mas a direção é consistente.
- O mecanismo é BPE (Gage, 1994): sequências longas de hífens não têm merges eficientes aprendidos e são fragmentadas em grupos de tokens sem conteúdo. `----------` vira quatro tokens onde havia zero informação.
- O estilo Google produz sugestões mais precisas porque agrupa tipo e parâmetro como unidade semântica coesa — reduz a fragmentação que Liu et al. (2023) mostraram afetar o desempenho do modelo em contextos longos.
- Em pipelines de RAG, embeddings de docstrings no estilo NumPy carregam mais ruído estrutural. Vetores mais ruidosos representam menos fielmente o significado real da função, e a recuperação semântica piora.
- Se você vai experimentar: meça antes. Taxa de acerto de tipo, precisão@K, rejeições manuais. Não deixe para depois.

## Referências

- Gage, P. (1994). A New Algorithm for Data Compression. *C Users Journal*, 12(2), 23–38.
- Liu, N. F. et al. (2023). Lost in the Middle: How Language Models Use Long Contexts. [arXiv:2307.03172](https://arxiv.org/abs/2307.03172).
- OpenAI. [How to count tokens with tiktoken](https://cookbook.openai.com/examples/how_to_count_tokens_with_tiktoken). OpenAI Cookbook.
- OpenAI. [tiktoken](https://github.com/openai/tiktoken). GitHub.
- Google. [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html).
- NumPy. [numpydoc Style Guide](https://numpydoc.readthedocs.io).
- Python. [PEP 257 — Docstring Conventions](https://peps.python.org/pep-0257/).
