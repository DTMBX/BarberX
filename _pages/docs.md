---
layout: default
title: "Evident Documentation"
description: "Complete technical documentation, API references, and guides for the Evident Legal Technologies platform"
permalink: /docs/
badge: "Technical Reference • User Guides • API Docs"
cta_primary: "Quick Start Guide"
cta_primary_url: "#getting-started"
cta_secondary: "API Reference"
cta_secondary_url: "#api"
---

{% include components/heroes/unified-hero.html %}

## Documentation Library

<ul>
  {% assign sorted_docs = site.docs | sort: 'title' %}
  {% for doc in sorted_docs %}
    <li><a href="{{ doc.url | relative_url }}">{{ doc.title | default: doc.slug | default: doc.name }}</a></li>
  {% endfor %}
</ul>
