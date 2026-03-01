# Sq Ft Helper Include Mapping (W×L×H)

Goal: Standardize a single sq-ft helper include and wire it into calculators where a user otherwise has to manually compute area.

## Canonical Include

- Include: `_includes/components/c-sqft-helper.html`
- Purpose: Provide width/length (and optional height) inputs, compute floor area and optionally 4-wall area, then allow pushing that computed value into an existing calculator input.
- Key attributes:
  - `data-sqft-helper`
  - `data-target-floor` / `data-target-wall` (CSS selector for the target input)

## Mapping Table

| Include (current) | Purpose | Used-by | Canonical / New Path | Action |
|---|---|---|---|---|
| `_includes/components/c-sqft-helper.html` | Reusable W×L×(H) sq-ft helper UI | Legacy calculators + cost estimator | `_includes/components/c-sqft-helper.html` | **Canonical** (added) |
| `_includes/tools/tile-calculator.html` | Tile quantity calculator | /tools/legacy/ | Uses `components/c-sqft-helper.html` → `#calc-area` | Wired helper in |
| `_includes/tools/mortar-calculator.html` | Mortar calculator | /tools/legacy/ | Uses `components/c-sqft-helper.html` → `#mortar-area` | Wired helper in |
| `_includes/tools/grout-calculator.html` | Grout calculator | /tools/legacy/ | Uses `components/c-sqft-helper.html` → `#grout-area` | Wired helper in |
| `_includes/tools/leveling-calculator.html` | Leveling calculator | /tools/legacy/ | Uses `components/c-sqft-helper.html` → `#level-area` | Wired helper in |
| `_includes/tools/waterproof-calculator.html` | Waterproof materials calculator | /tools/legacy/ | Uses `components/c-sqft-helper.html` → `#wp-area` | Wired helper in |
| `_includes/tools/labor-calculator.html` | Labor time estimator | /tools/legacy/ | Uses `components/c-sqft-helper.html` → `#labor-area` | Wired helper in |
| `_includes/tools/cost-estimator.html` | Bathroom remodel cost estimator | /tools/legacy/ | Uses `components/c-sqft-helper.html` → `#cost-sqft` (floor) and `#cost-tile-area` (walls) | Wired helper in |

## JS Wiring

- File: `assets/js/tools.js`
- Function: `initSqFtHelpersLegacy()`
- Behavior:
  - Live updates computed floor/wall sq ft outputs.
  - “Use … area” buttons set target input values and dispatch `input`/`change` events.

## Notes

- Height is optional and only enabled where wall-area input is useful (cost estimator; waterproof helper UI). For calculators that only need floor area, height is hidden.
