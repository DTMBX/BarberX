// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

/**
 * Enhanced Holistic Map - Interactive US State Medication & Plant Guide
 * Shows overmedication data, natural alternatives, and plant hardiness zones
 */

(() => {
  // Data from Jekyll
  const plantsData = window.HOLISTIC_DATA;
  const overmedData = window.HOLISTIC_OVERMEDICATION;
  const medicationStates = window.MEDICATION_STATES_DATA;

  if (!plantsData || !medicationStates) {
    console.warn("Required data not loaded");
    return;
  }

  // DOM Elements
  const zoneSelect = document.getElementById("zoneSelect");
  const stateSelect = document.getElementById("stateSelect");
  const searchInput = document.getElementById("searchInput");
  const chipsWrap = document.getElementById("conditionChips");
  const resultsGrid = document.getElementById("resultsGrid");
  const resultsMeta = document.getElementById("resultsMeta");
  const tooltip = document.getElementById("mapTooltip");

  if (!zoneSelect || !resultsGrid || !resultsMeta) return;

  // Selected state
  const selected = {
    zone: "",
    conditions: new Set(),
    q: "",
    state: "",
  };

  // ============================================================
  // HELPERS
  // ============================================================

  function escapeHtml(s) {
    return String(s).replace(
      /[&<>"']/g,
      (m) =>
        ({
          "&": "&amp;",
          "<": "&lt;",
          ">": "&gt;",
          '"': "&quot;",
          "'": "&#039;",
        })[m],
    );
  }

  function getStateData(abbr) {
    if (!medicationStates?.states) return null;
    return medicationStates.states[abbr];
  }

  function getMedicationInfo(medName) {
    if (!overmedData?.top_medicines) return null;
    return overmedData.top_medicines.find((m) =>
      m.name.toLowerCase().includes(medName.toLowerCase()),
    );
  }

  // ============================================================
  // STATE INFO PANEL
  // ============================================================

  function showStateInfo(stateAbbr) {
    const stateData = getStateData(stateAbbr);
    if (!stateData) {
      resultsMeta.innerHTML = `<p>No data available for ${stateAbbr}</p>`;
      return;
    }

    const rxLevel =
      stateData.rx_percentage >= 68
        ? "Very High (Crisis)"
        : stateData.rx_percentage >= 66
          ? "High"
          : stateData.rx_percentage >= 60
            ? "Moderate"
            : "Lower";

    let html = `
            <div class="state-info-panel">
                <div class="state-header">
                    <h3>${escapeHtml(stateData.name)}</h3>
                    <span class="state-zone-badge">Zone ${escapeHtml(stateData.zone)}</span>
                </div>

                <div class="overmedication-stats">
                    <div class="stat-card rx-level-${rxLevel.toLowerCase().replace(/[^a-z]/g, "")}">
                        <span class="stat-label">Prescription Rate</span>
                        <span class="stat-value">${stateData.rx_percentage}%</span>
                        <span class="stat-level">${rxLevel}</span>
                    </div>
                </div>

                <div class="top-medications">
                    <h4>💊 Most Over-Prescribed Medications</h4>
                    <div class="medication-list">
                        ${stateData.top_medications
                          .map((med) => {
                            const medInfo = getMedicationInfo(med);
                            return `
                                <div class="medication-item">
                                    <strong>${escapeHtml(med)}</strong>
                                    ${
                                      medInfo
                                        ? `
                                        <div class="medication-details">
                                            <div class="med-section med-harm">
                                                <strong>⚠️ Health Impact:</strong> ${escapeHtml(medInfo.harm)}
                                            </div>
                                            <div class="med-section med-nature">
                                                <strong>🌿 Natural Origin:</strong> ${escapeHtml(medInfo.nature_lineage)}
                                            </div>
                                            ${
                                              medInfo.supportive_plants
                                                ? `
                                                <div class="med-section med-alternatives">
                                                    <strong>🌱 Garden Alternatives:</strong> 
                                                    ${medInfo.supportive_plants.map((p) => escapeHtml(p)).join(", ")}
                                                </div>
                                            `
                                                : ""
                                            }
                                        </div>
                                    `
                                        : ""
                                    }
                                </div>
                            `;
                          })
                          .join("")}
                    </div>
                </div>

                <div class="featured-plants-section">
                    <h4>🌱 Plants You Can Garden in Zone ${escapeHtml(stateData.zone)}</h4>
                    <div class="featured-plants-grid">
                        ${stateData.featured_plants
                          .map(
                            (plant) => `
                            <div class="plant-item">
                                <span class="plant-icon">🌿</span>
                                <span class="plant-item-text">${escapeHtml(plant)}</span>
                            </div>
                        `,
                          )
                          .join("")}
                    </div>
                </div>

                <div class="state-context">
                    <h4>Healthcare Context</h4>
                    <p>${escapeHtml(stateData.overmedication_notes)}</p>
                    ${
                      stateData.clinician_opportunity
                        ? `
                        <p class="clinician-note">
                            <strong>Opportunity for Clinicians:</strong> 
                            ${escapeHtml(stateData.clinician_opportunity)}
                        </p>
                    `
                        : ""
                    }
                </div>

                <div class="data-sources-mini">
                    <p class="muted small">
                        Data: CDC NHIS, SAMHSA, Kaiser Family Foundation, USDA Plant Hardiness Zones
                    </p>
                </div>
            </div>
        `;

    resultsMeta.innerHTML = html;
  }

  // ============================================================
  // MAP INTERACTION
  // ============================================================

  function getMapRoot() {
    // Inline SVG
    const inline = document.getElementById("usMapSvg");
    if (inline) return inline;

    // <object> embedded SVG
    const obj = document.getElementById("usMapObj");
    if (!obj) return null;
    const svgDoc = obj.contentDocument;
    return svgDoc ? svgDoc.querySelector("svg") : null;
  }

  function getStateElements(mapRoot) {
    if (!mapRoot) return [];
    return Array.from(
      mapRoot.querySelectorAll("[data-state], .state, path[id]"),
    );
  }

  function getStateAbbr(el) {
    return (
      el.getAttribute("data-state") ||
      el.getAttribute("id") ||
      ""
    ).toUpperCase();
  }

  function getMedicationColor(rxPercentage) {
    if (!rxPercentage) return "#e5e7eb"; // gray
    if (rxPercentage >= 68) return "#dc2626"; // red (crisis)
    if (rxPercentage >= 66) return "#f59e0b"; // orange (high)
    if (rxPercentage >= 60) return "#fbbf24"; // yellow (moderate)
    return "#10b981"; // green (lower)
  }

  function colorizeMapByMedication() {
    const mapRoot = getMapRoot();
    if (!mapRoot) return;

    const states = getStateElements(mapRoot);
    states.forEach((el) => {
      const abbr = getStateAbbr(el);
      if (!abbr || abbr.length > 3) return;

      const stateData = getStateData(abbr);
      if (stateData) {
        const color = getMedicationColor(stateData.rx_percentage);
        el.style.fill = color;
        el.style.stroke = "#1f2937";
        el.style.strokeWidth = "0.5";
        el.style.cursor = "pointer";
        el.style.transition = "all 0.2s ease";

        // Add hover effect
        el.addEventListener("mouseenter", () => {
          el.style.stroke = "#000";
          el.style.strokeWidth = "2";
          if (tooltip) {
            tooltip.textContent = `${stateData.name}: ${stateData.rx_percentage}% Rx rate`;
            tooltip.hidden = false;
          }
        });

        el.addEventListener("mouseleave", () => {
          el.style.strokeWidth = "0.5";
          if (tooltip) tooltip.hidden = true;
        });

        el.addEventListener("mousemove", (e) => {
          if (tooltip) {
            tooltip.style.left = `${e.clientX + 10}px`;
            tooltip.style.top = `${e.clientY - 30}px`;
          }
        });
      }
    });
  }

  function highlightSelectedState() {
    const mapRoot = getMapRoot();
    if (!mapRoot) return;

    // Remove old selection
    mapRoot.querySelectorAll(".state--selected").forEach((n) => {
      n.classList.remove("state-selected");
      n.style.stroke = "#1f2937";
      n.style.strokeWidth = "0.5";
    });

    if (!selected.state) return;

    const sel = mapRoot.querySelector(
      `[data-state="${selected.state}"], #${CSS.escape(selected.state)}`,
    );
    if (sel) {
      sel.classList.add("state-selected");
      sel.style.stroke = "#000";
      sel.style.strokeWidth = "3";
    }
  }

  function selectState(abbr) {
    selected.state = abbr;
    const stateData = getStateData(abbr);

    if (stateData && stateData.zone) {
      selected.zone = stateData.zone;
      if (zoneSelect) zoneSelect.value = stateData.zone;
    }

    if (stateSelect) stateSelect.value = abbr;

    showStateInfo(abbr);
    highlightSelectedState();
    renderPlants();
  }

  function wireMap() {
    const obj = document.getElementById("usMapObj");
    if (obj) {
      obj.addEventListener("load", attachMapHandlers);
    } else {
      attachMapHandlers();
    }
  }

  function attachMapHandlers() {
    const mapRoot = getMapRoot();
    if (!mapRoot) return;

    colorizeMapByMedication();

    const states = getStateElements(mapRoot);
    states.forEach((el) => {
      const abbr = getStateAbbr(el);
      if (!abbr || abbr.length > 3) return;

      el.addEventListener("click", () => {
        selectState(abbr);
      });
    });
  }

  // ============================================================
  // PLANT FILTERING & DISPLAY
  // ============================================================

  function matchesZone(plant) {
    if (!selected.zone) return true;
    const z = Number(selected.zone);
    const min = Number(plant?.zones?.min);
    const max = Number(plant?.zones?.max);
    if (!Number.isFinite(min) || !Number.isFinite(max)) return true;
    return z >= min && z <= max;
  }

  function matchesConditions(plant) {
    if (selected.conditions.size === 0) return true;
    const tags = plant.tags || [];
    return [...selected.conditions].every((c) => tags.includes(c));
  }

  function matchesQuery(plant) {
    const q = (selected.q || "").trim().toLowerCase();
    if (!q) return true;

    const searchText = [
      plant.name,
      plant.latin,
      plant.type,
      plant.grow_notes,
      ...(plant.uses || []),
      ...(plant.cautions || []),
      ...(plant.tags || []),
    ]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();

    return searchText.includes(q);
  }

  function renderPlants() {
    const filtered = plantsData.plants.filter(
      (p) => matchesZone(p) && matchesConditions(p) && matchesQuery(p),
    );

    if (filtered.length === 0) {
      resultsGrid.innerHTML =
        '<p class="no-results">No plants match your filters.</p>';
      return;
    }

    resultsGrid.innerHTML = filtered
      .map(
        (plant) => `
            <div class="plant-card">
                <h3 class="plant-name">${escapeHtml(plant.name)}</h3>
                ${plant.latin ? `<p class="plant-latin">${escapeHtml(plant.latin)}</p>` : ""}
                
                <div class="plant-zones">
                    <strong>Zones:</strong> ${plant.zones?.min}-${plant.zones?.max}
                </div>

                ${
                  plant.uses && plant.uses.length
                    ? `
                    <div class="plant-uses">
                        <strong>Uses:</strong>
                        <ul>
                            ${plant.uses.map((use) => `<li>${escapeHtml(use)}</li>`).join("")}
                        </ul>
                    </div>
                `
                    : ""
                }

                ${
                  plant.grow_notes
                    ? `
                    <p class="plant-notes">${escapeHtml(plant.grow_notes)}</p>
                `
                    : ""
                }

                ${
                  plant.cautions && plant.cautions.length
                    ? `
                    <div class="plant-cautions">
                        <strong>⚠ Cautions:</strong>
                        <ul>
                            ${plant.cautions.map((c) => `<li>${escapeHtml(c)}</li>`).join("")}
                        </ul>
                    </div>
                `
                    : ""
                }
            </div>
        `,
      )
      .join("");
  }

  // ============================================================
  // EVENT LISTENERS
  // ============================================================

  if (zoneSelect) {
    zoneSelect.addEventListener("change", (e) => {
      selected.zone = e.target.value;
      renderPlants();
    });
  }

  if (stateSelect) {
    stateSelect.addEventListener("change", (e) => {
      const abbr = e.target.value;
      if (abbr) selectState(abbr);
    });
  }

  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      selected.q = e.target.value;
      renderPlants();
    });
  }

  if (chipsWrap) {
    chipsWrap.addEventListener("click", (e) => {
      const chip = e.target.closest("[data-condition]");
      if (!chip) return;

      const cond = chip.dataset.condition;
      if (selected.conditions.has(cond)) {
        selected.conditions.delete(cond);
        chip.classList.remove("active");
      } else {
        selected.conditions.add(cond);
        chip.classList.add("active");
      }
      renderPlants();
    });
  }

  // ============================================================
  // INITIALIZE
  // ============================================================

  wireMap();
  renderPlants();

  // Show initial message
  if (!selected.state) {
    resultsMeta.innerHTML = `
            <div class="welcome-message">
                <h3>👋 Welcome to the Interactive US Medication & Gardening Guide</h3>
                <p><strong>Click any state on the map above</strong> to discover:</p>
                <ul class="welcome-list">
                    <li>Which medications are most overprescribed in that state</li>
                    <li>The natural botanical origins of those medications</li>
                    <li>Plants you can garden as healthy alternatives</li>
                    <li>Your local hardiness zone and featured crops</li>
                    <li>Healthcare context and opportunities for improvement</li>
                </ul>
                <p style="margin-top: 1.5rem;"><strong>All data verified by:</strong> CDC, SAMHSA, Kaiser Family Foundation, and USDA</p>
            </div>
        `;
  }
})();
