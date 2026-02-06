---

layout: default
title: "FAQ"
permalink: /faq/
--

{% capture faq_content %}
{% include faq.md %}
{% endcapture %}

{{ faq_content | markdownify }}
