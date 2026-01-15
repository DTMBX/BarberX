// Symptom-to-Plant Selector Prototype for Holistic Independence Page
(function() {
  if (!window.SYMPTOM_PLANT_MAP) return;
  const data = window.SYMPTOM_PLANT_MAP;
  const container = document.createElement('div');
  container.className = 'symptom-plant-tool';
  container.innerHTML = `
    <h2>🌿 Symptom & Plant Selector (Prototype)</h2>
    <label for="symptomSelect"><strong>Select a symptom or condition:</strong></label>
    <select id="symptomSelect">
      <option value="">-- Choose --</option>
      ${data.map((d, i) => `<option value="${i}">${d.symptom}</option>`).join('')}
    </select>
    <div id="symptomPlantResults" class="symptom-plant-results"></div>
  `;
  // Insert at top of resultsGrid or fallback to body
  const resultsGrid = document.getElementById('resultsGrid');
  if (resultsGrid) {
    resultsGrid.parentNode.insertBefore(container, resultsGrid);
  } else {
    document.body.appendChild(container);
  }
  const select = container.querySelector('#symptomSelect');
  const results = container.querySelector('#symptomPlantResults');
  select.addEventListener('change', function() {
    const idx = this.value;
    if (!idx) { results.innerHTML = ''; return; }
    const entry = data[idx];
    results.innerHTML = `
      <h3>${entry.symptom}</h3>
      <ul>
        ${entry.plants.map(p => `
          <li>
            <strong>${p.name}</strong> (<em>${p.compound}</em>)<br>
            <span>Receptor(s): ${p.receptor && p.receptor.length ? p.receptor.join(', ') : 'N/A'}</span><br>
            <span>Usage: ${p.usage}</span><br>
            <span><strong>Caution:</strong> ${p.caution}</span>
          </li>
        `).join('')}
      </ul>
      <blockquote class="symptom-scripture">${entry.scripture}</blockquote>
    `;
  });
})();
