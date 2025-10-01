/**
 * SAMA PROMIS Training Website - Certificate Generator
 * Generates PDF certificates using jsPDF
 */

class CertificateGenerator {
  constructor() {
    this.template = 'standard'; // or 'trainer'
    this.orientation = 'landscape';
    this.format = 'a4';
    this.colors = {
      primary: [30, 58, 138],      // RGB for #1e3a8a
      secondary: [5, 150, 105],    // RGB for #059669
      accent: [245, 158, 11],      // RGB for #f59e0b
      dark: [31, 41, 55],          // RGB for #1f2937
      light: [248, 250, 252]       // RGB for #f8fafc
    };
  }
  
  /**
   * Generate a certificate PDF
   * @param {Object} data - Certificate data
   */
  generate(data) {
    // Check if jsPDF is loaded
    if (typeof window.jspdf === 'undefined') {
      console.error('jsPDF library not loaded');
      alert('Erreur: Bibliothèque PDF non chargée. Veuillez rafraîchir la page.');
      return null;
    }
    
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF({
      orientation: this.orientation,
      unit: 'mm',
      format: this.format
    });
    
    // Page dimensions
    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();
    
    // Add decorative border
    this.addBorder(doc, pageWidth, pageHeight);
    
    // Add header with logo
    this.addHeader(doc, pageWidth);
    
    // Add certificate title
    this.addTitle(doc, pageWidth, data.level);
    
    // Add recipient name
    this.addRecipientName(doc, pageWidth, data.userName);
    
    // Add certification text
    this.addCertificationText(doc, pageWidth, data);
    
    // Add details (date, score, etc.)
    this.addDetails(doc, pageWidth, pageHeight, data);
    
    // Add signatures
    this.addSignatures(doc, pageWidth, pageHeight);
    
    // Add footer
    this.addFooter(doc, pageWidth, pageHeight, data);
    
    // Add QR code for verification
    this.addQRCodePlaceholder(doc, pageWidth, pageHeight, data.certificateId);
    
    return doc;
  }
  
  /**
   * Add decorative border
   */
  addBorder(doc, width, height) {
    // Outer border
    doc.setDrawColor(...this.colors.primary);
    doc.setLineWidth(2);
    doc.rect(10, 10, width - 20, height - 20);
    
    // Inner border
    doc.setLineWidth(0.5);
    doc.rect(12, 12, width - 24, height - 24);
    
    // Decorative corners
    const cornerSize = 15;
    doc.setFillColor(...this.colors.secondary);
    
    // Top-left corner
    doc.triangle(10, 10, 10 + cornerSize, 10, 10, 10 + cornerSize, 'F');
    
    // Top-right corner
    doc.triangle(width - 10, 10, width - 10 - cornerSize, 10, width - 10, 10 + cornerSize, 'F');
    
    // Bottom-left corner
    doc.triangle(10, height - 10, 10 + cornerSize, height - 10, 10, height - 10 - cornerSize, 'F');
    
    // Bottom-right corner
    doc.triangle(width - 10, height - 10, width - 10 - cornerSize, height - 10, width - 10, height - 10 - cornerSize, 'F');
  }
  
  /**
   * Add header section
   */
  addHeader(doc, width) {
    // Organization name
    doc.setFontSize(18);
    doc.setTextColor(...this.colors.primary);
    doc.setFont('helvetica', 'bold');
    doc.text('SAMA PROMIS', width / 2, 25, { align: 'center' });
    
    // Subtitle
    doc.setFontSize(12);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...this.colors.dark);
    doc.text('Centre de Formation et Certification', width / 2, 32, { align: 'center' });
    
    // Decorative line
    doc.setDrawColor(...this.colors.secondary);
    doc.setLineWidth(1);
    doc.line(width / 2 - 40, 35, width / 2 + 40, 35);
  }
  
  /**
   * Add certificate title
   */
  addTitle(doc, width, level) {
    doc.setFontSize(32);
    doc.setTextColor(...this.colors.primary);
    doc.setFont('helvetica', 'bold');
    
    const title = level === 'Formateur' 
      ? 'CERTIFICAT DE FORMATEUR' 
      : 'CERTIFICAT DE FORMATION';
    
    doc.text(title, width / 2, 55, { align: 'center' });
    
    // Decorative underline
    doc.setDrawColor(...this.colors.accent);
    doc.setLineWidth(2);
    const titleWidth = doc.getTextWidth(title);
    doc.line(width / 2 - titleWidth / 2, 58, width / 2 + titleWidth / 2, 58);
  }
  
  /**
   * Add recipient name
   */
  addRecipientName(doc, width, userName) {
    doc.setFontSize(14);
    doc.setTextColor(...this.colors.dark);
    doc.setFont('helvetica', 'normal');
    doc.text('Ce certificat est décerné à', width / 2, 75, { align: 'center' });
    
    // Name with decorative styling
    doc.setFontSize(28);
    doc.setFont('times', 'bolditalic');
    doc.setTextColor(...this.colors.secondary);
    doc.text(userName, width / 2, 88, { align: 'center' });
    
    // Decorative line under name
    doc.setDrawColor(...this.colors.secondary);
    doc.setLineWidth(0.5);
    const nameWidth = doc.getTextWidth(userName);
    doc.line(width / 2 - nameWidth / 2 - 10, 91, width / 2 + nameWidth / 2 + 10, 91);
  }
  
  /**
   * Add certification text
   */
  addCertificationText(doc, width, data) {
    doc.setFontSize(13);
    doc.setTextColor(...this.colors.dark);
    doc.setFont('helvetica', 'normal');
    
    const text = `pour avoir complété avec succès la formation\n${data.role} - Niveau ${data.level}\ndans le cadre du programme SAMA PROMIS`;
    
    const lines = doc.splitTextToSize(text, width - 80);
    let yPos = 105;
    
    lines.forEach(line => {
      doc.text(line, width / 2, yPos, { align: 'center' });
      yPos += 7;
    });
  }
  
  /**
   * Add certificate details
   */
  addDetails(doc, width, height, data) {
    const leftX = 40;
    const rightX = width - 40;
    const y = height - 65;
    
    doc.setFontSize(11);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...this.colors.dark);
    
    // Left side - Date
    doc.text('Date de certification:', leftX, y);
    doc.setFont('helvetica', 'bold');
    doc.text(this.formatDate(data.completionDate), leftX, y + 6);
    
    // Left side - Score
    doc.setFont('helvetica', 'normal');
    doc.text('Score final:', leftX, y + 16);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...this.colors.secondary);
    doc.text(`${data.score}%`, leftX, y + 22);
    
    // Right side - Certificate number
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...this.colors.dark);
    doc.text('Numéro de certificat:', rightX, y, { align: 'right' });
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(10);
    doc.text(data.certificateId, rightX, y + 6, { align: 'right' });
    
    // Right side - Validity
    doc.setFontSize(11);
    doc.setFont('helvetica', 'normal');
    doc.text('Validité:', rightX, y + 16, { align: 'right' });
    doc.setFont('helvetica', 'bold');
    const validUntil = new Date(data.completionDate);
    validUntil.setFullYear(validUntil.getFullYear() + (data.level === 'Formateur' ? 3 : 2));
    doc.text(this.formatDate(validUntil), rightX, y + 22, { align: 'right' });
  }
  
  /**
   * Add signature lines
   */
  addSignatures(doc, width, height) {
    const y = height - 38;
    const leftX = width / 3;
    const rightX = (width / 3) * 2;
    
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...this.colors.dark);
    
    // Left signature line
    doc.setDrawColor(...this.colors.dark);
    doc.setLineWidth(0.5);
    doc.line(leftX - 30, y, leftX + 30, y);
    doc.text('Directeur de Formation', leftX, y + 6, { align: 'center' });
    
    // Right signature line
    doc.line(rightX - 30, y, rightX + 30, y);
    doc.text('Coordinateur SAMA PROMIS', rightX, y + 6, { align: 'center' });
  }
  
  /**
   * Add footer
   */
  addFooter(doc, width, height, data) {
    doc.setFontSize(8);
    doc.setTextColor(100, 100, 100);
    doc.setFont('helvetica', 'italic');
    
    const footer = 'Ce certificat peut être vérifié en ligne sur https://samaetat.sn/promis/verify';
    doc.text(footer, width / 2, height - 18, { align: 'center' });
    
    doc.text(`Généré le ${this.formatDate(new Date())}`, width / 2, height - 13, { align: 'center' });
    
    // License info
    doc.setFontSize(7);
    doc.text('SAMA Transparent State Solutions | LGPL-3 License', width / 2, height - 8, { align: 'center' });
  }
  
  /**
   * Add QR code placeholder
   */
  addQRCodePlaceholder(doc, width, height, certificateId) {
    // Draw a placeholder box for QR code
    const qrSize = 25;
    const qrX = width - 35;
    const qrY = height - 40;
    
    doc.setDrawColor(...this.colors.dark);
    doc.setLineWidth(0.5);
    doc.rect(qrX, qrY, qrSize, qrSize);
    
    // Add text
    doc.setFontSize(6);
    doc.setTextColor(...this.colors.dark);
    doc.text('Scan pour', qrX + qrSize / 2, qrY + qrSize + 3, { align: 'center' });
    doc.text('vérifier', qrX + qrSize / 2, qrY + qrSize + 6, { align: 'center' });
    
    // Note: In production, you would use QRCode.js to generate actual QR code
    // and add it as an image using doc.addImage()
  }
  
  /**
   * Format date to French locale
   */
  formatDate(date) {
    return new Date(date).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }
  
  /**
   * Download certificate
   */
  download(data) {
    const doc = this.generate(data);
    if (!doc) return;
    
    const filename = `SAMA_PROMIS_Certificate_${data.role.replace(/\s+/g, '_')}_${data.level}_${data.certificateId}.pdf`;
    doc.save(filename);
    
    Utils.showNotification('Certificat téléchargé avec succès!', 'success');
  }
  
  /**
   * Print certificate
   */
  print(data) {
    const doc = this.generate(data);
    if (!doc) return;
    
    doc.autoPrint();
    doc.output('dataurlnewwindow');
  }
  
  /**
   * Preview certificate in iframe
   */
  preview(data, containerId) {
    const doc = this.generate(data);
    if (!doc) return;
    
    const pdfData = doc.output('datauristring');
    const container = document.getElementById(containerId);
    
    if (container) {
      container.innerHTML = '';
      const iframe = document.createElement('iframe');
      iframe.src = pdfData;
      iframe.style.width = '100%';
      iframe.style.height = '600px';
      iframe.style.border = 'none';
      iframe.style.borderRadius = '8px';
      iframe.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
      container.appendChild(iframe);
    }
  }
  
  /**
   * Generate sample certificate for preview
   */
  generateSample() {
    const sampleData = {
      userName: 'Exemple Utilisateur',
      role: 'Chef de Projet',
      level: 'Utilisateur',
      completionDate: new Date(),
      score: 95,
      certificateId: 'PROMIS-SAMPLE-' + Math.random().toString(36).substr(2, 9).toUpperCase()
    };
    
    return this.generate(sampleData);
  }
}

// ============================================
// Helper Functions
// ============================================

/**
 * Show certificate preview modal
 */
function showCertificatePreview(userData, role, level) {
  const certificateData = {
    userName: userData.name || 'Utilisateur',
    role: role,
    level: level,
    completionDate: new Date(),
    score: 95, // This should come from actual quiz results
    certificateId: Utils.generateId()
  };
  
  const modalHtml = `
    <div class="modal fade" id="certificatePreviewModal" tabindex="-1">
      <div class="modal-dialog modal-xl modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header bg-promis-primary text-white">
            <h5 class="modal-title">
              <i class="fas fa-certificate me-2"></i>
              Aperçu du Certificat
            </h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div id="certificate-preview-container"></div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-promis-secondary" onclick="certificateGenerator.download(${JSON.stringify(certificateData).replace(/"/g, '&quot;')})">
              <i class="fas fa-download me-2"></i>Télécharger
            </button>
            <button type="button" class="btn btn-promis-primary" onclick="certificateGenerator.print(${JSON.stringify(certificateData).replace(/"/g, '&quot;')})">
              <i class="fas fa-print me-2"></i>Imprimer
            </button>
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fermer</button>
          </div>
        </div>
      </div>
    </div>
  `;
  
  document.body.insertAdjacentHTML('beforeend', modalHtml);
  const modal = new bootstrap.Modal(document.getElementById('certificatePreviewModal'));
  modal.show();
  
  // Generate preview
  const generator = new CertificateGenerator();
  generator.preview(certificateData, 'certificate-preview-container');
  
  // Remove modal from DOM after hiding
  document.getElementById('certificatePreviewModal').addEventListener('hidden.bs.modal', function() {
    this.remove();
  });
}

// ============================================
// Initialize
// ============================================

// Create global instance
const certificateGenerator = new CertificateGenerator();

// Export for use in other scripts
window.CertificateGenerator = CertificateGenerator;
window.certificateGenerator = certificateGenerator;
window.showCertificatePreview = showCertificatePreview;
