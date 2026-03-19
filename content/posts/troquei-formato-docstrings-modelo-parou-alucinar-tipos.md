---
title: "Docstring é input de modelo. E o formato importa."
date: 2026-03-19T00:00:00-03:00
description: "Troquei o formato das minhas docstrings. O modelo parou de alucinar tipos."
image: ""
draft: true
tags: ["ai-engineering", "rag", "tokenizacao", "python", "docstrings", "bpe", "data-quality", "context-window", "engenharia-de-dados"]
---

Fui revisitar um projeto antigo de qualidade de dados. Um módulo que escrevi anos atrás, quando ainda estava aprendendo Python num contexto científico. Funções de completude, unicidade, validação de intervalo. O tipo de código que qualquer engenheiro de dados já escreveu inúmeras vezes.

Resolvi usar um modelo SLM local para ajudar na refatoração. Parecia uma boa ideia na época.

O modelo errava os tipos dos parâmetros o tempo todo. Gerava retornos que não batiam com o contrato real das funções. Sugeria lógica que ignorava o que estava documentado ali na frente dele.

Reescrevi o prompt três vezes. Mesmo resultado.

Na quarta tentativa parei de culpar o prompt e fui olhar para o código.

## O problema estava nos traços

O projeto era antigo, e as docstrings seguiam o estilo NumPy. Faz sentido: quando aprendi Python, o ambiente era científico. NumPy, pandas, scikit-learn. Tudo seguia esse padrão. Copiei sem questionar, como a gente copia muita coisa no começo.

A função que mais me dava problema era essa, uma regra de completude bem típica de pipelines de qualidade de dados:

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

Mas os números eram a parte menos interessante do que estava acontecendo.

## O que está acontecendo por baixo dos panos

O `cl100k_base` é baseado em Byte Pair Encoding, o BPE. Philip Gage descreveu o algoritmo em 1994 e ele foi adaptado para os tokenizadores modernos. A ideia é simples: o tokenizador aprende quais sequências de caracteres aparecem juntas com frequência no corpus de treinamento e as junta em tokens únicos. Na prática, tokenização é compressão estatística orientada por frequência.

E é aí que o estilo NumPy começa a perder.

As linhas `----------` e `-------` são ASCII decorativo. O próprio [numpydoc Style Guide](https://numpydoc.readthedocs.io) admite isso: o formato foi desenhado para legibilidade em terminais de texto, não para densidade de informação. Em termos de tokenização, esse padrão tem um efeito interessante: `---` é um token único no `cl100k_base` (o tokenizador aprendeu esse merge porque sequências de três hífens são comuns em texto), mas `----------` não é. A sequência de dez hífens é fragmentada em grupos — `---`, `---`, `---`, `-` — quatro tokens no lugar de nenhuma informação semântica.

O problema não é que cada hífen vira um token individual. O problema é que sequências longas de hífens não têm merges aprendidos eficientes, e o tokenizador as quebra em pedaços pequenos. Nas duas docstrings acima, as linhas separadoras do estilo NumPy adicionam tokens sem entregar conteúdo semântico nenhum.

O estilo Google evita esse problema por outra razão também. O formato é mais linear, mais próximo da prosa técnica que domina os corpora de treinamento. Tipo e parâmetro ficam juntos: `col_ref (str):` é uma unidade coesa. No estilo NumPy, essa mesma informação está espalhada em linhas separadas — nome na primeira, tipo na segunda, descrição na terceira — o que fragmenta a relação semântica entre eles na janela de contexto.

Uma ressalva importante: isso não é regra absoluta. Em docstrings com tipos muito simples e repetitivos a diferença pode ser menor. O que vale mesmo é que formatos com padrões mais frequentes no corpus comprimem melhor. O estilo Google tende a se encaixar mais nesse critério para a maioria das docstrings de engenharia de dados.

## Por que isso afetou a qualidade das respostas

Custo de tokens é mensurável. Mas o que me surpreendeu mesmo foi a melhora na qualidade das sugestões.

Um estudo de Liu et al. (2023), "Lost in the Middle: How Language Models Use Long Contexts" ([arXiv:2307.03172](https://arxiv.org/abs/2307.03172)), da Stanford University, UC Berkeley e Samaya AI, mostra que a posição e a densidade da informação na janela de contexto afetam diretamente a qualidade das respostas. Quando a informação relevante está dispersa, o modelo performa pior — o desempenho cai significativamente quando ele precisa acessar dados no meio de contextos longos. A fragmentação de tipo, nome e descrição em linhas separadas produz exatamente esse efeito, dentro da própria docstring.

Converti as funções do módulo para o estilo Google, à mão, função por função. Queria entender o que mudava em cada uma, não só executar uma substituição cega.

Voltei com o mesmo pedido de refatoração que tinha falhado antes. O modelo acertou os tipos. Inferiu corretamente os casos de erro. Gerou código consistente com o contrato do módulo sem que eu precisasse explicar esse contrato no prompt.

## O problema em escala

Achei que era um detalhe pontual. Aí fiz a conta para o contexto real de quem trabalha com pipelines de qualidade de dados.

Pensa num catálogo com quatro regras típicas:

```python
rules = [
    calcular_completude,
    validar_unicidade,
    validar_intervalo,
    validar_regex
]
```

Em produção esse catálogo tem dezenas, às vezes centenas de regras. Cada uma com sua docstring. Quando você injeta esse módulo numa janela de contexto — seja para gerar documentação, analisar cobertura ou sugerir novas regras — o conteúdo inteiro entra junto.

A diferença medida foi de 45 tokens por função. Em 100 funções, são 4.500 tokens a mais por chamada. Tokens que poderiam estar sendo usados por lógica de negócio, exemplos de uso ou contexto de domínio.

O impacto em RAG é ainda mais direto. Se você mantém um catálogo de regras com busca semântica — um padrão comum em plataformas de data quality — os embeddings gerados no estilo NumPy carregam mais ruído estrutural. Tokens sem conteúdo semântico contribuem para o vetor como ruído. A representação fica menos fiel ao significado real da função, e a recuperação piora.

Testei isso no próprio módulo: gerei embeddings com as docstrings no estilo NumPy, testei a recuperação, depois gerei de novo no estilo Google. A diferença de precisão foi clara o suficiente para mudar minha decisão de padrão de vez.

## O que ninguém contava quando aprendemos a documentar

Quando aprendi a escrever docstrings, havia um único leitor: o humano que ia manter o código depois de mim.

Esse leitor ainda existe. Mas agora tem outro.

Cada vez que um pipeline de RAG recupera uma função para compor contexto, cada vez que um sistema de geração de código lê o contrato de uma função para sugerir algo coerente, as docstrings são consumidas como dado. O formato que você escolheu lá atrás determina como esse dado vai ser tokenizado, vetorizado e recuperado.

Docstring não é mais só documentação. É payload do seu pipeline de IA.

Esse ponto muda tudo. O estilo NumPy tem beleza visual, é o padrão das bibliotecas científicas que admiro e faz sentido em notebooks. Mas para código que alimenta pipelines de RAG e geração de contexto, o estilo Google não é preferência estética. É uma decisão de engenharia.

## O que eu faria diferente

Instrumentar antes de experimentar.

Saí com evidências qualitativas quando poderia ter saído com métricas. Taxa de acerto de tipo nas sugestões. Número de rejeições manuais. Precisão@K na recuperação vetorial com K fixo. Não defini nenhuma dessas métricas antes de começar, e o aprendizado ficou menos transferível do que poderia ter sido.

Aprendi o resultado. Não aprendi a medir o resultado.

Hoje todo projeto começa com o estilo Google. Não por estética. O estilo NumPy tem uma elegância que o Google não tem. Mas a docstring tem dois leitores agora.

Escrevo para os dois.

## Conclusões

O mecanismo é BPE (Gage, 1994): padrões ASCII decorativos de baixa frequência no corpus — como longas sequências de hífens — não têm merges eficientes aprendidos e são fragmentados em grupos de tokens sem conteúdo semântico.

O estilo Google produz sugestões mais precisas porque agrupa tipo e parâmetro como unidade semântica coesa, reduzindo fragmentação na janela de contexto (Liu et al., 2023, arXiv:2307.03172).

Em pipelines de RAG, embeddings de docstrings no estilo NumPy carregam mais ruído estrutural. Vetores mais ruidosos representam menos fielmente o significado real da função, e a recuperação semântica piora.

Docstring não é mais só documentação. É payload do seu pipeline de IA. Esse realinhamento muda o trade-off entre os dois formatos.

Se você vai experimentar: meça antes. Defina taxa de acerto de tipo, precisão@K, rejeições manuais. Não deixe para depois.

## Referências

- Gage, P. (1994). A New Algorithm for Data Compression. *C Users Journal*, 12(2), 23–38.
- Liu, N. F. et al. (2023). Lost in the Middle: How Language Models Use Long Contexts. [arXiv:2307.03172](https://arxiv.org/abs/2307.03172).
- OpenAI. [How to count tokens with tiktoken](https://cookbook.openai.com/examples/how_to_count_tokens_with_tiktoken). OpenAI Cookbook.
- OpenAI. [tiktoken](https://github.com/openai/tiktoken). GitHub.
- Google. [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html).
- NumPy. [numpydoc Style Guide](https://numpydoc.readthedocs.io).
- Python. [PEP 257 — Docstring Conventions](https://peps.python.org/pep-0257/).
