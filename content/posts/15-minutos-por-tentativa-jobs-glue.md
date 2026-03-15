---
title: "15 minutos por tentativa. Era assim que testávamos jobs Glue."
date: 2024-06-15T00:00:00-03:00
description: "Como uma fixture de pytest mudou o ciclo de desenvolvimento de centenas de squads — sem mudar uma linha de infraestrutura."
image: images/cctv.jpeg
draft: false
tags: ["data-engineering", "aws-glue", "pyspark", "pytest", "unit-testing", "spark", "developer-experience", "engenharia-de-dados"]
---

Você escreve o job. Abre o PR. Espera a pipeline. Espera o deploy na conta de testes. Quinze minutos depois descobre que o schema estava errado.

Corrige. Repete. Mais quinze minutos.

O bug que finalmente forçou a conversa foi ridículo. Um cast errado de string para timestamp. Levamos quase uma hora para descobrir algo que um teste local teria mostrado em segundos. Faça isso cinco vezes numa tarde e você gastou mais de uma hora esperando infraestrutura.

## O problema não era falta de ambiente

Tínhamos tudo: conta AWS dedicada a testes, pipelines configuradas, processo documentado. O problema era outro.

Nosso ambiente de validação era caro demais para ser usado com a frequência que desenvolvimento real exige.

E o efeito colateral silencioso: quando o feedback custa 15 minutos, o engenheiro para de testar incrementalmente. Começa a acumular mudanças para "aproveitar o deploy". O job falha e ninguém sabe qual das cinco alterações causou o problema.

O ambiente de testes existia para dar segurança. Na prática, estava empurrando o time para exatamente o comportamento que queríamos evitar.

## Onde percebemos que o ambiente de testes estava sendo usado errado

Ambiente de testes em nuvem existe para validar integração — permissões, conectividade, dados próximos do real. Não é o lugar certo para validar lógica de transformação.

Para isso, você precisa de segundos. Não de minutos.

A solução foi provisionar uma SparkSession local diretamente no ciclo de testes, usando fixtures do pytest para gerenciar o ciclo de vida da sessão. A fixture sobe o ambiente antes do teste, injeta a sessão como dependência, e derruba tudo ao final.

```python
def test_schema_correto(spark_session) -> None:
    df = spark_session.table("db_saida.tb_resultado")

    assert df.schema == schema_esperado
```

Sem credencial AWS. Sem deploy. Sem espera. O Spark rodou localmente. Executou a transformação com dados sintéticos. O teste respondeu em segundos.

## Por que não simplesmente mockar?

É a pergunta óbvia.

Mock em Spark testa sua simulação, não sua lógica. Um DataFrame mockado não exercita casting implícito de tipos, não valida comportamento de particionamento, não captura os mesmos erros que dados reais produzem. Você descobre isso quando o job passa em todos os testes e falha na primeira execução em produção.

A fixture com Spark local não simula o Spark — executa o Spark. O Hive Metastore é substituído por uma instância Derby embarcada. O filesystem distribuído vira filesystem local. Mas a engine de execução é a mesma.

O teste é mais lento que um mock puro? Sim. Segundos contra milissegundos. Mas segundos ainda são cem vezes mais rápidos que quinze minutos.

## O que quase afundou a adoção

Fazer o Spark rodar localmente foi a parte simples. O ambiente das máquinas dos engenheiros quase não foi.

Paths com espaços e caracteres especiais quebravam a inicialização do Derby com mensagens de erro que não apontavam para a causa real. O Spark reclamava de metastore. O problema era o path do workspace.

Os primeiros squads que toparam com isso eram exatamente os que tinham menos paciência para debugar infraestrutura de teste. O público que mais precisava da ferramenta foi o primeiro a abandoná-la.

Aprendi nesse dia: o produto não é a solução técnica. É a experiência de chegar ao primeiro teste verde. Se o setup tem atrito, a adoção morre antes de começar.

## O que mudou de verdade

Squads que adotaram pararam de usar a conta de testes como ambiente de debug.

O ciclo de quinze minutos não sumiu — foi movido para onde faz sentido. A conta de testes passou a ser acionada quando o job já estava validado localmente. O deploy virou confirmação, não descoberta.

O efeito mais relevante não foi velocidade. Foi confiança. Time que testa incrementalmente encontra bugs menores, mais cedo, com contexto fresco. Time que espera 15 minutos por ciclo acumula mudanças, perde contexto, encontra problemas maiores.

Em escala de milhares de jobs, essa diferença se traduz em incidentes evitados toda semana.

## Takeaways

- Ambiente de testes em nuvem valida integração. Pytest com Spark local valida lógica. São responsabilidades diferentes e merecem ferramentas diferentes.
- Mock em Spark testa simulação. Spark local com dados sintéticos testa comportamento real — com custo de segundos, não de minutos.
- Ciclo de feedback longo muda comportamento: menos testes, mais mudanças acumuladas, bugs maiores e mais difíceis de isolar.
- Setup com atrito mata adoção. A experiência de chegar ao primeiro teste verde é parte do produto.
