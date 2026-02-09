"""
PDF Fixture Generator
Generate sample legal PDFs for testing
"""
import os
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor
import io


def create_legal_pdf(filename: str, case_number: str, parties: str, content: str) -> None:
    """
    Create a sample legal PDF with given content
    
    Args:
        filename: Path to save PDF
        case_number: Case number (e.g., "2023-CV-12345")
        parties: Party names (e.g., "Plaintiff v. Defendant")
        content: Body text
    """
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Header
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 50, "LEGAL COMPLAINT")
    
    # Case Info
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 80, f"Case No. {case_number}")
    c.drawString(50, height - 100, f"Parties: {parties}")
    
    # Content
    c.setFont("Helvetica", 10)
    y = height - 130
    line_height = 14
    
    for line in content.split('\n'):
        if y < 50:
            c.showPage()
            y = height - 50
        if line.strip():
            c.drawString(50, y, line.strip()[:80])
            y -= line_height
    
    c.save()
    print(f"Created: {filename}")


def generate_sample_pdfs(output_dir: str) -> None:
    """Generate sample legal PDFs for testing"""
    os.makedirs(output_dir, exist_ok=True)
    
    # PDF 1: Complaint
    create_legal_pdf(
        os.path.join(output_dir, 'complaint.pdf'),
        '2023-CV-12345',
        'ABC Corp v. XYZ Inc.',
        """
        COMPLAINT FOR BREACH OF CONTRACT
        
        Plaintiff ABC Corp brings this action against Defendant XYZ Inc.
        
        FACTS:
        1. This court has jurisdiction over this matter.
        2. Plaintiff entered into service agreement with Defendant on January 15, 2023.
        3. Defendant failed to perform obligations under said agreement.
        4. Plaintiff performed all obligations required under the agreement.
        5. Defendant's breach caused damages of $250,000.
        
        RELIEF REQUESTED:
        Damages in amount of $250,000 plus attorneys fees and costs.
        """
    )
    
    # PDF 2: Discovery Response
    create_legal_pdf(
        os.path.join(output_dir, 'discovery.pdf'),
        '2023-CV-12345',
        'ABC Corp v. XYZ Inc.',
        """
        DISCOVERY RESPONSES
        
        INTERROGATORY 1: Identify all documents related to the service agreement.
        RESPONSE: See attached Exhibit A (documents 1-47).
        
        INTERROGATORY 2: Describe in detail the alleged breach.
        RESPONSE: Defendant failed to deliver services as specified in Paragraph 3
        of the Service Agreement dated January 15, 2023.
        
        INTERROGATORY 3: Calculate damages incurred.
        RESPONSE: Plaintiff incurred $250,000 in damages as calculated in attached
        Exhibit B, including lost revenue and remedial costs.
        """
    )
    
    # PDF 3: Motion
    create_legal_pdf(
        os.path.join(output_dir, 'motion.pdf'),
        '2023-CV-12345',
        'ABC Corp v. XYZ Inc.',
        """
        MOTION FOR SUMMARY JUDGMENT
        
        Plaintiff ABC Corp respectfully submits this Motion for Summary Judgment.
        
        LEGAL STANDARD:
        Under Rule 56, summary judgment is appropriate when the pleadings, 
        affidavits, and other evidence show no genuine dispute of material fact.
        
        ARGUMENT:
        1. Undisputed Facts: The service agreement is authentic and enforceable.
        2. Defendant's breach is clear from the documentary evidence.
        3. Damages are well-documented and calculated.
        
        CONCLUSION:
        There is no genuine dispute of material fact. Plaintiff is entitled to 
        judgment as a matter of law.
        """
    )
    
    # PDF 4: Certification (Expert)
    create_legal_pdf(
        os.path.join(output_dir, 'certification.pdf'),
        '2023-CV-12345',
        'ABC Corp v. XYZ Inc.',
        """
        EXPERT CERTIFICATION
        
        I, Dr. Expert Witness, declare under penalty of perjury:
        
        1. I am qualified to provide expert opinion on industry standards
        regarding technology service delivery.
        
        2. I have reviewed the service agreement and all discovery materials.
        
        3. In my professional opinion, Defendant's performance fell below
        industry standards by approximately 60%.
        
        4. The estimated remedial costs are $250,000.
        
        5. The timeline for remedy is 90 days.
        
        I declare under penalty of perjury that the foregoing is true and correct.
        
        Date: April 15, 2023
        """
    )
    
    print(f"\nGenerated 4 sample PDFs in {output_dir}")


def generate_dismissed_case_pdfs(output_dir: str) -> None:
    """Generate dismissed case PDFs (for reuse testing)"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Dismissed Case Complaint
    create_legal_pdf(
        os.path.join(output_dir, 'dismissed_complaint.pdf'),
        '2022-CV-98765',
        'Big Law Firm v. Original Corp.',
        """
        COMPLAINT FOR FRAUD AND NEGLIGENCE
        
        Plaintiff Big Law Firm brings this action against Original Corp.
        
        FACTS:
        1. Parties entered into business relationship in 2020.
        2. Defendant made false representations about product quality.
        3. Plaintiff relied on said representations and suffered damages.
        4. Actual damages: $500,000
        5. Punitive damages sought: $1,000,000
        
        VIOLATIONS:
        - Actual Fraud (2 causes of action)
        - Negligent Misrepresentation
        - Breach of Fiduciary Duty
        
        RELIEF REQUESTED:
        $500,000 compensatory + $1,000,000 punitive damages.
        """
    )
    
    # Dismissed Case Certification
    create_legal_pdf(
        os.path.join(output_dir, 'dismissed_certification.pdf'),
        '2022-CV-98765',
        'Big Law Firm v. Original Corp.',
        """
        EXPERT CERTIFICATION - DAMAGES ANALYSIS
        
        I declare under penalty of perjury:
        
        1. I have 25 years experience in technology consulting and damages analysis.
        
        2. I reviewed all documents and depositions in this matter.
        
        3. Defendant's misrepresentations caused direct financial losses of $500,000:
           - Lost business opportunity: $300,000
           - Remedial costs: $150,000
           - Investigation costs: $50,000
        
        4. The fraud was intentional based on documented communications.
        
        5. Punitive damages of $1,000,000 are appropriate given the severity.
        
        This certification is 90% reusable for similar cases with comparable damages.
        """
    )
    
    # Dismissed Case Discovery
    create_legal_pdf(
        os.path.join(output_dir, 'dismissed_discovery.pdf'),
        '2022-CV-98765',
        'Big Law Firm v. Original Corp.',
        """
        DISCOVERY MATERIALS - COMMUNICATIONS
        
        EMAIL 1 (Jan 5, 2021):
        "Our product is industry-leading with 99.9% uptime guarantee."
        [SIGNED: VP Sales]
        
        EMAIL 2 (Feb 2, 2021):
        "Upon deployment, we discovered actual uptime was 85%."
        [EVIDENCE OF KNOWLEDGE]
        
        EMAIL 3 (Mar 15, 2021):
        "We are discontinuing this product line."
        [EVIDENCE OF HIDDEN DEFECT]
        
        DOCUMENTS ATTACHED:
        - Service Level Agreement (false)
        - Performance Reports (actual 85% uptime)
        - Internal Emails (showing defendant knowledge)
        
        70% of discovery is reusable for similar fraud cases.
        """
    )
    
    print(f"\nGenerated 3 dismissed case PDFs in {output_dir}")


if __name__ == '__main__':
    # Generate sample PDFs
    sample_dir = os.path.join(
        os.path.dirname(__file__),
        'sample_pdfs'
    )
    dismissed_dir = os.path.join(
        os.path.dirname(__file__),
        'dismissed_cases'
    )
    
    generate_sample_pdfs(sample_dir)
    generate_dismissed_case_pdfs(dismissed_dir)
    
    print("\n✅ All fixtures generated successfully!")
