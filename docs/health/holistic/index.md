---

layout: default title: "Holistic Independence Guide" permalink:
/health/holistic/ description: "Filter plants by USDA growing zone and health
goals. Food-first, faith-forward, medically cautious." hero_panel: false
hide_hero: true show_breadcrumbs: true --

<section class="section-block">
  <div class="container">
    <p class="section-eyebrow">Stewardship • Food-first • Accountability</p>
    <h1>Holistic Independence Guide</h1>
    <p class="section-lead">
      Filter plants by USDA growing zone and common health goals. This is educational and collaborative, not medical advice.
    </p>
    <p class="muted">
      <strong>Capacity note:</strong> This is not a directive to stop medication. Any medication changes must be made with a licensed clinician.
    </p>
  </div>
</section>

<section class="section-block">
  <div class="container">

    <div class="holistic-controls">
      <label class="control">
        <span>USDA Zone</span>
        <select id="zoneSelect">
          <option value="">Choose zone…</option>
          {% for z in (site.data.holistic_plants.zones.min..site.data.holistic_plants.zones.max) %}
          <option value="{{ z }}">{{ z }}</option>
          {% endfor %}
        </select>
      </label>

      <label class="control">
        <span>State</span>
        <select id="stateSelect">
          <option value="">(optional) pick state…</option>
          <option value="FL" data-zone="9">Florida (example)</option>
          <!-- Add more states progressively OR wire to an SVG map (recommended). ->
        </select>
      </label>

      <label class="control">
        <span>Search</span>
        <input id="searchInput" type="search" placeholder="turmeric, tea, sleep…" />
      </label>
    </div>

    <div class="holistic-conditions" id="conditionChips"></div>

    <div class="holistic-layout">
      <div class="holistic-map">
        <h2 class="h4">U.S. Growing Map</h2>
        <p class="muted">
          Optional interactive map: add <code>/assets/svg/us-states.svg</code> with state paths that include <code>data-state="FL"</code>, etc.
          Until then, the state selector above works.
        </p>
        <div class="map-shell" id="usMapShell">
          <!-- If you add /assets/svg/us-states.svg, this becomes clickable ->
          <object id="usMapObj" type="image/svg+xml" data="{{ '/assets/svg/us-states.svg' | relative_url }}">
          </object>
        </div>
      </div>

      <div class="holistic-results">
        <div class="results-meta" id="resultsMeta"></div>
        <div class="results-grid" id="resultsGrid"></div>
      </div>
    </div>

    <hr />

    <div class="holistic-links">
      <a class="btn btn-ghost" href="{{ '/docs/health/holistic/guide/' | relative_url }}">Full guide →</a>
      <a class="btn btn-ghost" href="{{ '/docs/health/holistic/appendix-clinicians/' | relative_url }}">Clinician appendix →</a>
      <a class="btn btn-ghost" href="{{ '/docs/health/holistic/conditions/pain-nerve/' | relative_url }}">Pain + nerve subguide →</a>
    </div>

  </div>
</section>

<script>
  window.HOLISTIC_DATA = {{ site.data.holistic_plants | jsonify }};
</script>
<script src="{{ '/assets/js/holistic-filter.js' | relative_url }}"></script>
<link rel="stylesheet" href="{{ '/assets/css/holistic.css' | relative_url }}">
