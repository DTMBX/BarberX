/**
 * Project State Manager
 * Unified state management for Tillerstead Tools Hub
 *
 * Features:
 * - Centralized ProjectState with schema versioning
 * - localStorage persistence with auto-save
 * - Event system for reactive updates
 * - Migration utilities for backward compatibility
 * - Export to PDF/CSV
 *
 * @version 1.0.0
 * @author Tillerstead LLC
 */

(function(window) {
  'use strict';

  const STORAGE_KEY = 'tillerstead_project_state';
  const CURRENT_VERSION = '1.0.0';
  const AUTO_SAVE_DELAY = 2000; // ms

  /**
   * Project State Manager Class
   */
  class ProjectStateManager {
    constructor() {
      this.version = CURRENT_VERSION;
      this.storageKey = STORAGE_KEY;
      this.autoSaveTimer = null;
      this.listeners = {};

      // Load existing state or create new
      this.state = this.load();

      // Auto-save on page unload
      window.addEventListener('beforeunload', () => this.save());
    }

    /**
     * Load state from localStorage with migration
     * @returns {Object} ProjectState
     */
    load() {
      try {
        const stored = localStorage.getItem(this.storageKey);
        if (!stored) return this.createNew();

        const parsed = JSON.parse(stored);

        // Migrate if version mismatch
        if (parsed.version !== this.version) {
          return this.migrate(parsed);
        }

        return parsed;
      } catch (e) {
        console.error('[ProjectState] Failed to load:', e);
        return this.createNew();
      }
    }

    /**
     * Save state to localStorage
     * @returns {boolean} Success
     */
    save() {
      try {
        this.state.updated = new Date().toISOString();
        localStorage.setItem(this.storageKey, JSON.stringify(this.state));
        this.dispatch('save', this.state);
        return true;
      } catch (e) {
        console.error('[ProjectState] Failed to save:', e);

        // Check if quota exceeded
        if (e.name === 'QuotaExceededError') {
          console.warn('[ProjectState] LocalStorage quota exceeded, attempting cleanup...');
          this.cleanupOldData();
          // Retry
          try {
            localStorage.setItem(this.storageKey, JSON.stringify(this.state));
            return true;
          } catch (retryError) {
            console.error('[ProjectState] Retry failed:', retryError);
            return false;
          }
        }
        return false;
      }
    }

    /**
     * Auto-save with debounce
     * @param {number} delay - Delay in ms (default: 2000)
     */
    autoSave(delay = AUTO_SAVE_DELAY) {
      clearTimeout(this.autoSaveTimer);
      this.autoSaveTimer = setTimeout(() => {
        this.save();
      }, delay);
    }

    /**
     * Get value at path
     * @param {string} path - Dot-notation path (e.g., 'project.rooms.0.width')
     * @returns {*} Value at path or undefined
     */
    get(path) {
      if (!path) return this.state;

      return path.split('.').reduce((obj, key) => {
        // Handle array indices
        if (/^\d+$/.test(key)) {
          return Array.isArray(obj) ? obj[parseInt(key)] : undefined;
        }
        return obj?.[key];
      }, this.state);
    }

    /**
     * Set value at path
     * @param {string} path - Dot-notation path
     * @param {*} value - Value to set
     */
    set(path, value) {
      const keys = path.split('.');
      const lastKey = keys.pop();

      // Navigate to parent object
      const parent = keys.reduce((obj, key) => {
        // Handle array indices
        if (/^\d+$/.test(key)) {
          const index = parseInt(key);
          if (!Array.isArray(obj)) {
            throw new Error(`Expected array at ${key}, got ${typeof obj}`);
          }
          if (!obj[index]) obj[index] = {};
          return obj[index];
        }

        // Create object if doesn't exist
        if (!obj[key]) obj[key] = {};
        return obj[key];
      }, this.state);

      // Set value
      parent[lastKey] = value;

      // Trigger events
      this.dispatch('change', { path, value });
      this.autoSave();
    }

    /**
     * Delete value at path
     * @param {string} path - Dot-notation path
     */
    delete(path) {
      const keys = path.split('.');
      const lastKey = keys.pop();
      const parent = this.get(keys.join('.'));

      if (parent) {
        delete parent[lastKey];
        this.dispatch('delete', { path });
        this.autoSave();
      }
    }

    /**
     * Update multiple paths at once (batched)
     * @param {Object} updates - Object with path:value pairs
     */
    update(updates) {
      Object.entries(updates).forEach(([path, value]) => {
        const keys = path.split('.');
        const lastKey = keys.pop();
        const parent = keys.reduce((obj, key) => {
          if (!obj[key]) obj[key] = {};
          return obj[key];
        }, this.state);
        parent[lastKey] = value;
      });

      this.dispatch('batch-update', updates);
      this.autoSave();
    }

    /**
     * Create new project state
     * @returns {Object} New ProjectState
     */
    createNew() {
      const now = new Date().toISOString();
      return {
        version: this.version,
        created: now,
        updated: now,

        project: {
          id: `proj_${Date.now()}`,
          name: 'Untitled Project',
          type: 'bathroom', // bathroom, kitchen, floor, shower
          status: 'planning', // planning, quoted, scheduled, completed
          rooms: []
        },

        tile: {
          size: {},
          material: '',
          finish: '',
          color: '',
          pattern: 'straight',
          wastePercent: 10,
          calculated: {}
        },

        grout: {
          jointWidth: 0.125,
          jointDepth: 0.375,
          type: 'sanded',
          color: '',
          calculated: {}
        },

        mortar: {
          trowelSize: '',
          backButter: false,
          type: 'polymer-modified',
          calculated: {}
        },

        waterproofing: {
          membraneType: 'liquid',
          coats: 2,
          reinforcingBand: true,
          calculated: {}
        },

        slope: {
          drainType: 'center',
          slopeRate: 0.25,
          calculated: {}
        },

        leveling: {
          pourDepth: 0.25,
          primerCoats: 1,
          calculated: {}
        },

        labor: {
          complexity: 'medium',
          additionalWork: [],
          calculated: {}
        },

        budget: {
          materials: {},
          labor: {},
          total: {}
        },

        contact: {
          name: '',
          email: '',
          phone: '',
          address: {},
          preferredContact: 'email',
          timeline: '',
          quoteRequested: false,
          calendlyBooked: false
        },

        exports: [],

        preferences: {
          units: 'imperial',
          currency: 'USD',
          showProTips: true,
          showRetailerLinks: true,
          autoSave: true
        }
      };
    }

    /**
     * Migrate old state to current version
     * @param {Object} oldState - Old state object
     * @returns {Object} Migrated state
     */
    migrate(oldState) {
      const oldVersion = oldState.version || '0.9.0';
      console.log(`[ProjectState] Migrating from ${oldVersion} to ${this.version}`);

      // Migration from pre-unification (0.9.0) to 1.0.0
      if (oldVersion === '0.9.0' || !oldState.version) {
        const newState = this.createNew();

        // Attempt to migrate legacy calculator data
        try {
          // Tile calculator
          const tileData = JSON.parse(localStorage.getItem('tile_calc_data') || '{}');
          if (tileData.tileWidth) {
            newState.tile.size.width = tileData.tileWidth;
            newState.tile.size.length = tileData.tileLength;
            newState.tile.wastePercent = tileData.waste || 10;
          }

          // Grout calculator
          const groutData = JSON.parse(localStorage.getItem('grout_calc_data') || '{}');
          if (groutData.jointWidth) {
            newState.grout.jointWidth = groutData.jointWidth;
            newState.grout.jointDepth = groutData.jointDepth;
            newState.grout.type = groutData.type || 'sanded';
          }

          // Mortar calculator
          const mortarData = JSON.parse(localStorage.getItem('mortar_calc_data') || '{}');
          if (mortarData.trowelSize) {
            newState.mortar.trowelSize = mortarData.trowelSize;
            newState.mortar.backButter = mortarData.backButter || false;
          }

          // Preserve project name if exists
          if (oldState.projectName) {
            newState.project.name = oldState.projectName;
          }
        } catch (e) {
          console.warn('[ProjectState] Legacy data migration failed:', e);
        }

        newState.version = '1.0.0';
        return newState;
      }

      // No migration needed
      return oldState;
    }

    /**
     * Reset to new empty state
     * @param {boolean} confirm - Require confirmation (default: true)
     * @returns {boolean} Success
     */
    reset(confirm = true) {
      if (confirm && !window.confirm('Delete all project data? This cannot be undone.')) {
        return false;
      }

      this.state = this.createNew();
      this.save();
      this.dispatch('reset');
      return true;
    }

    /**
     * Event system: Add listener
     * @param {string} event - Event name
     * @param {Function} callback - Callback function
     */
    on(event, callback) {
      if (!this.listeners[event]) {
        this.listeners[event] = [];
      }
      this.listeners[event].push(callback);
    }

    /**
     * Event system: Remove listener
     * @param {string} event - Event name
     * @param {Function} callback - Callback to remove
     */
    off(event, callback) {
      if (!this.listeners[event]) return;
      this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
    }

    /**
     * Event system: Dispatch event
     * @param {string} event - Event name
     * @param {*} data - Event data
     */
    dispatch(event, data) {
      if (!this.listeners[event]) return;
      this.listeners[event].forEach(callback => {
        try {
          callback(data);
        } catch (e) {
          console.error(`[ProjectState] Event handler error (${event}):`, e);
        }
      });
    }

    /**
     * Export to PDF
     * @returns {Promise<string>} Blob URL
     */
    async exportPDF() {
      // This will integrate with existing pdf-generator.js
      // For now, return a placeholder
      console.log('[ProjectState] Exporting to PDF...');

      // TODO: Integrate with assets/js/pdf-generator.js
      // const doc = await generateProjectPDF(this.state);
      // const blob = doc.output('blob');
      // const url = URL.createObjectURL(blob);

      const url = '#pdf-export-coming-soon';

      this.state.exports.push({
        id: `export_${Date.now()}`,
        type: 'pdf',
        timestamp: new Date().toISOString(),
        url
      });
      this.save();

      return url;
    }

    /**
     * Export to CSV (for GCs)
     * @returns {string} CSV string
     */
    exportCSV() {
      console.log('[ProjectState] Exporting to CSV...');

      // Build material list CSV
      const rows = [
        ['Material', 'Quantity', 'Unit', 'Notes'],
        ['---', '---', '---', '---']
      ];

      // Tile
      if (this.state.tile.calculated.tileCount) {
        rows.push([
          `Tile (${this.state.tile.size.width}x${this.state.tile.size.length}")`,
          this.state.tile.calculated.boxesNeeded || this.state.tile.calculated.tileCount,
          this.state.tile.calculated.boxesNeeded ? 'boxes' : 'pieces',
          `${this.state.tile.wastePercent}% waste included`
        ]);
      }

      // Grout
      if (this.state.grout.calculated.bagsNeeded) {
        rows.push([
          `Grout (${this.state.grout.type})`,
          this.state.grout.calculated.bagsNeeded,
          'bags',
          `${this.state.grout.calculated.lbsPerBag || 25}lb bags`
        ]);
      }

      // Mortar
      if (this.state.mortar.calculated.bagsNeeded) {
        rows.push([
          `Thin-set Mortar (${this.state.mortar.trowelSize})`,
          this.state.mortar.calculated.bagsNeeded,
          'bags',
          this.state.mortar.backButter ? 'Includes back-butter' : ''
        ]);
      }

      // Convert to CSV string
      const csv = rows.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');

      return csv;
    }

    /**
     * Cleanup old data to free space
     */
    cleanupOldData() {
      // Remove old exports (keep last 5)
      if (this.state.exports.length > 5) {
        this.state.exports = this.state.exports.slice(-5);
      }

      // Remove legacy calculator data if exists
      [
        'tile_calc_data',
        'mortar_calc_data',
        'grout_calc_data',
        'waterproof_calc_data',
        'slope_calc_data',
        'leveling_calc_data',
        'labor_calc_data'
      ].forEach(key => {
        localStorage.removeItem(key);
      });
    }

    /**
     * Get project summary stats
     * @returns {Object} Summary statistics
     */
    getSummary() {
      const rooms = this.state.project.rooms || [];
      const totalArea = rooms.reduce((sum, room) => sum + (room.areaFloor || 0), 0);

      return {
        projectName: this.state.project.name,
        projectType: this.state.project.type,
        totalArea,
        roomCount: rooms.length,
        tileCount: this.state.tile.calculated.tileCount || 0,
        boxesNeeded: this.state.tile.calculated.boxesNeeded || 0,
        budgetEstimate: this.state.budget.total.estimate || 0,
        laborDays: this.state.labor.calculated.days || 0,
        completionPercent: this.calculateCompletionPercent()
      };
    }

    /**
     * Calculate project completion percentage
     * @returns {number} Percentage (0-100)
     */
    calculateCompletionPercent() {
      const steps = [
        !!this.state.project.rooms.length,           // 1. Rooms defined
        !!this.state.tile.size.width,                // 2. Tile selected
        !!this.state.tile.calculated.tileCount,      // 3. Tile calculated
        !!this.state.grout.calculated.bagsNeeded,    // 4. Grout calculated
        !!this.state.mortar.calculated.bagsNeeded,   // 5. Mortar calculated
        !!this.state.labor.calculated.hours,         // 6. Labor estimated
        !!this.state.budget.total.estimate,          // 7. Budget calculated
        !!this.state.contact.email                   // 8. Contact provided
      ];

      const completed = steps.filter(Boolean).length;
      return Math.round((completed / steps.length) * 100);
    }
  }

  // Create global instance
  const ProjectState = new ProjectStateManager();

  // Expose to window for global access
  window.ProjectState = ProjectState;

  // Debug helpers (only in development)
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    window.ProjectState.debug = {
      getState: () => ProjectState.state,
      setState: (state) => { ProjectState.state = state; ProjectState.save(); },
      clearState: () => { ProjectState.reset(false); },
      exportJSON: () => JSON.stringify(ProjectState.state, null, 2)
    };
    console.log('[ProjectState] Debug helpers available: ProjectState.debug');
  }

  console.log('[ProjectState] Initialized v' + CURRENT_VERSION);

})(window);
