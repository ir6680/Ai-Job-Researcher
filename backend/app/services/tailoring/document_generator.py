"""
ATS-Friendly Document Generator for Tailored CVs.
Produces clean, single-column, standard ATS-compliant DOCX and PDF documents.
Follows strict formatting guidelines:
- No graphics, photos, icons, skill bars, or nested tables for core content
- Standard font hierarchy (Calibri / Arial / Helvetica)
- Standard margins (0.75 in / 54 pt)
- Standard section headers (SUMMARY, TECHNICAL SKILLS, EXPERIENCE, PROJECTS, EDUCATION)
"""

import os
from typing import Dict, Any, List
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)


def generate_docx_cv(cv_data: Dict[str, Any], output_path: str) -> str:
    """
    Generate clean, ATS-compliant DOCX file.
    Single column, no tables, standard typography.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = Document()

    # Set 0.75-inch standard margins
    for section in doc.sections:
        section.top_margin = Inches(0.6)
        section.bottom_margin = Inches(0.6)
        section.left_margin = Inches(0.7)
        section.right_margin = Inches(0.7)

    # 1. Header (Name & Contact Info)
    name_para = doc.add_paragraph()
    name_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_name = name_para.add_run(cv_data.get("full_name", "Applicant").upper())
    run_name.bold = True
    run_name.font.size = Pt(18)
    run_name.font.color.rgb = RGBColor(17, 24, 39) # Deep slate

    contact_parts = []
    if cv_data.get("location"):
        contact_parts.append(cv_data["location"])
    if cv_data.get("email"):
        contact_parts.append(cv_data["email"])
    if cv_data.get("phone"):
        contact_parts.append(cv_data["phone"])
    if cv_data.get("linkedin_url"):
        contact_parts.append("LinkedIn")
    if cv_data.get("github_url"):
        contact_parts.append("GitHub")

    contact_para = doc.add_paragraph(" | ".join(contact_parts))
    contact_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    contact_para.paragraph_format.space_after = Pt(10)
    for run in contact_para.runs:
        run.font.size = Pt(9.5)
        run.font.color.rgb = RGBColor(75, 85, 99)

    def add_section_heading(title: str):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(3)
        run = p.add_run(title.upper())
        run.bold = True
        run.font.size = Pt(11)
        run.font.color.rgb = RGBColor(15, 23, 42)

    # 2. Professional Summary
    if cv_data.get("summary"):
        add_section_heading("Professional Summary")
        p = doc.add_paragraph(cv_data["summary"])
        p.paragraph_format.space_after = Pt(6)
        p.runs[0].font.size = Pt(10)

    # 3. Technical Skills
    skills_by_cat = cv_data.get("skills_by_category", {})
    if skills_by_cat:
        add_section_heading("Technical Skills")
        for cat, skills_list in skills_by_cat.items():
            if skills_list:
                p = doc.add_paragraph()
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.space_before = Pt(0)
                run_cat = p.add_run(f"{cat}: ")
                run_cat.bold = True
                run_cat.font.size = Pt(9.5)
                run_skills = p.add_run(", ".join(skills_list))
                run_skills.font.size = Pt(9.5)

    # 4. Relevant Projects
    projects = cv_data.get("projects", [])
    if projects:
        add_section_heading("Key Projects")
        for proj in projects:
            p_title = doc.add_paragraph()
            p_title.paragraph_format.space_before = Pt(4)
            p_title.paragraph_format.space_after = Pt(1)
            
            run_title = p_title.add_run(proj.get("title", ""))
            run_title.bold = True
            run_title.font.size = Pt(10)
            
            if proj.get("technologies"):
                run_tech = p_title.add_run(f" | {', '.join(proj['technologies'])}")
                run_tech.italic = True
                run_tech.font.size = Pt(9)
                run_tech.font.color.rgb = RGBColor(75, 85, 99)

            for bullet in proj.get("highlights", []):
                p_bullet = doc.add_paragraph(bullet, style='List Bullet')
                p_bullet.paragraph_format.space_after = Pt(1)
                p_bullet.paragraph_format.space_before = Pt(0)
                p_bullet.runs[0].font.size = Pt(9.5)

    # 5. Experience
    experiences = cv_data.get("experience", [])
    if experiences:
        add_section_heading("Professional Experience")
        for exp in experiences:
            p_exp = doc.add_paragraph()
            p_exp.paragraph_format.space_before = Pt(4)
            p_exp.paragraph_format.space_after = Pt(1)
            
            run_role = p_exp.add_run(f"{exp.get('role_title', '')} - {exp.get('company_name', '')}")
            run_role.bold = True
            run_role.font.size = Pt(10)

            dates = []
            if exp.get("start_date"):
                dates.append(exp["start_date"])
            dates.append("Present" if exp.get("is_current") else (exp.get("end_date") or ""))
            date_str = " - ".join(d for d in dates if d)
            if date_str:
                run_date = p_exp.add_run(f" ({date_str})")
                run_date.italic = True
                run_date.font.size = Pt(9)
                run_date.font.color.rgb = RGBColor(75, 85, 99)

            for bullet in exp.get("highlights", []):
                p_bullet = doc.add_paragraph(bullet, style='List Bullet')
                p_bullet.paragraph_format.space_after = Pt(1)
                p_bullet.paragraph_format.space_before = Pt(0)
                p_bullet.runs[0].font.size = Pt(9.5)

    # 6. Education
    education = cv_data.get("education", [])
    if education:
        add_section_heading("Education")
        for edu in education:
            p_edu = doc.add_paragraph()
            p_edu.paragraph_format.space_before = Pt(3)
            p_edu.paragraph_format.space_after = Pt(1)
            
            run_degree = p_edu.add_run(f"{edu.get('degree', '')} - {edu.get('institution', '')}")
            run_degree.bold = True
            run_degree.font.size = Pt(9.5)

            if edu.get("location"):
                run_loc = p_edu.add_run(f", {edu['location']}")
                run_loc.font.size = Pt(9)
                run_loc.font.color.rgb = RGBColor(107, 114, 128)

    doc.save(output_path)
    logger.info(f"Generated DOCX tailored CV at: {output_path}")
    return output_path


def generate_pdf_cv(cv_data: Dict[str, Any], output_path: str) -> str:
    """
    Generate clean, ATS-compliant PDF file using ReportLab.
    Single-column, clean typography, strict ATS hierarchy.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=48,
        rightMargin=48,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # Custom Clean Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=18,
        alignment=1, # Center
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=4
    )

    contact_style = ParagraphStyle(
        'ContactLine',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        alignment=1, # Center
        textColor=colors.HexColor('#475569'),
        spaceAfter=8
    )

    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=4
    )

    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        leftIndent=12,
        firstLineIndent=-8,
        textColor=colors.HexColor('#334155'),
        spaceAfter=2
    )

    item_title_style = ParagraphStyle(
        'ItemTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11.5,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=3,
        spaceAfter=1
    )

    story = []

    # 1. Header
    story.append(Paragraph(cv_data.get("full_name", "Applicant").upper(), title_style))
    contact_parts = []
    if cv_data.get("location"):
        contact_parts.append(cv_data["location"])
    if cv_data.get("email"):
        contact_parts.append(cv_data["email"])
    if cv_data.get("phone"):
        contact_parts.append(cv_data["phone"])
    if cv_data.get("linkedin_url"):
        contact_parts.append("LinkedIn")
    if cv_data.get("github_url"):
        contact_parts.append("GitHub")

    story.append(Paragraph(" | ".join(contact_parts), contact_style))
    story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor('#cbd5e1'), spaceBefore=2, spaceAfter=4))

    # Helper for Section Divider
    def add_pdf_section(title: str):
        story.append(Paragraph(title.upper(), heading_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e2e8f0'), spaceBefore=1, spaceAfter=3))

    # 2. Professional Summary
    if cv_data.get("summary"):
        add_pdf_section("Professional Summary")
        story.append(Paragraph(cv_data["summary"], body_style))

    # 3. Technical Skills
    skills_by_cat = cv_data.get("skills_by_category", {})
    if skills_by_cat:
        add_pdf_section("Technical Skills")
        for cat, skills_list in skills_by_cat.items():
            if skills_list:
                line = f"<b>{cat}:</b> {', '.join(skills_list)}"
                story.append(Paragraph(line, body_style))

    # 4. Key Projects
    projects = cv_data.get("projects", [])
    if projects:
        add_pdf_section("Key Projects")
        for proj in projects:
            tech_str = f" <i>| {', '.join(proj.get('technologies', []))}</i>" if proj.get('technologies') else ""
            title_text = f"<b>{proj.get('title', '')}</b>{tech_str}"
            story.append(Paragraph(title_text, item_title_style))
            for bullet in proj.get("highlights", []):
                story.append(Paragraph(f"• {bullet}", bullet_style))

    # 5. Professional Experience
    experiences = cv_data.get("experience", [])
    if experiences:
        add_pdf_section("Professional Experience")
        for exp in experiences:
            dates = []
            if exp.get("start_date"):
                dates.append(exp["start_date"])
            dates.append("Present" if exp.get("is_current") else (exp.get("end_date") or ""))
            date_str = f" <i>({ ' - '.join(d for d in dates if d) })</i>" if dates else ""
            
            title_text = f"<b>{exp.get('role_title', '')}</b> - {exp.get('company_name', '')}{date_str}"
            story.append(Paragraph(title_text, item_title_style))
            for bullet in exp.get("highlights", []):
                story.append(Paragraph(f"• {bullet}", bullet_style))

    # 6. Education
    education = cv_data.get("education", [])
    if education:
        add_pdf_section("Education")
        for edu in education:
            loc_str = f", {edu['location']}" if edu.get("location") else ""
            story.append(Paragraph(f"<b>{edu.get('degree', '')}</b> - {edu.get('institution', '')}{loc_str}", body_style))

    doc.build(story)
    logger.info(f"Generated PDF tailored CV at: {output_path}")
    return output_path
