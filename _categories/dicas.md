---
title: "Dicas"
layout: default
permalink: "/categorias/dicas.html"
categories: [ dicas ]
---

<div class="related">
    <h3>Posts Relacionados</h3>
    {% assign firstCategory = page.categories | first %}
    {% assign relatedCount = 0 %}
    {% for related in site.categories[firstCategory] %}
        {% unless page.permalink == related.permalink %}
            {% assign relatedCount = relatedCount | plus: 1 %}
            <a href="{{related.permalink}}">{{ related.title }}</a>
        {% endunless %}

        {% if relatedCount == 3 %}
            {% break %}
        {% endif %}
    {% endfor %}
</div>
