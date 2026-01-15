(() => {
    const data = window.HOLISTIC_DATA;
    if (!data) return;

    const frostData = window.HOLISTIC_FROST || null;

    const zoneSelect = document.getElementById("zoneSelect");
    const stateSelect = document.getElementById("stateSelect");
    const searchInput = document.getElementById("searchInput");
    const chipsWrap = document.getElementById("conditionChips");
    const resultsGrid = document.getElementById("resultsGrid");
    const resultsMeta = document.getElementById("resultsMeta");

    if (!zoneSelect || !chipsWrap || !resultsGrid || !resultsMeta) return;

    // Optional: if you add a tooltip div in the page, this will use it.
    // <div id="mapTooltip" class="map-tooltip" hidden></div>
    const tooltip = document.getElementById("mapTooltip") || null;

    // Optional: state→zone fallback (you can fill this progressively)
    // Prefer storing zones directly on SVG states via data-zone.
    const stateZoneFallback = window.HOLISTIC_STATE_ZONES || {}; // e.g., { "FL": 9, "NJ": 7 }

    const selected = {
        zone: "",
        conditions: new Set(),
        q: "",
        state: ""
    };

    // ------------------------------------------------------------
    // Helpers
    // ------------------------------------------------------------
    function escapeHtml(s) {
        return String(s).replace(/[&<>"']/g, m => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            "\"": "&quot;",
            "'": "&#039;"
        }[m]));
    }

    function getFrostLine(zone) {
        if (!zone || !frostData?.zones) return "";
        const frost = frostData.zones.find(x => String(x.zone) === String(zone));
        if (!frost) return "";
        return `Approx. frost window: last spring ${frost.last_spring_frost} • first fall ${frost.first_fall_frost} (verify locally)`;
    }

    function setSelectedZone(zone, { stateAbbr = "" } = {}) {
        if (zone) {
            zoneSelect.value = zone;
            selected.zone = String(zone);
        } else {
            zoneSelect.value = "";
            selected.zone = "";
        }

        if (stateAbbr) {
            selected.state = stateAbbr;
            if (stateSelect) stateSelect.value = stateAbbr;
        }

        render();
        highlightSelectedState();
    }

    // ------------------------------------------------------------
    // Filter logic
    // ------------------------------------------------------------
    function matchesZone(plant, zone) {
        if (!zone) return true;
        const z = Number(zone);
        const min = Number(plant?.zones?.min);
        const max = Number(plant?.zones?.max);
        if (!Number.isFinite(min) || !Number.isFinite(max)) return true;
        return z >= min && z <= max;
    }

    function matchesConditions(plant) {
        if (selected.conditions.size === 0) return true;
        const tags = plant.tags || [];
        return [...selected.conditions].every(c => tags.includes(c));
    }

    function matchesQuery(plant) {
        const q = (selected.q || "").trim().toLowerCase();
        if (!q) return true;

        const hay = [
            plant.name,
            plant.latin,
            plant.type,
            plant.grow_notes,
            ...(plant.uses || []),
            ...(plant.cautions || []),
            ...(plant.tags || [])
        ]
            .filter(Boolean)
            .join(" ")
            .toLowerCase();

        return hay.includes(q);
    }

    function filterPlants() {
        return (data.plants || []).filter(p =>
            matchesZone(p, selected.zone) &&
            matchesConditions(p) &&
            matchesQuery(p)
        );
    }

    // ------------------------------------------------------------
    // UI: Chips
    // ------------------------------------------------------------
    function buildChips() {
        chipsWrap.innerHTML = "";
        (data.conditions || []).forEach(c => {
            const btn = document.createElement("button");
            btn.type = "button";
            btn.className = "chip";
            btn.dataset.cond = c.id;
            btn.textContent = c.label;

            btn.addEventListener("click", () => {
                if (selected.conditions.has(c.id)) {
                    selected.conditions.delete(c.id);
                    btn.classList.remove("chip--on");
                } else {
                    selected.conditions.add(c.id);
                    btn.classList.add("chip--on");
                }
                render();
            });

            chipsWrap.appendChild(btn);
        });
    }

    // ------------------------------------------------------------
    // Render: Cards + Meta
    // ------------------------------------------------------------
    function plantCard(p) {
        const tags = (p.tags || []).map(t => {
            const label = (data.conditions || []).find(c => c.id === t)?.label || t;
            return `<span class="tag">${escapeHtml(label)}</span>`;
        }).join("");

        const uses = (p.uses || []).map(u => `<li>${escapeHtml(u)}</li>`).join("");
        const cautions = (p.cautions || []).map(c => `<li>${escapeHtml(c)}</li>`).join("");

        return `
      <article class="plant-card">
        <header>
          <h3>${escapeHtml(p.name)} <span class="latin">${escapeHtml(p.latin || "")}</span></h3>
          <p class="meta">
            <span class="pill">Type: ${escapeHtml(p.type || "plant")}</span>
            <span class="pill">Zones: ${p.zones?.min ?? "?"}–${p.zones?.max ?? "?"}</span>
          </p>
        </header>

        <div class="tags">${tags}</div>

        ${p.grow_notes ? `<p class="notes"><strong>Grow:</strong> ${escapeHtml(p.grow_notes)}</p>` : ""}

        ${uses ? `<div><strong>Practical uses</strong><ul>${uses}</ul></div>` : ""}

        ${cautions ? `<div class="cautions"><strong>Cautions</strong><ul>${cautions}</ul></div>` : ""}

        <footer class="smallprint">
          Educational only. Medication changes require clinician collaboration.
        </footer>
      </article>
    `;
    }

    function render() {
        const plants = filterPlants();
        const frostLine = getFrostLine(selected.zone);

        resultsMeta.textContent =
            `${plants.length} plant(s) match` +
            (selected.zone ? ` • zone ${selected.zone}` : "") +
            (selected.conditions.size ? ` • ${selected.conditions.size} condition filter(s)` : "") +
            (frostLine ? ` • ${frostLine}` : "");

        resultsGrid.innerHTML = plants.map(plantCard).join("");

        // Optional: keep the map colored with the currently selected zone scheme
        colorizeMapByZone();
    }

    // ------------------------------------------------------------
    // MAP: Support both <object> SVG and inline SVG
    // ------------------------------------------------------------
    function getMapRoot() {
        // Inline SVG case:
        const inline = document.getElementById("usMapSvg");
        if (inline) return inline;

        // <object> case:
        const obj = document.getElementById("usMapObj");
        if (!obj) return null;
        const svgDoc = obj.contentDocument;
        if (!svgDoc) return null;
        return svgDoc.querySelector("svg");
    }

    function getStateElements(mapRoot) {
        if (!mapRoot) return [];
        return Array.from(mapRoot.querySelectorAll("[data-state], .state, path[id]"));
    }

    function getStateAbbr(el) {
        return el.getAttribute("data-state")
            || el.getAttribute("id")
            || "";
    }

    function getStateZone(el, abbr) {
        const z = el.getAttribute("data-zone") || "";
        if (z) return z;
        if (abbr && stateZoneFallback[abbr]) return String(stateZoneFallback[abbr]);
        return "";
    }

    // Simple, readable discrete zone palette.
    // (No hardcoded “brand colors” — you can theme these via CSS later if desired.)
    function zoneToFill(zone) {
        const z = Number(zone);
        if (!Number.isFinite(z)) return "";
        if (z <= 4) return "#dbeafe";
        if (z <= 6) return "#bbf7d0";
        if (z <= 8) return "#fde68a";
        if (z <= 10) return "#fecaca";
        return "#e9d5ff";
    }

    function colorizeMapByZone() {
        const mapRoot = getMapRoot();
        if (!mapRoot) return;

        const states = getStateElements(mapRoot);
        states.forEach(el => {
            const abbr = getStateAbbr(el);
            if (!abbr || abbr.length > 3) return; // ignore random paths
            const zone = getStateZone(el, abbr);
            const fill = zoneToFill(zone);
            if (fill) el.style.fill = fill;
            el.style.cursor = "pointer";
        });
    }

    function highlightSelectedState() {
        const mapRoot = getMapRoot();
        if (!mapRoot) return;

        // Remove old selection
        mapRoot.querySelectorAll(".state--selected").forEach(n => n.classList.remove("state--selected"));

        if (!selected.state) return;

        const sel = mapRoot.querySelector(`[data-state="${selected.state}"], #${CSS.escape(selected.state)}`);
        if (sel) sel.classList.add("state--selected");
    }

    function wireMap() {
        // For <object> maps, wait for load
        const obj = document.getElementById("usMapObj");
        if (obj) {
            obj.addEventListener("load", () => {
                attachMapHandlers();
            });
        } else {
            // Inline map already in DOM
            attachMapHandlers();
        }
    }

    function attachMapHandlers() {
        const mapRoot = getMapRoot();
        if (!mapRoot) return;

        colorizeMapByZone();

        const states = getStateElements(mapRoot);
        states.forEach(el => {
            const abbr = getStateAbbr(el);
            if (!abbr || abbr.length > 3) return;

            el.addEventListener("click", () => {
                const zone = getStateZone(el, abbr);

                // If the SVG doesn't provide a zone, we still select the state and render
                if (zone) {
                    setSelectedZone(zone, { stateAbbr: abbr });
                } else {
                    selected.state = abbr;
                    if (stateSelect) stateSelect.value = abbr;
                    render();
                    highlightSelectedState();
                }
            });

            if (tooltip) {
                el.addEventListener("mousemove", (e) => {
                    const zone = getStateZone(el, abbr);
                    const frostLine = zone ? getFrostLine(zone) : "";
                    tooltip.hidden = false;
                    tooltip.innerHTML =
                        `<strong>${escapeHtml(abbr)}</strong>` +
                        (zone ? `<div>Zone: ${escapeHtml(zone)}</div>` : "") +
                        (frostLine ? `<div>${escapeHtml(frostLine)}</div>` : "");
                    tooltip.style.left = `${e.pageX + 12}px`;
                    tooltip.style.top = `${e.pageY + 12}px`;
                });
                el.addEventListener("mouseleave", () => {
                    tooltip.hidden = true;
                });
            }
        });
    }

    // ------------------------------------------------------------
    // Events
    // ------------------------------------------------------------
    zoneSelect.addEventListener("change", () => {
        setSelectedZone(zoneSelect.value, { stateAbbr: selected.state });
    });

    stateSelect?.addEventListener("change", () => {
        const opt = stateSelect.selectedOptions?.[0];
        const abbr = stateSelect.value || "";
        if (opt?.dataset?.zone) {
            setSelectedZone(opt.dataset.zone, { stateAbbr: abbr });
        } else {
            selected.state = abbr;
            render();
            highlightSelectedState();
        }
    });

    searchInput?.addEventListener("input", () => {
        selected.q = searchInput.value;
        render();
    });

    // ------------------------------------------------------------
    // Init
    // ------------------------------------------------------------
    buildChips();
    wireMap();
    render();
})();
