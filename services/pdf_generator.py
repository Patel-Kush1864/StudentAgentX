import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_notes_pdf(topic, content):
    """
    Compiles generated markdown notes text into a styled PDF document.
    Returns a BytesIO binary buffer ready for Flask download transmission.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=54, leftMargin=54,
                            topMargin=54, bottomMargin=54)
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=15
    )
    
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceAfter=10
    )
    
    heading_style = ParagraphStyle(
        'HeadingStyle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#1e3a8a'),
        spaceBefore=12,
        spaceAfter=6
    )
    
    story = []
    
    # Title
    story.append(Paragraph(f"Study Notes: {topic}", title_style))
    story.append(Spacer(1, 15))
    
    # Parse notes content line by line
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Identify headers/headings
        if line.startswith('1.') or line.startswith('2.') or line.startswith('3.') or line.startswith('4.') or line.startswith('5.') or line.startswith('6.') or line.startswith('**'):
            hdr_text = line.replace('**', '').strip()
            story.append(Paragraph(hdr_text, heading_style))
        else:
            # Bullet point checking
            if line.startswith('*') or line.startswith('-'):
                bullet_text = line.lstrip('* -').strip()
                story.append(Paragraph(f"&bull; {bullet_text}", body_style))
            else:
                story.append(Paragraph(line, body_style))
            
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_resume_pdf(skills, education, projects, ai_resume_content=""):
    """
    Creates a clean, single-page professional resume PDF document layout.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=40, leftMargin=40,
                            topMargin=40, bottomMargin=40)
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'ResTitle',
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=6,
        alignment=1  # Centered
    )
    
    section_title_style = ParagraphStyle(
        'ResSection',
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1e3a8a'),
        spaceBefore=10,
        spaceAfter=4
    )
    
    body_style = ParagraphStyle(
        'ResBody',
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#334155'),
        spaceAfter=6
    )
    
    story = []
    
    story.append(Paragraph("PROFESSIONAL RESUME", title_style))
    story.append(Spacer(1, 10))
    
    # Professional summary
    if ai_resume_content:
        story.append(Paragraph("SUMMARY", section_title_style))
        story.append(Paragraph(ai_resume_content, body_style))
        story.append(Spacer(1, 5))
        
    # Education
    story.append(Paragraph("EDUCATION", section_title_style))
    for edu in education.split('\n'):
        if edu.strip():
            story.append(Paragraph(edu.strip(), body_style))
    story.append(Spacer(1, 5))
    
    # Skills
    story.append(Paragraph("TECHNICAL SKILLS", section_title_style))
    story.append(Paragraph(skills, body_style))
    story.append(Spacer(1, 5))
    
    # Projects
    story.append(Paragraph("ACADEMIC & PERSONAL PROJECTS", section_title_style))
    for proj in projects.split('\n'):
        if proj.strip():
            if proj.strip().startswith('*') or proj.strip().startswith('-'):
                proj_text = proj.strip().lstrip('* -').strip()
                story.append(Paragraph(f"&bull; {proj_text}", body_style))
            else:
                story.append(Paragraph(proj.strip(), body_style))
            
    doc.build(story)
    buffer.seek(0)
    return buffer
