---
title: "Docstring é input de modelo, e o formato importa"
date: 2026-03-19T00:00:00-03:00
description: "Troquei o formato das minhas docstrings... o modelo parou de alucinar."
image: ""
draft: false
tags: ["ai-engineering", "rag", "tokenizacao", "python", "docstrings", "bpe", "data-quality", "context-window", "engenharia-de-dados"]
--- 

Fui revisitar um projeto antigo de qualidade de dados. Era um módulo que escrevi anos atrás, quando ainda estava aprendendo Python em um contexto mais científico. Tinha funções de completude, unicidade, validação de intervalo. O tipo de código que praticamente todo engenheiro de dados já escreveu várias vezes ao longo da carreira.

Resolvi usar um modelo SLM local para ajudar na refatoração. A ideia parecia boa. Delegar parte do trabalho repetitivo e acelerar ajustes de código.

O problema é que o modelo errava com frequência. Inferia tipos incorretos para os parâmetros, sugeria retornos inconsistentes com o contrato das funções e, em alguns casos, ignorava completamente o que estava descrito na docstring. Reescrevi o prompt algumas vezes tentando guiar melhor o comportamento, mas o resultado continuava praticamente o mesmo.

Na quarta tentativa, ficou claro que o problema não estava apenas no prompt. Fui olhar com mais atenção para o próprio código.

## O problema não era o prompt

O projeto era antigo e as docstrings seguiam o estilo NumPy. Isso fazia sentido no momento em que escrevi o código. Meu contexto era científico, influenciado por bibliotecas como NumPy, pandas e scikit-learn, onde esse padrão é amplamente utilizado. Na época, simplesmente adotei o formato sem questionar.

Uma das funções que mais gerava erro era uma regra simples de completude, bem comum em pipelines de qualidade de dados:

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

Rodei o tiktoken com o `cl100k_base` e contei: **148 tokens**.

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

Dessa vez, a contagem foi de **119 tokens**. A informação era a mesma, mas a estrutura era diferente, resultando em aproximadamente 20% menos tokens.

Mas a contagem era a parte menos interessante do que estava acontecendo.

## Por que o formato muda o que o modelo entende

O `cl100k_base` usa Byte Pair Encoding (BPE). Philip Gage descreveu o algoritmo em 1994, e ele foi adaptado para os tokenizadores modernos. A ideia central é simples: o tokenizador aprende quais sequências de caracteres aparecem juntas com frequência no corpus de treinamento e as une em tokens únicos.

Na prática, tokenização é compressão estatística orientada por frequência.

É aí que o estilo NumPy começa a perder. As linhas `----------` e `-------` são ASCII decorativo. O próprio [numpydoc Style Guide](https://numpydoc.readthedocs.io) admite: o formato foi desenhado para legibilidade em terminal, não para densidade de informação.

Em termos de tokenização, o efeito é esse: `---` é um token único no `cl100k_base`. O tokenizador aprendeu esse merge porque sequências de três hífens são comuns em texto. Mas `----------` não tem merge aprendido para toda a sequência. O tokenizador a quebra em partes: `---`, `---`, `---`, `-`. Quatro tokens no lugar de nenhuma informação semântica.

Tokens sem conteúdo. Espaço desperdiçado.

O estilo Google resolve isso de outra forma também. O formato é mais linear. Tipo e parâmetro ficam na mesma linha: `col_ref (str):` é uma unidade coesa. No estilo NumPy, a mesma informação está espalhada: nome numa linha, tipo na outra, descrição na terceira. A relação semântica entre eles se fragmenta dentro da janela de contexto.

E modelos são sensíveis a isso.

Um estudo de 2023 da Stanford, "Lost in the Middle: How Language Models Use Long Contexts" (arXiv:2307.03172), mostra que a densidade e a posição da informação na janela de contexto afetam diretamente a qualidade das respostas. Quando a informação relevante está dispersa, o modelo performa pior. A fragmentação de tipo, nome e descrição em linhas separadas produz exatamente isso, dentro da própria docstring.

## O problema em escala

Achei que era um detalhe pontual. Aí fiz a conta.

Um catálogo de data quality em produção tem dezenas, às vezes centenas de regras, cada uma com sua docstring. Quando você injeta esse módulo numa janela de contexto para gerar documentação, analisar cobertura ou sugerir novas regras, o conteúdo inteiro entra junto.

A diferença medida foi de cerca de 29 tokens por função. Em 100 funções, são aproximadamente 2.900 tokens a mais por chamada. Tokens que poderiam estar sendo usados por lógica de negócio, exemplos de uso ou contexto de domínio.

O impacto em RAG é ainda mais direto. Se você mantém um catálogo com busca semântica, padrão em plataformas de data quality, os embeddings gerados a partir de docstrings mais verbosas e com ruído estrutural tendem a representar pior o significado real da função. Tokens sem conteúdo semântico competem por espaço no vetor e reduzem a qualidade da representação.

Testei isso no próprio módulo: gerei embeddings com docstrings no estilo NumPy, avaliei a recuperação, depois gerei novamente no estilo Google. A diferença não foi absoluta, mas foi consistente o suficiente para influenciar minha decisão de padrão.

## O leitor que ninguém contou que ia aparecer

Quando aprendi a escrever docstrings, havia um único leitor: o humano que ia manter o código depois de mim.

Esse leitor ainda existe. Mas agora tem outro.

Cada vez que um pipeline de RAG recupera uma função para compor contexto, cada vez que um modelo lê o contrato de uma função para sugerir algo coerente, a docstring é consumida como dado. O formato que você escolheu lá atrás determina como esse dado vai ser tokenizado, vetorizado e recuperado.

Docstring não é mais só documentação. É payload do seu pipeline de IA.

O estilo NumPy tem elegância visual: é o padrão das bibliotecas científicas que admiro, faz sentido em notebooks, em ambientes científicos. Mas para código que alimenta pipelines de RAG e geração de contexto, o estilo Google não é preferência estética.

É uma decisão de engenharia.

## O que eu faria diferente

Se eu fosse repetir esse experimento, começaria instrumentando antes de sair testando. No fim de semana, eu terminei com evidências qualitativas de que algo tinha melhorado, mas poderia ter saído com métricas claras que sustentassem melhor a decisão. Poderia ter acompanhado a taxa de acerto de tipos nas sugestões do modelo, o número de rejeições manuais e até a precisão@K na recuperação vetorial com K fixo.

Como não defini essas métricas antes de começar, o aprendizado ficou menos transferível do que poderia ter sido. Eu sei que o resultado melhorou, mas não tenho uma forma objetiva de medir o quanto melhorou ou de comparar com outros cenários.

No fim, aprendi o resultado, mas não aprendi a medir o resultado.

Hoje, todo projeto novo já começa com docstrings no estilo Google, não por uma questão estética, mas porque, nesse contexto, ele se mostrou mais eficiente. A docstring continua sendo documentação, mas também passou a funcionar como uma interface com o modelo, e isso inevitavelmente muda a forma como eu escrevo.

## Conclusões

- O estilo NumPy gerou 192 tokens contra 147 do estilo Google nas docstrings testadas: 23% a mais, sendo parte desse overhead tokens de separadores que não carregam nenhum conteúdo semântico. A diferença exata varia com o conteúdo, mas a direção é consistente.
- O mecanismo é BPE (Gage, 1994): sequências longas de hífens não têm merges eficientes aprendidos e são fragmentadas em grupos de tokens sem conteúdo. `----------` vira quatro tokens onde havia zero informação.
- O estilo Google produz sugestões mais precisas porque agrupa tipo e parâmetro como unidade semântica coesa, o que reduz a fragmentação que Liu et al. (2023) mostraram afetar o desempenho do modelo em contextos longos.
- Em pipelines de RAG, embeddings de docstrings no estilo NumPy carregam mais ruído estrutural. Vetores mais ruidosos representam menos fielmente o significado real da função, e a recuperação semântica piora.
- Se você vai experimentar: meça antes. Taxa de acerto de tipo, precisão@K, rejeições manuais. Não deixe para depois.

## Referências

- Gage, P. (1994). A New Algorithm for Data Compression. *C Users Journal*, 12(2), 23–38.
- Liu, N. F. et al. (2023). Lost in the Middle: How Language Models Use Long Contexts. [arXiv:2307.03172](https://arxiv.org/abs/2307.03172).
- OpenAI. [How to count tokens with tiktoken](https://cookbook.openai.com/examples/how_to_count_tokens_with_tiktoken). OpenAI Cookbook.
- OpenAI. [tiktoken](https://github.com/openai/tiktoken). GitHub.
- Google. [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html).
- NumPy. [numpydoc Style Guide](https://numpydoc.readthedocs.io).
- Python. [PEP 257: Docstring Conventions](https://peps.python.org/pep-0257/).
