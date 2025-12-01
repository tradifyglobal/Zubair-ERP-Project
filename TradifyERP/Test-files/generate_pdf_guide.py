#!/usr/bin/env python
"""
Generate a comprehensive PDF guide for Leads & Lead Sources
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from datetime import datetime

# Create PDF
pdf_path = 'LEADS_LEAD_SOURCES_Usage_Guide.pdf'
doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=0.5*inch, leftMargin=0.5*inch,
                        topMargin=0.5*inch, bottomMargin=0.5*inch)

# Container for PDF elements
elements = []

# Get base styles
styles = getSampleStyleSheet()

# Define custom styles
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=24,
    textColor=colors.HexColor('#1f4788'),
    spaceAfter=6,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold'
)

heading_style = ParagraphStyle(
    'CustomHeading',
    parent=styles['Heading2'],
    fontSize=14,
    textColor=colors.HexColor('#2e5c9a'),
    spaceAfter=12,
    spaceBefore=12,
    fontName='Helvetica-Bold'
)

subheading_style = ParagraphStyle(
    'CustomSubHeading',
    parent=styles['Heading3'],
    fontSize=11,
    textColor=colors.HexColor('#3d6bb3'),
    spaceAfter=8,
    spaceBefore=6,
    fontName='Helvetica-Bold'
)

normal_style = ParagraphStyle(
    'CustomNormal',
    parent=styles['BodyText'],
    fontSize=10,
    alignment=TA_JUSTIFY,
    spaceAfter=6
)

# Title Page
elements.append(Spacer(1, 1*inch))
elements.append(Paragraph("LEADS & LEAD SOURCES", title_style))
elements.append(Spacer(1, 0.2*inch))
elements.append(Paragraph("Complete Usage Guide", ParagraphStyle(
    'Subtitle', parent=styles['Normal'], fontSize=16, alignment=TA_CENTER, 
    textColor=colors.HexColor('#555555')
)))
elements.append(Spacer(1, 0.5*inch))
elements.append(Paragraph(f"TradifyERP CRM Module", normal_style))
elements.append(Paragraph(f"Version 1.0 | {datetime.now().strftime('%B %d, %Y')}", normal_style))
elements.append(Spacer(1, 0.5*inch))

# Table of Contents
elements.append(PageBreak())
elements.append(Paragraph("TABLE OF CONTENTS", heading_style))
toc_items = [
    "1. What is a Lead?",
    "2. What is a Lead Source?",
    "3. Lead Lifecycle - Step by Step",
    "4. Real-World Examples",
    "5. Lead Scoring",
    "6. Key Business Use Cases",
    "7. Lead Status Workflow",
    "8. Lead Fields Reference",
    "9. Lead vs. Opportunity vs. Contact",
    "10. Practical Dashboard Metrics",
    "11. Quick Reference Guide"
]

for item in toc_items:
    elements.append(Paragraph(item, normal_style))

elements.append(PageBreak())

# Section 1: What is a Lead
elements.append(Paragraph("1. WHAT IS A LEAD?", heading_style))
elements.append(Paragraph(
    "A <b>Lead</b> is a <b>prospective customer</b> that has shown interest in your products/services but hasn't yet become a paying customer.",
    normal_style
))
elements.append(Spacer(1, 0.2*inch))
elements.append(Paragraph("Typical Lead Workflow:", subheading_style))
elements.append(Paragraph(
    "Prospect → LEAD (Interest Shown) → QUALIFIED → OPPORTUNITY → CUSTOMER",
    ParagraphStyle('Workflow', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER, 
                   textColor=colors.HexColor('#444444'), fontName='Helvetica-Bold')
))
elements.append(Spacer(1, 0.2*inch))

elements.append(Paragraph("Key Information Stored in a Lead:", subheading_style))
lead_info = [
    "<b>Identification:</b> Name, Email, Phone, Company",
    "<b>Status:</b> NEW → CONTACTED → QUALIFIED → PROPOSAL SENT → CONVERTED/LOST",
    "<b>Lead Score:</b> 0-100 rating of how qualified the lead is",
    "<b>Source:</b> Where the lead came from (Website, Email, Referral, etc.)",
    "<b>Assignment:</b> Which salesperson owns this lead",
    "<b>Dates:</b> Created, Last Contact, Qualified date",
    "<b>Value:</b> Estimated deal size if converted"
]

for info in lead_info:
    elements.append(Paragraph(info, normal_style))

elements.append(PageBreak())

# Section 2: What is a Lead Source
elements.append(Paragraph("2. WHAT IS A LEAD SOURCE?", heading_style))
elements.append(Paragraph(
    "A <b>Lead Source</b> is the <b>channel/origin</b> where a lead came from. It answers: \"How did this person find us?\"",
    normal_style
))
elements.append(Spacer(1, 0.2*inch))

# Lead Sources Table
elements.append(Paragraph("Your Available Lead Sources:", subheading_style))
source_data = [
    ["Code", "Name", "Example Usage"],
    ["WEB", "Website", "Contact form submission on your website"],
    ["REF", "Referral", "Existing customer recommended your company"],
    ["CALL", "Cold Call", "Your sales team called them"],
    ["EMAIL", "Email Campaign", "Marketing sent them a campaign email"],
    ["SHOW", "Trade Show", "They visited your booth at an event"],
    ["SOCIAL", "Social Media", "They found you via LinkedIn, Facebook, Instagram"],
    ["ADV", "Advertisement", "Google Ads, Facebook Ads, paid advertising"],
    ["INBOUND", "Inbound Inquiry", "They called or messaged you directly"],
    ["OTHER", "Other", "Doesn't fit the above categories"]
]

source_table = Table(source_data, colWidths=[1*inch, 1.5*inch, 2.5*inch])
source_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e5c9a')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 9),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 1), (-1, -1), 9),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
]))

elements.append(source_table)
elements.append(PageBreak())

# Section 3: Lead Lifecycle
elements.append(Paragraph("3. LEAD LIFECYCLE - STEP BY STEP", heading_style))

lifecycle_stages = [
    {
        "title": "Stage 1: LEAD CREATED (NEW)",
        "content": [
            "<b>Action:</b> Someone shows interest in your business",
            "<b>Status:</b> NEW",
            "<b>Who:</b> Salesperson or marketing person creates lead",
            "<b>Data:</b> Name, Email, Phone, Company, Lead Source",
            "<b>Example:</b> \"John from ACME Inc visited our website - WEB source\""
        ]
    },
    {
        "title": "Stage 2: LEAD CONTACTED",
        "content": [
            "<b>Status:</b> CONTACTED",
            "<b>Action:</b> Salesperson reaches out to the lead",
            "<b>Update:</b> last_contact_date is recorded",
            "<b>Example:</b> \"Called John to understand his requirements\""
        ]
    },
    {
        "title": "Stage 3: LEAD QUALIFIED",
        "content": [
            "<b>Status:</b> QUALIFIED",
            "<b>Action:</b> Lead meets your criteria (budget, authority, need, timing)",
            "<b>Data:</b> lead_score increases, qualified_date recorded",
            "<b>Example:</b> \"John confirmed: budget $50K, decision in Jan 2026\""
        ]
    },
    {
        "title": "Stage 4: PROPOSAL SENT",
        "content": [
            "<b>Status:</b> PROPOSAL SENT",
            "<b>Action:</b> Send formal proposal/quote to lead",
            "<b>Data:</b> estimated_deal_size = $50,000",
            "<b>Example:</b> \"Sent proposal to John for $50K contract\""
        ]
    },
    {
        "title": "Stage 5: CONVERTED or LOST",
        "content": [
            "<b>✅ CONVERTED:</b> Lead becomes a paying customer",
            "   → Move to Opportunity/Customer module",
            "   → Track as closed-won deal",
            "",
            "<b>❌ LOST:</b> Lead decided not to proceed",
            "   → Reason documented in notes",
            "   → Can reopen later if they re-engage"
        ]
    }
]

for stage in lifecycle_stages:
    elements.append(Paragraph(stage["title"], subheading_style))
    for line in stage["content"]:
        if line == "":
            elements.append(Spacer(1, 0.1*inch))
        else:
            elements.append(Paragraph(line, normal_style))
    elements.append(Spacer(1, 0.15*inch))

elements.append(PageBreak())

# Section 4: Real-World Examples
elements.append(Paragraph("4. REAL-WORLD EXAMPLES", heading_style))

examples = [
    {
        "title": "Example 1: Website Lead",
        "steps": [
            "Website visitor fills contact form",
            "↓",
            "System creates Lead:",
            "  • lead_name: \"Sarah Johnson\"",
            "  • company_name: \"Tech Solutions Inc\"",
            "  • email: sarah@techsol.com",
            "  • source: LeadSource(code='WEB', name='Website')",
            "  • status: NEW",
            "  • lead_score: 50",
            "  • assigned_to: \"John Smith\" (Salesperson)",
            "",
            "Day 1: Sales team contacts Sarah",
            "  • status: CONTACTED",
            "  • last_contact_date: 2025-11-24",
            "  • notes: \"Sarah interested in licensing product\"",
            "",
            "Day 3: Sarah confirms requirements",
            "  • status: QUALIFIED",
            "  • lead_score: 85",
            "  • estimated_deal_size: $75,000",
            "  • qualified_date: 2025-11-26",
            "",
            "Day 5: Send proposal",
            "  • status: PROPOSAL_SENT",
            "",
            "Day 10: Contract signed",
            "  • status: CONVERTED",
            "  • Move to Opportunity module as Closed-Won deal"
        ]
    },
    {
        "title": "Example 2: Referral Lead",
        "steps": [
            "Existing customer \"ACME Corp\" refers \"Global Industries\"",
            "↓",
            "Sales team creates Lead:",
            "  • lead_name: \"Mike Chen\"",
            "  • company_name: \"Global Industries\"",
            "  • source: LeadSource(code='REF', name='Referral')",
            "  • notes: \"Referred by ACME Corp - strong fit\"",
            "  • lead_score: 90 (referrals often highly qualified)",
            "  • status: CONTACTED (sales team reached out via existing customer)",
            "",
            "Result: Higher conversion rate because it's a warm lead"
        ]
    }
]

for example in examples:
    elements.append(Paragraph(example["title"], subheading_style))
    for step in example["steps"]:
        if step.startswith("  •"):
            elements.append(Paragraph("&nbsp;&nbsp;&nbsp;" + step[4:], normal_style))
        elif step.startswith("  "):
            elements.append(Paragraph("&nbsp;" + step, normal_style))
        else:
            elements.append(Paragraph(step, normal_style))
    elements.append(Spacer(1, 0.2*inch))

elements.append(PageBreak())

# Section 5: Lead Scoring
elements.append(Paragraph("5. LEAD SCORING - HOW GOOD IS THIS LEAD?", heading_style))
elements.append(Paragraph("<b>Lead Score: 0-100</b>", subheading_style))

scoring_levels = [
    ("<b>0-30:</b> \"Cold\"", "Not ready to buy → Nurture with content, emails"),
    ("<b>30-60:</b> \"Warm\"", "Showing interest → Have conversation, understand needs"),
    ("<b>60-80:</b> \"Hot\"", "Actively interested → Move to QUALIFIED status, Create proposal"),
    ("<b>80-100:</b> \"Blazing\"", "Ready to buy NOW → Priority follow-up, Handle by senior salesperson")
]

score_data = [["Score Range", "Status", "Action"]]
for level, action in scoring_levels:
    score_data.append([level, "", action])

score_table = Table(score_data, colWidths=[1.5*inch, 1.5*inch, 2*inch])
score_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e5c9a')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 1), (-1, -1), 9),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')])
]))

elements.append(score_table)
elements.append(Spacer(1, 0.2*inch))

elements.append(Paragraph("How Scores Change:", subheading_style))
score_changes = [
    "• Opens marketing email? <b>+5 points</b>",
    "• Visits product page? <b>+10 points</b>",
    "• Downloads whitepaper? <b>+15 points</b>",
    "• Attends webinar? <b>+20 points</b>",
    "• Requests demo? <b>+25 points</b>",
    "• Days since contact? <b>-2 points per week</b> (stale leads lose points)"
]

for change in score_changes:
    elements.append(Paragraph(change, normal_style))

elements.append(PageBreak())

# Section 6: Key Business Use Cases
elements.append(Paragraph("6. KEY BUSINESS USE CASES", heading_style))

use_cases = [
    {
        "title": "Use Case 1: Track Sales Performance",
        "desc": "Question: \"Which salesperson converts the most leads?\"",
        "result": "Shows productivity of each salesperson"
    },
    {
        "title": "Use Case 2: Measure Channel Effectiveness",
        "desc": "Question: \"Which lead source generates best customers?\"",
        "result": "Website: 100 leads, 25 converted (25%)<br/>Referral: 20 leads, 15 converted (75%) ← BEST!<br/>Cold Call: 50 leads, 5 converted (10%)"
    },
    {
        "title": "Use Case 3: Calculate Revenue Impact",
        "desc": "Question: \"How much revenue comes from each source?\"",
        "result": "Website: $750,000 | Referral: $450,000 | Cold Call: $200,000"
    },
    {
        "title": "Use Case 4: Identify Stale Leads",
        "desc": "Question: \"Which leads haven't been contacted in 30+ days?\"",
        "result": "Follow up on these leads or re-assign"
    },
    {
        "title": "Use Case 5: Lead Distribution",
        "desc": "Question: \"Distribute 50 new leads fairly among 5 salespeople\"",
        "result": "Assigns 10 leads to each person based on current workload"
    }
]

for i, case in enumerate(use_cases, 1):
    elements.append(Paragraph(case["title"], subheading_style))
    elements.append(Paragraph(case["desc"], normal_style))
    elements.append(Paragraph("<b>Result:</b> " + case["result"], normal_style))
    elements.append(Spacer(1, 0.15*inch))

elements.append(PageBreak())

# Section 7: Lead Status Workflow
elements.append(Paragraph("7. LEAD STATUS WORKFLOW", heading_style))

workflow_text = """
<b>┌─────────────────────────────────────────────────────┐</b><br/>
<b>│                    LEAD LIFECYCLE                    │</b><br/>
<b>└─────────────────────────────────────────────────────┘</b><br/>
<br/>
&nbsp;&nbsp;&nbsp;&nbsp;NEW (Created)<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↓<br/>
&nbsp;&nbsp;&nbsp;&nbsp;CONTACTED (Salesperson reached out)<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↓<br/>
&nbsp;&nbsp;&nbsp;&nbsp;QUALIFIED (Meets criteria)<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↓<br/>
&nbsp;&nbsp;&nbsp;&nbsp;PROPOSAL SENT (Quote delivered)<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├──→ <b>✅ CONVERTED</b> (Became a customer!)<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└──→ Move to Opportunity/Customer<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└──→ <b>❌ LOST</b> (They said no)<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└──→ Move to Lost Deals report<br/>
"""

elements.append(Paragraph(workflow_text, normal_style))

elements.append(PageBreak())

# Section 8: Lead Fields Reference
elements.append(Paragraph("8. LEAD FIELDS REFERENCE", heading_style))

fields_data = [
    ["Field Name", "Purpose"],
    ["lead_number", "Unique ID (AUTO-GENERATED)"],
    ["lead_name", "Contact person name"],
    ["company_name", "Company/organization name"],
    ["email", "Contact email address"],
    ["phone", "Contact phone number"],
    ["address", "Full mailing address"],
    ["status", "Current lead stage (NEW, CONTACTED, QUALIFIED, etc.)"],
    ["source", "Where lead came from (Website, Referral, etc.)"],
    ["lead_score", "0-100 quality rating"],
    ["estimated_deal_size", "Potential deal value if converted"],
    ["assigned_to", "Sales rep owner of this lead"],
    ["created_date", "When lead was created"],
    ["last_contact_date", "Last interaction date"],
    ["qualified_date", "When lead became qualified"],
    ["notes", "Internal comments/observations"]
]

fields_table = Table(fields_data, colWidths=[2*inch, 3.5*inch])
fields_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e5c9a')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 9),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 1), (-1, -1), 8),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')])
]))

elements.append(fields_table)

elements.append(PageBreak())

# Section 9: Lead vs Opportunity vs Contact
elements.append(Paragraph("9. LEAD vs. OPPORTUNITY vs. CONTACT", heading_style))

comparison_text = """
<b>LEAD:</b><br/>
• Unknown/new prospect<br/>
• No established relationship<br/>
• Status: NEW → CONTACTED → QUALIFIED<br/>
• Example: \"John from website form\"<br/>
<br/>
<b>CONTACT:</b><br/>
• Known person in target company<br/>
• Existing relationship<br/>
• Can be: decision maker, influencer, etc.<br/>
• Linked to Account/Company<br/>
• Example: \"John Smith - VP at ACME Corp\"<br/>
<br/>
<b>OPPORTUNITY:</b><br/>
• Qualified lead ready to become customer<br/>
• Has deal size, probability, close date<br/>
• Status: Proposal → Negotiation → Won/Lost<br/>
• Example: \"$50K licensing deal with ACME\"<br/>
<br/>
<b>PROGRESSION FLOW:</b><br/>
Lead (NEW) → Contact (relationship) → Opportunity (deal) → Customer
"""

elements.append(Paragraph(comparison_text, normal_style))

elements.append(PageBreak())

# Section 10: Dashboard Metrics
elements.append(Paragraph("10. PRACTICAL DASHBOARD METRICS", heading_style))

dashboard_text = """
<b>Sales Manager Dashboard would show:</b><br/>
<br/>
📊 <b>LEAD PIPELINE</b><br/>
&nbsp;&nbsp;&nbsp;• New Leads: 15 (Last 7 days)<br/>
&nbsp;&nbsp;&nbsp;• Total in Pipeline: 247<br/>
&nbsp;&nbsp;&nbsp;• Win Rate: 32% (Converted/Total)<br/>
<br/>
🎯 <b>BY SOURCE</b><br/>
&nbsp;&nbsp;&nbsp;• Website: 45 leads → 15 converted (33%)<br/>
&nbsp;&nbsp;&nbsp;• Referral: 20 leads → 18 converted (90%)<br/>
&nbsp;&nbsp;&nbsp;• Cold Call: 50 leads → 8 converted (16%)<br/>
&nbsp;&nbsp;&nbsp;• Email: 132 leads → 12 converted (9%)<br/>
<br/>
👤 <b>BY SALESPERSON</b><br/>
&nbsp;&nbsp;&nbsp;• John: 50 leads → 18 converted (36%)<br/>
&nbsp;&nbsp;&nbsp;• Sarah: 60 leads → 22 converted (37%)<br/>
&nbsp;&nbsp;&nbsp;• Mike: 40 leads → 10 converted (25%)<br/>
<br/>
💰 <b>PIPELINE VALUE</b><br/>
&nbsp;&nbsp;&nbsp;• Total qualified deals: $2,450,000<br/>
&nbsp;&nbsp;&nbsp;• Expected revenue (32%): $784,000<br/>
<br/>
⏰ <b>AGING</b><br/>
&nbsp;&nbsp;&nbsp;• Leads > 30 days old: 45 (need follow-up)<br/>
&nbsp;&nbsp;&nbsp;• Leads > 60 days old: 12 (re-qualify)<br/>
"""

elements.append(Paragraph(dashboard_text, normal_style))

elements.append(PageBreak())

# Section 11: Quick Reference
elements.append(Paragraph("11. QUICK REFERENCE GUIDE", heading_style))

quick_ref_data = [
    ["Situation", "Action", "Status"],
    ["Website form submission", "Create Lead", "NEW"],
    ["Salesperson gets referral", "Create Lead with source=REF", "NEW"],
    ["Need list of prospects", "Filter Leads by score, source", "—"],
    ["Convert to customer", "Change status to CONVERTED", "CONVERTED"],
    ["Customer went silent", "Mark as LOST after 90 days", "LOST"],
    ["Find best sources", "Group by source, count conversions", "—"],
    ["Assign work fairly", "Distribute new leads evenly", "—"],
    ["Track performance", "Count conversions per salesperson", "—"]
]

quick_table = Table(quick_ref_data, colWidths=[1.8*inch, 2.2*inch, 1.5*inch])
quick_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e5c9a')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 9),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 1), (-1, -1), 8),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')])
]))

elements.append(quick_table)

elements.append(Spacer(1, 0.5*inch))

# Summary
elements.append(Paragraph("SUMMARY", heading_style))
summary_text = """
<b>🎯 LEADS = Your Sales Pipeline</b><br/>
&nbsp;&nbsp;&nbsp;• Prospect interested in your product<br/>
&nbsp;&nbsp;&nbsp;• Need qualification and nurturing<br/>
&nbsp;&nbsp;&nbsp;• Can become customers<br/>
<br/>
<b>📌 LEAD SOURCE = Where leads come from</b><br/>
&nbsp;&nbsp;&nbsp;• Website, Referral, Email, Cold Call, etc.<br/>
&nbsp;&nbsp;&nbsp;• Track which channels work best<br/>
&nbsp;&nbsp;&nbsp;• Measure ROI of marketing/sales efforts<br/>
<br/>
<b>💼 USAGE:</b><br/>
&nbsp;&nbsp;&nbsp;1. Create lead when prospect shows interest<br/>
&nbsp;&nbsp;&nbsp;2. Update status as they progress through pipeline<br/>
&nbsp;&nbsp;&nbsp;3. Track source to measure channel effectiveness<br/>
&nbsp;&nbsp;&nbsp;4. Score leads to prioritize follow-up<br/>
&nbsp;&nbsp;&nbsp;5. Assign to salespeople for ownership<br/>
&nbsp;&nbsp;&nbsp;6. Convert to customer when deal closes<br/>
&nbsp;&nbsp;&nbsp;7. Analyze trends to improve sales process<br/>
"""

elements.append(Paragraph(summary_text, normal_style))

# Build PDF
doc.build(elements)
print(f"✅ PDF created successfully: {pdf_path}")
