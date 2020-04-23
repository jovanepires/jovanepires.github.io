---
title: "Jovane Pires :: Desenvolvedor de Software"
layout: archive
permalink: "arquivo"
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

    
      {% for post in site.posts %}

        <article id="post-42" class="post-list post-42 post type-post status-publish format-standard has-post-thumbnail hentry category-food-recipe tag-cooking tag-food">
        <div class="post-header">
          <div class="post-meta-date">
            <p> <span>{{ post.date | date: "%-d" }}</span> 
              {% assign m = post.date | date: "%-m" %}
              {% case m %}
                {% when '1' %}JAN
                {% when '2' %}FEV
                {% when '3' %}MAR
                {% when '4' %}ABR
                {% when '5' %}MAI
                {% when '6' %}JUN
                {% when '7' %}JUL
                {% when '8' %}AGO
                {% when '9' %}SET
                {% when '10' %}OUT
                {% when '11' %}NOV
                {% when '12' %}DEZ
              {% endcase %}
              {{ post.date | date: "%Y" }}
            </p>
          </div>
          
          <div class="post-title">
                <h2><a href="{{ post.url }}" rel="bookmark">{{ post.title }}</a></h2>					
                <div class="post-meta">
                  <span>Por</span>
                  <a href="/autor/">@jovanepires</a>
                  <span>, In </span>
                  <a href="https://demo.awaikenthemes.com/blogman/category/food-recipe/" rel="category tag">Food &amp Recipe</a>							
                </div>
          </div>
        </div>
          <div class="post-featured-image">
          <figure>
            <img width="1140" height="468" src="https://demo.awaikenthemes.com/blogman/wp-content/uploads/2018/03/post-12.jpg" class="attachment-full size-full wp-post-image" alt="" srcset="https://demo.awaikenthemes.com/blogman/wp-content/uploads/2018/03/post-12.jpg 1140w, https://demo.awaikenthemes.com/blogman/wp-content/uploads/2018/03/post-12-768x315.jpg 768w" sizes="(max-width: 1140px) 100vw, 1140px">		</figure>
        </div>
        <div class="post-body">
                <p>{{ post.excerpt }}</p>
            </div>
        
          
        
        <div class="post-footer">
          <a href="{{ post.url }}" class="btn-read-more">Leia mais... <i class="fas fa-arrow-right"></i></a>
        </div>
      </article>
        
      {% endfor %}
    

  </div>
</div>
