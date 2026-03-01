/**
 * TillerPro™ Quote Generator
 * Professional quote generation with PDF export, validation, and legal compliance
 *
 * @version 2.0.0
 * @author Tillerstead LLC
 */

(function() {
  'use strict';

  class QuoteGenerator {
    constructor() {
      this.config = window.TillerProConfig;
      this.validator = new QuoteValidator(this.config);
      this.state = window.ProjectState;
      this.quoteNumber = this.generateQuoteNumber();
      this.currentQuote = null;
    }

    /**
     * Generate unique quote number
     */
    generateQuoteNumber() {
      const now = new Date();
      const year = now.getFullYear();
      const month = String(now.getMonth() + 1).padStart(2, '0');
      const day = String(now.getDate()).padStart(2, '0');
      const random = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
      return `Q${year}${month}${day}-${random}`;
    }

    /**
     * Build complete quote from ProjectState
     */
    buildQuote(customerData) {
      const summary = this.state ? this.state.getSummary() : {};
      const materials = this.calculateMaterials(summary);
      const labor = this.calculateLabor(summary);
      const totals = this.calculateTotals(materials, labor);

      return {
        quoteNumber: this.quoteNumber,
        date: new Date().toISOString(),
        expiresAt: this.getExpirationDate(),

        customer: {
          name: customerData.name || '',
          email: customerData.email || '',
          phone: customerData.phone || '',
          address: customerData.address || ''
        },

        project: {
          name: summary.projectName || 'Tile Installation Project',
          description: customerData.projectDescription || '',
          location: customerData.address || '',
          totalArea: summary.totalArea || 0,
          roomCount: summary.roomCount || 1,
          tileType: summary.tileSize || 'Standard',
          complexity: customerData.complexity || 'moderate'
        },

        materials: materials,
        labor: labor,
        totals: totals,

        timeline: {
          estimatedDays: this.estimateProjectDuration(summary.totalArea),
          startAvailability: 'Within 2-3 weeks',
          seasonalNote: this.getSeasonalNote()
        },

        acknowledgments: {},

        notes: customerData.notes || '',

        createdBy: this.config.company.name,
        createdAt: new Date().toISOString()
      };
    }

    /**
     * Calculate materials breakdown
     */
    calculateMaterials(summary) {
      const materials = [];
      const area = summary.totalArea || 0;
      const wasteFactor = 1.10; // 10% waste

      // Tile
      if (summary.tilesNeeded) {
        materials.push({
          item: 'Porcelain Tile',
          quantity: Math.ceil(summary.tilesNeeded * wasteFactor),
          unit: 'pieces',
          unitPrice: 4.50,
          total: Math.ceil(summary.tilesNeeded * wasteFactor) * 4.50,
          category: 'tile'
        });
      }

      // Grout
      if (summary.groutBags) {
        materials.push({
          item: 'Premium Grout',
          quantity: summary.groutBags,
          unit: 'bags',
          unitPrice: 35.00,
          total: summary.groutBags * 35.00,
          category: 'grout'
        });
      }

      // Mortar/Thinset
      const mortarBags = Math.ceil(area / 50); // 50 sqft per bag
      materials.push({
        item: 'Modified Thinset Mortar',
        quantity: mortarBags,
        unit: 'bags',
        unitPrice: 28.00,
        total: mortarBags * 28.00,
        category: 'mortar'
      });

      // Underlayment/Membrane
      if (area > 0) {
        materials.push({
          item: 'Crack Isolation Membrane',
          quantity: Math.ceil(area * 1.05),
          unit: 'sqft',
          unitPrice: 1.20,
          total: Math.ceil(area * 1.05) * 1.20,
          category: 'underlayment'
        });
      }

      // Miscellaneous
      materials.push({
        item: 'Supplies & Miscellaneous',
        quantity: 1,
        unit: 'lot',
        unitPrice: 150.00,
        total: 150.00,
        category: 'misc'
      });

      return materials;
    }

    /**
     * Calculate labor costs
     */
    calculateLabor(summary) {
      const area = summary.totalArea || 0;
      const hourlyRate = 70.00;
      const sqftPerHour = 9; // Typical installation rate
      const hours = Math.ceil(area / sqftPerHour);

      return {
        hours: hours,
        hourlyRate: hourlyRate,
        total: hours * hourlyRate,
        description: 'Professional installation labor',
        breakdown: [
          { task: 'Surface Preparation', hours: Math.ceil(hours * 0.2), rate: hourlyRate },
          { task: 'Tile Installation', hours: Math.ceil(hours * 0.6), rate: hourlyRate },
          { task: 'Grouting & Finishing', hours: Math.ceil(hours * 0.2), rate: hourlyRate }
        ]
      };
    }

    /**
     * Calculate totals with tax and fees
     */
    calculateTotals(materials, labor) {
      const materialsSubtotal = materials.reduce((sum, item) => sum + item.total, 0);
      const laborSubtotal = labor.total;
      const subtotal = materialsSubtotal + laborSubtotal;

      const salesTaxRate = 0.06625; // NJ sales tax
      const salesTax = materialsSubtotal * salesTaxRate; // Only materials are taxed

      const total = subtotal + salesTax;

      return {
        materialsSubtotal: materialsSubtotal,
        laborSubtotal: laborSubtotal,
        subtotal: subtotal,
        salesTax: salesTax,
        salesTaxRate: salesTaxRate,
        total: total,
        deposit: total * 0.30, // 30% deposit
        balanceOnCompletion: total * 0.70
      };
    }

    /**
     * Estimate project duration
     */
    estimateProjectDuration(area) {
      if (area < 100) return 1;
      if (area < 300) return 2;
      if (area < 500) return 3;
      if (area < 800) return 4;
      return Math.ceil(area / 200);
    }

    /**
     * Get quote expiration date
     */
    getExpirationDate() {
      const date = new Date();
      date.setDate(date.getDate() + 30); // Valid for 30 days
      return date.toISOString();
    }

    /**
     * Get seasonal note
     */
    getSeasonalNote() {
      const month = new Date().getMonth();
      if (month >= 11 || month <= 2) {
        return 'Winter scheduling: Projects may require indoor climate control.';
      }
      if (month >= 5 && month <= 8) {
        return 'Summer season: High demand, book early for preferred dates.';
      }
      return null;
    }

    /**
     * Validate quote before generation
     */
    validateQuote(quoteData) {
      return this.validator.validate(quoteData);
    }

    /**
     * Generate PDF quote with legal pages
     */
    async generatePDF(quoteData) {
      // Validate first
      const validation = this.validateQuote(quoteData);
      if (!validation.valid) {
        throw new Error('Quote validation failed: ' + validation.errors.join(', '));
      }

      const { jsPDF } = window.jspdf;
      const doc = new jsPDF();

      // Page 1: Quote Details
      this.renderQuotePage(doc, quoteData);

      // Page 2: Legal Disclaimers
      doc.addPage();
      this.renderDisclaimersPage(doc);

      // Page 3: Contract Terms
      doc.addPage();
      this.renderContractTermsPage(doc);

      // Page 4: Signature Block
      doc.addPage();
      this.renderSignaturePage(doc, quoteData);

      return doc;
    }

    /**
     * Render Quote Details (Page 1)
     */
    renderQuotePage(doc, quote) {
      const company = this.config.company;
      let y = 20;

      // Header
      doc.setFontSize(20);
      doc.setFont('helvetica', 'bold');
      doc.text(company.name, 20, y);

      y += 7;
      doc.setFontSize(10);
      doc.setFont('helvetica', 'normal');
      doc.text(company.tagline, 20, y);

      y += 5;
      doc.setFontSize(9);
      doc.text(`License: ${company.license.number} | Phone: ${company.contact.phone}`, 20, y);

      y += 5;
      doc.text(`Email: ${company.contact.email} | Web: ${company.contact.website}`, 20, y);

      // Quote Number & Date
      y += 10;
      doc.setFontSize(12);
      doc.setFont('helvetica', 'bold');
      doc.text(`QUOTE #${quote.quoteNumber}`, 20, y);

      doc.setFont('helvetica', 'normal');
      doc.setFontSize(9);
      doc.text(`Date: ${new Date(quote.date).toLocaleDateString()}`, 150, y);
      y += 5;
      doc.text(`Expires: ${new Date(quote.expiresAt).toLocaleDateString()}`, 150, y);

      // Customer Info
      y += 10;
      doc.setFontSize(11);
      doc.setFont('helvetica', 'bold');
      doc.text('PREPARED FOR:', 20, y);

      y += 6;
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(10);
      doc.text(quote.customer.name, 20, y);
      y += 5;
      if (quote.customer.address) doc.text(quote.customer.address, 20, y), y += 5;
      doc.text(quote.customer.email, 20, y);
      y += 5;
      doc.text(quote.customer.phone, 20, y);

      // Project Details
      y += 10;
      doc.setFontSize(11);
      doc.setFont('helvetica', 'bold');
      doc.text('PROJECT DETAILS:', 20, y);

      y += 6;
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(10);
      doc.text(`Project: ${quote.project.name}`, 20, y);
      y += 5;
      doc.text(`Area: ${quote.project.totalArea} sq ft`, 20, y);
      y += 5;
      doc.text(`Estimated Duration: ${quote.timeline.estimatedDays} days`, 20, y);

      // Materials Table
      y += 10;
      doc.setFontSize(11);
      doc.setFont('helvetica', 'bold');
      doc.text('MATERIALS:', 20, y);

      y += 8;
      doc.setFontSize(9);
      doc.setFont('helvetica', 'bold');
      doc.text('Item', 20, y);
      doc.text('Qty', 100, y);
      doc.text('Unit Price', 130, y);
      doc.text('Total', 170, y, { align: 'right' });

      y += 1;
      doc.line(20, y, 190, y);
      y += 5;

      doc.setFont('helvetica', 'normal');
      quote.materials.forEach(item => {
        if (y > 250) {
          doc.addPage();
          y = 20;
        }
        doc.text(item.item, 20, y);
        doc.text(`${item.quantity} ${item.unit}`, 100, y);
        doc.text(`$${item.unitPrice.toFixed(2)}`, 130, y);
        doc.text(`$${item.total.toFixed(2)}`, 190, y, { align: 'right' });
        y += 5;
      });

      // Labor
      y += 5;
      doc.setFont('helvetica', 'bold');
      doc.text('LABOR:', 20, y);
      y += 5;

      doc.setFont('helvetica', 'normal');
      doc.text(quote.labor.description, 20, y);
      doc.text(`${quote.labor.hours} hrs @ $${quote.labor.hourlyRate}/hr`, 100, y);
      doc.text(`$${quote.labor.total.toFixed(2)}`, 190, y, { align: 'right' });

      // Totals
      y += 10;
      doc.line(120, y, 190, y);
      y += 6;

      doc.text('Materials Subtotal:', 120, y);
      doc.text(`$${quote.totals.materialsSubtotal.toFixed(2)}`, 190, y, { align: 'right' });
      y += 5;

      doc.text('Labor Subtotal:', 120, y);
      doc.text(`$${quote.totals.laborSubtotal.toFixed(2)}`, 190, y, { align: 'right' });
      y += 5;

      doc.text(`Sales Tax (${(quote.totals.salesTaxRate * 100).toFixed(2)}%):`, 120, y);
      doc.text(`$${quote.totals.salesTax.toFixed(2)}`, 190, y, { align: 'right' });
      y += 7;

      doc.setFont('helvetica', 'bold');
      doc.setFontSize(12);
      doc.text('TOTAL:', 120, y);
      doc.text(`$${quote.totals.total.toFixed(2)}`, 190, y, { align: 'right' });

      // Payment Terms
      y += 10;
      doc.setFontSize(9);
      doc.setFont('helvetica', 'normal');
      doc.text(`Deposit Required (30%): $${quote.totals.deposit.toFixed(2)}`, 120, y);
      y += 5;
      doc.text(`Balance on Completion: $${quote.totals.balanceOnCompletion.toFixed(2)}`, 120, y);

      // Footer
      y = 280;
      doc.setFontSize(8);
      doc.setTextColor(100);
      doc.text('This quote is valid for 30 days. See pages 2-4 for complete terms and conditions.', 105, y, { align: 'center' });
    }

    /**
     * Render Legal Disclaimers (Page 2)
     */
    renderDisclaimersPage(doc) {
      let y = 20;

      doc.setFontSize(14);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(0);
      doc.text('IMPORTANT DISCLAIMERS', 105, y, { align: 'center' });

      y += 10;
      doc.setFontSize(8);
      doc.setFont('helvetica', 'normal');

      const disclaimers = this.config.quote.disclaimers;

      disclaimers.forEach((disclaimer, index) => {
        if (y > 270) {
          doc.addPage();
          y = 20;
        }

        doc.setFont('helvetica', 'bold');
        doc.text(`${index + 1}. ${disclaimer.title}`, 20, y);
        y += 5;

        doc.setFont('helvetica', 'normal');
        const lines = doc.splitTextToSize(disclaimer.text, 170);
        doc.text(lines, 20, y);
        y += (lines.length * 4) + 5;
      });
    }

    /**
     * Render Contract Terms (Page 3)
     */
    renderContractTermsPage(doc) {
      let y = 20;

      doc.setFontSize(14);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(0);
      doc.text('CONTRACT TERMS & CONDITIONS', 105, y, { align: 'center' });

      y += 10;
      doc.setFontSize(8);
      doc.setFont('helvetica', 'normal');

      const terms = this.config.quote.contractTerms;

      terms.forEach((term, index) => {
        if (y > 270) {
          doc.addPage();
          y = 20;
        }

        doc.setFont('helvetica', 'bold');
        doc.text(`${index + 1}. ${term.title}`, 20, y);
        y += 5;

        doc.setFont('helvetica', 'normal');
        const lines = doc.splitTextToSize(term.text, 170);
        doc.text(lines, 20, y);
        y += (lines.length * 4) + 5;
      });
    }

    /**
     * Render Signature Page (Page 4)
     */
    renderSignaturePage(doc, quote) {
      let y = 20;

      doc.setFontSize(14);
      doc.setFont('helvetica', 'bold');
      doc.text('ACCEPTANCE & SIGNATURES', 105, y, { align: 'center' });

      y += 15;
      doc.setFontSize(9);
      doc.setFont('helvetica', 'normal');

      const acknowledgments = this.config.quote.requiredAcknowledgments;

      doc.text('BY SIGNING BELOW, THE CUSTOMER ACKNOWLEDGES:', 20, y);
      y += 8;

      doc.setFontSize(8);
      acknowledgments.forEach((ack, index) => {
        const checkbox = quote.acknowledgments[ack.id] ? '☑' : '☐';
        doc.text(`${checkbox} ${ack.label}`, 25, y);
        y += 6;
      });

      // Signature blocks
      y += 15;
      doc.setFontSize(10);
      doc.setFont('helvetica', 'bold');
      doc.text('CUSTOMER ACCEPTANCE:', 20, y);

      y += 20;
      doc.line(20, y, 90, y);
      y += 5;
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(9);
      doc.text('Customer Signature', 20, y);

      y += 5;
      doc.text(`Print Name: ${quote.customer.name}`, 20, y);

      y += 5;
      doc.text(`Date: _______________`, 20, y);

      // Contractor signature
      y = y - 30;
      doc.setFontSize(10);
      doc.setFont('helvetica', 'bold');
      doc.text('CONTRACTOR:', 120, y);

      y += 20;
      doc.line(120, y, 190, y);
      y += 5;
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(9);
      doc.text('Authorized Representative', 120, y);

      y += 5;
      doc.text(`Company: ${this.config.company.name}`, 120, y);

      y += 5;
      doc.text(`Date: _______________`, 120, y);
    }

    /**
     * Download PDF
     */
    downloadPDF(doc, quoteNumber) {
      doc.save(`TillerPro-Quote-${quoteNumber}.pdf`);
    }

    /**
     * Save quote to localStorage
     */
    saveQuote(quoteData) {
      const quotes = JSON.parse(localStorage.getItem('tillerpro_quotes') || '[]');
      quotes.unshift(quoteData);

      // Keep only last 50 quotes
      if (quotes.length > 50) {
        quotes.splice(50);
      }

      localStorage.setItem('tillerpro_quotes', JSON.stringify(quotes));
    }

    /**
     * Get quote history
     */
    getQuoteHistory() {
      return JSON.parse(localStorage.getItem('tillerpro_quotes') || '[]');
    }
  }

  // Export globally
  window.QuoteGenerator = QuoteGenerator;

})();
