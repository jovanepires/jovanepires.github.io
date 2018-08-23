---
title: My page
layout: default
permalink: "teste.html"
---

<div class="row">
  <!-- <div class="col-12">
    <div class="">
      <img src="https://s.gravatar.com/avatar/f78d1158d3624507c05fb43230219ef1?s=100" alt="" class="img-thumbnail">
      <div class="mb-5"></div>
      <h3>Jovane Pires</h3>
      <h5>Desenvolvedor de Software</h5>
      <div class="mb-3"></div>
      <div class="">
        Fortaleza/CE - Brasil
      </div>
      <div class="mb-3"></div>
      <div class=""><a href="#"><i class="far fa-envelope"></i>&nbsp; jovane.amaro.pires@gmail.com</a></div>

      <div class=""><a href="https://github.com/jovanepires" target="_blank" onclick="handleOutboundLinkClicks(this)"><i class="fab fa-github"></i> Github</a></div>
      <div class=""><a href="https://twitter.com/jovanepires" target="_blank" onclick="handleOutboundLinkClicks(this)"><i class="fab fa-twitter"></i> Twitter</a></div>
      <div class=""><a href="https://plus.google.com/+JovaneAmaroPires?rel=author" target="_blank" onclick="handleOutboundLinkClicks(this)"><i class="fab fa-google-plus"></i> Google+</a></div>
    </div>
  </div> -->
  <div class="col-12">
    <div class="mb-5">
      <ul>
        {% for category in site.categories %}
        <div class="catbloc" id="{{ category | first | remove:' ' }}">
         <h2><a href="/categorias/{{ category | first }}.html">{{ category | first }}</a></h2>

         <ul>
            {% for posts in category %}
              {% for post in posts %}
                {% if post.url %}
                 <li>
                   <a href="{{ post.url }}">
                     <time>{{ post.date | date: "%-d %B %Y" }}</time>
                     {{ post.title }}
                   </a>
                 </li>
               {% endif %}
             {% endfor %}
           {% endfor %}
        </ul>
      </div>
        {% endfor %}
      </ul>
    </div>
    <div class="mb-5">
      <ul>
        {% for post in site.posts %}
          <li>
            <div class="FeaturedImgBanner" {% if post.featured-img %} style="background-image: url('{{ post.featured-img }}');" {% endif %}>
              <!-- Include your post title, byline, date, and other info inside the header here. -->
            </div>
            <a href="{{ post.url }}">{{ post.title }}</a>
            {{ post.excerpt }}
          </li>
        {% endfor %}
      </ul>
    </div>

  </div>
</div>
