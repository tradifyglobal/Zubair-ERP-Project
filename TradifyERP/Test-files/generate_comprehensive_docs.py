"""
TradifyERP - Comprehensive Documentation Generator
Generates professional PDF documentation with graphics and diagrams
"""

import os
import sys
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, Image, Frame, KeepTogether, ListFlowable, ListItem
)
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect, String, Circle, Line
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics import renderPDF
from reportlab.lib.colors import HexColor, PCMYKColor
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from io import BytesIO

# Set Django settings
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
sys.path.insert(0, project_root)

# Add base path
BASE_DIR = project_root
OUTPUT_DIR = os.path.join(BASE_DIR, 'documentation_pdfs')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Brand Colors
BRAND_PRIMARY = HexColor('#556ee6')  # Blue
BRAND_SUCCESS = HexColor('#34c38f')  # Green  
BRAND_DANGER = HexColor('#f46a6a')   # Red
BRAND_WARNING = HexColor('#f1b44c')  # Yellow
BRAND_INFO = HexColor('#50a5f1')     # Light Blue
BRAND_DARK = HexColor('#343a40')     # Dark Gray
BRAND_LIGHT = HexColor('#f8f9fa')    # Light Gray

# ERP Module Data
MODULES = {
    'accounting': {
        'name': 'Accounting & Finance',
        'models': 29,
        'views': 40,
        'templates': 25,
        'color': BRAND_PRIMARY,
        'icon': '💰',
        'features': [
            'General Ledger Management',
            'Trial Balance & Financial Reports',
            'Fixed Assets & Depreciation',
            'Accounts Payable/Receivable',
            'Bank Reconciliation',
            'Tax Management',
            'Audit Trail & Period Locks'
        ]
    },
    'hr': {
        'name': 'Human Resources',
        'models': 12,
        'views': 15,
        'templates': 12,
        'color': BRAND_SUCCESS,
        'icon': '👥',
        'features': [
            'Employee Management',
            'Payroll Processing',
            'Leave Management',
            'Attendance Tracking',
            'Performance Reviews',
            'Salary History',
            'Disciplinary Actions'
        ]
    },
    'manufacturing': {
        'name': 'Manufacturing',
        'models': 13,
        'views': 18,
        'templates': 15,
        'color': BRAND_WARNING,
        'icon': '🏭',
        'features': [
            'Bill of Materials (BOM)',
            'Work Orders',
            'Production Planning',
            'Quality Control',
            'Routing & Operations',
            'Resource Management',
            'Production Reporting'
        ]
    },
    'sales': {
        'name': 'Sales Management',
        'models': 3,
        'views': 12,
        'templates': 10,
        'color': BRAND_INFO,
        'icon': '📊',
        'features': [
            'Sales Orders',
            'Customer Invoicing',
            'Revenue Recognition',
            'GL Integration',
            'Tax Calculation',
            'Payment Tracking'
        ]
    },
    'inventory': {
        'name': 'Inventory Management',
        'models': 8,
        'views': 14,
        'templates': 12,
        'color': BRAND_DANGER,
        'icon': '📦',
        'features': [
            'Multi-warehouse Support',
            'Stock Movements',
            'Batch & Serial Tracking',
            'Stock Adjustments',
            'Reorder Points',
            'Inventory Valuation'
        ]
    },
    'procurement': {
        'name': 'Procurement',
        'models': 6,
        'views': 10,
        'templates': 8,
        'color': HexColor('#6f42c1'),
        'icon': '🛒',
        'features': [
            'Purchase Requisitions',
            'Purchase Orders',
            'RFQ Management',
            '3-way Matching',
            'Vendor Management',
            'Procurement Analytics'
        ]
    },
    'ap': {
        'name': 'Accounts Payable',
        'models': 4,
        'views': 8,
        'templates': 6,
        'color': HexColor('#fd7e14'),
        'icon': '💳',
        'features': [
            'Vendor Bills',
            'Payment Processing',
            'Aging Reports',
            'Payment Scheduling',
            'Vendor Statements'
        ]
    },
    'ar': {
        'name': 'Accounts Receivable',
        'models': 4,
        'views': 8,
        'templates': 6,
        'color': HexColor('#e83e8c'),
        'icon': '💵',
        'features': [
            'Customer Invoicing',
            'Payment Collection',
            'Aging Reports',
            'Credit Management',
            'Dunning Process'
        ]
    },
    'crm': {
        'name': 'Customer Relationship Management',
        'models': 21,
        'views': 25,
        'templates': 20,
        'color': HexColor('#20c997'),
        'icon': '🤝',
        'features': [
            'Lead Management',
            'Opportunity Pipeline',
            'Quote Management',
            'Activity Tracking',
            'Campaign Management',
            'Loyalty Programs',
            'Distributor Management'
        ]
    },
    'projects': {
        'name': 'Project Management',
        'models': 8,
        'views': 12,
        'templates': 10,
        'color': HexColor('#17a2b8'),
        'icon': '📋',
        'features': [
            'Project Planning',
            'Task Management',
            'Time Tracking',
            'Budget Management',
            'Resource Allocation',
            'Milestone Tracking'
        ]
    },
    'cash_management': {
        'name': 'Cash Management',
        'models': 5,
        'views': 8,
        'templates': 6,
        'color': HexColor('#6610f2'),
        'icon': '💸',
        'features': [
            'Cash Flow Forecasting',
            'Payment Scheduling',
            'Treasury Management',
            'Liquidity Analysis',
            'Bank Integration'
        ]
    },
    'maintenance': {
        'name': 'Site Maintenance',
        'models': 6,
        'views': 10,
        'templates': 8,
        'color': HexColor('#fd7e14'),
        'icon': '🔧',
        'features': [
            'Asset Management',
            'Work Order Management',
            'Preventive Maintenance',
            'Vendor Management',
            'Cost Tracking'
        ]
    }
}


class ERPDocumentGenerator:
    """Generate all ERP documentation PDFs"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.create_custom_styles()
        
    def create_custom_styles(self):
        """Create custom paragraph styles"""
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=BRAND_PRIMARY,
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=BRAND_DARK,
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Section style
        self.styles.add(ParagraphStyle(
            name='CustomSection',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=BRAND_PRIMARY,
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))
        
        # Body style with justification
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=8
        ))
        
        # Code style
        self.styles.add(ParagraphStyle(
            name='CustomCode',
            parent=self.styles['Code'],
            fontSize=9,
            fontName='Courier',
            textColor=colors.black,
            backColor=BRAND_LIGHT,
            leftIndent=20,
            rightIndent=20,
            spaceAfter=10
        ))
    
    def create_cover_page(self, title, subtitle, doc_type):
        """Create a professional cover page"""
        story = []
        
        # Add logo/header space
        story.append(Spacer(1, 1.5*inch))
        
        # Main title
        story.append(Paragraph(
            f'<b>{title}</b>',
            ParagraphStyle(
                'CoverTitle',
                parent=self.styles['CustomTitle'],
                fontSize=32,
                textColor=BRAND_PRIMARY
            )
        ))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Subtitle
        story.append(Paragraph(
            subtitle,
            ParagraphStyle(
                'CoverSubtitle',
                parent=self.styles['CustomSubtitle'],
                fontSize=18,
                textColor=BRAND_DARK,
                alignment=TA_CENTER
            )
        ))
        
        story.append(Spacer(1, 0.5*inch))
        
        # Document type
        story.append(Paragraph(
            f'<b>{doc_type}</b>',
            ParagraphStyle(
                'DocType',
                fontSize=16,
                textColor=BRAND_INFO,
                alignment=TA_CENTER
            )
        ))
        
        story.append(Spacer(1, 1*inch))
        
        # System info box
        info_data = [
            ['System Version:', 'TradifyERP v1.0'],
            ['Total Modules:', '12 Modules'],
            ['Database:', 'PostgreSQL / SQLite'],
            ['Framework:', 'Django 5.2.8'],
            ['Python Version:', '3.14'],
            ['Generated:', datetime.now().strftime('%B %d, %Y')]
        ]
        
        info_table = Table(info_data, colWidths=[2.5*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), BRAND_LIGHT),
            ('TEXTCOLOR', (0, 0), (-1, -1), BRAND_DARK),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, BRAND_PRIMARY),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 1*inch))
        
        # Footer
        story.append(Paragraph(
            '<b>Tradify Global</b><br/>Enterprise Resource Planning System',
            ParagraphStyle(
                'Footer',
                fontSize=12,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
        ))
        
        story.append(PageBreak())
        return story
    
    def create_module_diagram(self, width=500, height=400):
        """Create a visual diagram showing all modules"""
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # Central core
        core = patches.Circle((5, 5), 1.5, linewidth=3, 
                             edgecolor='#556ee6', 
                             facecolor='#f8f9fa')
        ax.add_patch(core)
        ax.text(5, 5, 'CORE\nAccounting', ha='center', va='center', 
               fontsize=12, fontweight='bold')
        
        # Module positions in a circle
        module_list = [
            ('HR', 'cyan', 3, 1.2),
            ('Sales', 'lightgreen', 5, 1.5),
            ('Inventory', 'orange', 7, 1.2),
            ('Manufacturing', 'yellow', 8.5, 5),
            ('CRM', 'pink', 7, 8.8),
            ('Projects', 'lightblue', 5, 8.5),
            ('Procurement', 'lightcoral', 3, 8.8),
            ('AP', 'lightgray', 1.5, 5),
            ('AR', 'lavender', 3, 5),
            ('Cash Mgmt', 'lightyellow', 7, 5),
            ('Maintenance', 'lightgoldenrodyellow', 5, 3)
        ]
        
        for name, color, x, y in module_list:
            circle = patches.Circle((x, y), 0.6, linewidth=2,
                                   edgecolor='black', facecolor=color)
            ax.add_patch(circle)
            ax.text(x, y, name, ha='center', va='center', 
                   fontsize=9, fontweight='bold')
            
            # Draw connection to core
            ax.plot([x, 5], [y, 5], 'k--', alpha=0.3, linewidth=1)
        
        # Title
        ax.text(5, 9.5, 'TradifyERP Module Architecture', 
               ha='center', fontsize=14, fontweight='bold')
        
        # Save to bytes
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close()
        
        return Image(buf, width=width, height=height)
    
    def generate_system_overview(self):
        """Generate Document 1: Complete System Overview & Module Linkages"""
        filename = os.path.join(OUTPUT_DIR, '1_TradifyERP_System_Overview_and_Module_Linkages.pdf')
        doc = SimpleDocTemplate(filename, pagesize=letter,
                               rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)
        
        story = []
        
        # Cover page
        story.extend(self.create_cover_page(
            'TradifyERP',
            'Complete System Overview & Module Linkages',
            'System Architecture Document'
        ))
        
        # Table of Contents
        story.append(Paragraph('<b>Table of Contents</b>', self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        toc_data = [
            ['Section', 'Page'],
            ['1. Executive Summary', '3'],
            ['2. System Architecture', '5'],
            ['3. Module Overview', '8'],
            ['4. Module Interconnections', '15'],
            ['5. Data Flow Diagrams', '20'],
            ['6. Integration Points', '25'],
            ['7. Technology Stack', '30']
        ]
        
        toc_table = Table(toc_data, colWidths=[4*inch, 1*inch])
        toc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BRAND_PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, BRAND_PRIMARY),
        ]))
        
        story.append(toc_table)
        story.append(PageBreak())
        
        # Executive Summary
        story.append(Paragraph('<b>1. Executive Summary</b>', self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph(
            '''TradifyERP is a comprehensive, enterprise-grade resource planning system designed to 
            manage all aspects of business operations. Built on Django 5.2.8 with Python 3.14, the system 
            comprises 12 fully integrated modules covering financial management, human resources, 
            manufacturing, sales, inventory, procurement, and customer relationship management.''',
            self.styles['CustomBody']
        ))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Key statistics
        story.append(Paragraph('<b>System Statistics</b>', self.styles['CustomSection']))
        
        stats_data = [
            ['Total Modules', '12', 'Production Ready'],
            ['Total Models', '122+', 'Database Tables'],
            ['Total Views', '150+', 'Business Logic'],
            ['Total Templates', '100+', 'User Interface'],
            ['Lines of Code', '20,000+', 'Well-Documented'],
            ['Integrated Workflows', '25+', 'Cross-Module']
        ]
        
        stats_table = Table(stats_data, colWidths=[2*inch, 1.5*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BRAND_PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, -1), BRAND_DARK),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, BRAND_PRIMARY),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [BRAND_LIGHT, colors.white])
        ]))
        
        story.append(stats_table)
        story.append(PageBreak())
        
        # System Architecture Diagram
        story.append(Paragraph('<b>2. System Architecture</b>', self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph(
            '''The TradifyERP system follows a modular architecture pattern where each module operates 
            independently while seamlessly integrating with the central accounting core. This design ensures 
            data consistency, enables scalability, and maintains clear separation of concerns.''',
            self.styles['CustomBody']
        ))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Add module diagram
        diagram = self.create_module_diagram()
        story.append(diagram)
        
        story.append(PageBreak())
        
        # Module Overview
        story.append(Paragraph('<b>3. Module Overview</b>', self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        for module_key, module_data in MODULES.items():
            story.append(Paragraph(
                f'''<b>{module_data['icon']} {module_data['name']}</b>''',
                self.styles['CustomSubtitle']
            ))
            
            # Module stats
            module_stats = [
                ['Models', str(module_data['models'])],
                ['Views', str(module_data['views'])],
                ['Templates', str(module_data['templates'])]
            ]
            
            module_table = Table(module_stats, colWidths=[1.5*inch, 1*inch])
            module_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), BRAND_LIGHT),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 0), (-1, -1), 9)
            ]))
            
            story.append(module_table)
            story.append(Spacer(1, 0.1*inch))
            
            # Features list
            story.append(Paragraph('<b>Key Features:</b>', self.styles['CustomBody']))
            
            feature_items = [ListItem(Paragraph(f, self.styles['CustomBody']), 
                           leftIndent=20) for f in module_data['features']]
            feature_list = ListFlowable(feature_items, bulletType='bullet')
            story.append(feature_list)
            
            story.append(Spacer(1, 0.2*inch))
        
        story.append(PageBreak())
        
        # Module Interconnections
        story.append(Paragraph('<b>4. Module Interconnections</b>', self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        connections = [
            ['From Module', 'To Module', 'Integration Type', 'Data Flow'],
            ['Sales', 'Accounting', 'Real-time', 'Revenue Recognition'],
            ['Sales', 'AR', 'Real-time', 'Customer Invoices'],
            ['Manufacturing', 'Inventory', 'Real-time', 'Material Consumption'],
            ['Manufacturing', 'Accounting', 'Batch', 'Production Costs'],
            ['Procurement', 'AP', 'Real-time', 'Vendor Bills'],
            ['Procurement', 'Inventory', 'Real-time', 'Stock Receipts'],
            ['HR', 'Accounting', 'Batch', 'Payroll Entries'],
            ['CRM', 'Sales', 'Real-time', 'Opportunities to Orders'],
            ['Projects', 'Accounting', 'Batch', 'Project Costs'],
            ['AP', 'Accounting', 'Real-time', 'Payment Entries'],
            ['AR', 'Accounting', 'Real-time', 'Receipt Entries'],
            ['Cash Mgmt', 'Accounting', 'Real-time', 'Cash Forecasts']
        ]
        
        conn_table = Table(connections, colWidths=[1.5*inch, 1.5*inch, 1.2*inch, 1.8*inch])
        conn_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BRAND_PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, BRAND_PRIMARY),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BRAND_LIGHT])
        ]))
        
        story.append(conn_table)
        
        # Build PDF
        doc.build(story)
        print(f'✅ Generated: {filename}')
        
        return filename
    
    def generate_knowledge_transfer(self):
        """Generate Document 2: Knowledge Transfer Document"""
        filename = os.path.join(OUTPUT_DIR, '2_TradifyERP_Knowledge_Transfer_Document.pdf')
        doc = SimpleDocTemplate(filename, pagesize=letter,
                               rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)
        
        story = []
        
        # Cover
        story.extend(self.create_cover_page(
            'TradifyERP',
            'Knowledge Transfer Document',
            'Developer & Administrator Guide'
        ))
        
        # Content sections
        story.append(Paragraph('<b>1. System Overview</b>', self.styles['CustomTitle']))
        story.append(Paragraph(
            '''This document provides comprehensive knowledge transfer for TradifyERP developers and 
            administrators. It covers system architecture, coding conventions, deployment procedures, 
            and operational best practices.''',
            self.styles['CustomBody']
        ))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Technology Stack
        story.append(Paragraph('<b>2. Technology Stack</b>', self.styles['CustomSubtitle']))
        
        tech_stack = [
            ['Component', 'Technology', 'Version'],
            ['Backend Framework', 'Django', '5.2.8'],
            ['Programming Language', 'Python', '3.14'],
            ['Database', 'PostgreSQL / SQLite', '15+ / 3.x'],
            ['Frontend Framework', 'Bootstrap', '5.3'],
            ['Template Engine', 'Django Templates', '5.2.8'],
            ['Authentication', 'Django Allauth', 'Latest'],
            ['Forms', 'Crispy Forms', 'Latest'],
            ['Task Queue', 'Celery (Optional)', '5.x']
        ]
        
        tech_table = Table(tech_stack, colWidths=[2*inch, 2*inch, 1.5*inch])
        tech_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BRAND_PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, BRAND_PRIMARY),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')
        ]))
        
        story.append(tech_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Project Structure
        story.append(Paragraph('<b>3. Project Structure</b>', self.styles['CustomSubtitle']))
        
        story.append(Paragraph('''<font name="Courier" size="9">
TradifyERP/<br/>
├── TradifyERP/<br/>
│   ├── __init__.py<br/>
│   ├── settings.py          # Main configuration<br/>
│   ├── urls.py              # Root URL configuration<br/>
│   ├── wsgi.py              # WSGI application<br/>
│   └── asgi.py              # ASGI application<br/>
├── accounting/              # Core accounting module<br/>
│   ├── models.py            # 29 models<br/>
│   ├── views.py             # Business logic<br/>
│   ├── urls.py              # URL routing<br/>
│   ├── forms.py             # Form definitions<br/>
│   └── templates/           # HTML templates<br/>
├── hr/                      # HR module<br/>
├── manufacturing/           # Manufacturing module<br/>
├── sales/                   # Sales module<br/>
├── inventory/               # Inventory module<br/>
├── procurement/             # Procurement module<br/>
├── ap/                      # Accounts Payable<br/>
├── ar/                      # Accounts Receivable<br/>
├── crm/                     # CRM module<br/>
├── projects/                # Project management<br/>
├── cash_management/         # Cash management<br/>
├── maintenance/             # Site maintenance<br/>
├── templates/               # Global templates<br/>
├── static/                  # Static files<br/>
├── manage.py                # Django management<br/>
└── requirements.txt         # Python dependencies
</font>''', self.styles['CustomCode']))
        
        story.append(PageBreak())
        
        # Database Schema
        story.append(Paragraph('<b>4. Database Schema Overview</b>', self.styles['CustomSubtitle']))
        
        story.append(Paragraph(
            '''The database consists of 122+ tables organized by module. All modules share the Entity 
            model for multi-company support. Key relationships include:''',
            self.styles['CustomBody']
        ))
        
        schema_points = [
            'Entity → All modules (one-to-many)',
            'Account → LedgerEntry (one-to-many)',
            'VendorInvoice → VendorPayment (one-to-many)',
            'Customer → SalesOrder → SalesInvoice (cascading)',
            'Product → BOM → WorkOrder (manufacturing chain)',
            'Employee → Payroll → PayrollItem (HR hierarchy)',
            'Project → Task → TimeEntry (project tracking)'
        ]
        
        for point in schema_points:
            story.append(Paragraph(f'• {point}', self.styles['CustomBody']))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Key Business Processes
        story.append(Paragraph('<b>5. Key Business Processes</b>', self.styles['CustomSubtitle']))
        
        processes = [
            ('Order to Cash (O2C)', [
                '1. CRM Lead → Opportunity',
                '2. Sales Quote → Sales Order',
                '3. Sales Invoice (Revenue Recognition)',
                '4. AR Collection → Bank Deposit',
                '5. GL Posting (automatic)'
            ]),
            ('Procure to Pay (P2P)', [
                '1. Purchase Requisition',
                '2. RFQ → Purchase Order',
                '3. Goods Receipt → Stock',
                '4. Vendor Invoice (3-way match)',
                '5. AP Payment → Bank',
                '6. GL Posting (automatic)'
            ]),
            ('Manufacturing Process', [
                '1. Sales Order → Production Planning',
                '2. BOM → Work Order',
                '3. Material Requisition → Inventory',
                '4. Production Execution',
                '5. Quality Control',
                '6. Finished Goods → Stock',
                '7. Cost Accounting → GL'
            ])
        ]
        
        for process_name, steps in processes:
            story.append(Paragraph(f'<b>{process_name}:</b>', self.styles['CustomSection']))
            for step in steps:
                story.append(Paragraph(step, self.styles['CustomBody']))
            story.append(Spacer(1, 0.2*inch))
        
        story.append(PageBreak())
        
        # Security & Access Control
        story.append(Paragraph('<b>6. Security & Access Control</b>', self.styles['CustomSubtitle']))
        
        story.append(Paragraph(
            '''TradifyERP implements role-based access control (RBAC) with the following features:''',
            self.styles['CustomBody']
        ))
        
        security_features = [
            'Role-based permissions (View, Create, Edit, Delete, Approve)',
            'Digital signatures for critical transactions',
            'Approval workflows with multi-level authorization',
            'Audit trail for all financial transactions',
            'Period locks to prevent backdating',
            'User action logging (who, what, when)',
            'Session management and timeout controls'
        ]
        
        for feature in security_features:
            story.append(Paragraph(f'• {feature}', self.styles['CustomBody']))
        
        # Build PDF
        doc.build(story)
        print(f'✅ Generated: {filename}')
        
        return filename
    
    def generate_technical_documentation(self):
        """Generate Document 3: Technical Documentation"""
        filename = os.path.join(OUTPUT_DIR, '3_TradifyERP_Technical_Documentation.pdf')
        doc = SimpleDocTemplate(filename, pagesize=letter,
                               rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)
        
        story = []
        
        # Cover
        story.extend(self.create_cover_page(
            'TradifyERP',
            'Technical Documentation',
            'Developer Reference Guide'
        ))
        
        # API Documentation
        story.append(Paragraph('<b>1. API Reference</b>', self.styles['CustomTitle']))
        story.append(Paragraph(
            '''TradifyERP provides a comprehensive set of views, models, and utilities for each module. 
            This section documents the key APIs and their usage.''',
            self.styles['CustomBody']
        ))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Model API Example
        story.append(Paragraph('<b>1.1 Accounting Models</b>', self.styles['CustomSubtitle']))
        
        story.append(Paragraph('''<font name="Courier" size="9">
# Entity Model<br/>
class Entity(models.Model):<br/>
    """Represents a legal entity or business unit"""<br/>
    name = models.CharField(max_length=255, unique=True)<br/>
    code = models.CharField(max_length=50, unique=True)<br/>
    description = models.TextField(blank=True, null=True)<br/>
    is_active = models.BooleanField(default=True)<br/>
    <br/>
# LedgerEntry Model<br/>
class LedgerEntry(models.Model):<br/>
    """General Ledger entries"""<br/>
    account = models.ForeignKey(Account)<br/>
    entity = models.ForeignKey(Entity)<br/>
    entry_date = models.DateField()<br/>
    entry_type = models.CharField(choices=ENTRY_TYPES)<br/>
    amount = models.DecimalField(max_digits=18, decimal_places=2)<br/>
    description = models.TextField()<br/>
    is_posted = models.BooleanField(default=False)
</font>''', self.styles['CustomCode']))
        
        story.append(PageBreak())
        
        # Views Documentation
        story.append(Paragraph('<b>1.2 Views & URL Patterns</b>', self.styles['CustomSubtitle']))
        
        story.append(Paragraph('''<font name="Courier" size="9">
# Dashboard View<br/>
class DashboardView(LoginRequiredMixin, TemplateView):<br/>
    template_name = 'accounting/dashboard.html'<br/>
    <br/>
    def get_context_data(self, **kwargs):<br/>
        context = super().get_context_data(**kwargs)<br/>
        entity = Entity.objects.filter(is_active=True).first()<br/>
        context['entity'] = entity<br/>
        context['total_revenue'] = self.calculate_revenue()<br/>
        return context<br/>
<br/>
# URL Pattern<br/>
urlpatterns = [<br/>
    path('dashboard/', DashboardView.as_view(), name='dashboard'),<br/>
    path('accounts/', AccountListView.as_view(), name='account_list'),<br/>
    path('ledger/', LedgerEntryListView.as_view(), name='ledger_list'),<br/>
]
</font>''', self.styles['CustomCode']))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Database Optimization
        story.append(Paragraph('<b>2. Database Optimization</b>', self.styles['CustomSubtitle']))
        
        optimization_tips = [
            ('Indexes', 'All foreign keys and frequently queried fields have database indexes'),
            ('Query Optimization', 'Use select_related() and prefetch_related() for related objects'),
            ('Caching', 'Django cache framework for frequently accessed data'),
            ('Database Pooling', 'Connection pooling for production deployments'),
            ('Migrations', 'All schema changes tracked in migration files')
        ]
        
        for tip_title, tip_desc in optimization_tips:
            story.append(Paragraph(f'<b>{tip_title}:</b> {tip_desc}', self.styles['CustomBody']))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Testing
        story.append(Paragraph('<b>3. Testing Strategy</b>', self.styles['CustomSubtitle']))
        
        story.append(Paragraph('''<font name="Courier" size="9">
# Unit Test Example<br/>
from django.test import TestCase<br/>
from accounting.models import Entity, Account<br/>
<br/>
class AccountModelTest(TestCase):<br/>
    def setUp(self):<br/>
        self.entity = Entity.objects.create(<br/>
            name='Test Company',<br/>
            code='TEST01'<br/>
        )<br/>
    <br/>
    def test_account_creation(self):<br/>
        account = Account.objects.create(<br/>
            entity=self.entity,<br/>
            account_number='1000',<br/>
            name='Cash',<br/>
            account_type='ASSET'<br/>
        )<br/>
        self.assertEqual(account.account_number, '1000')<br/>
        self.assertTrue(account.is_active)
</font>''', self.styles['CustomCode']))
        
        # Build PDF
        doc.build(story)
        print(f'✅ Generated: {filename}')
        
        return filename
    
    def generate_system_capabilities(self):
        """Generate Document 4: System Capabilities & Features"""
        filename = os.path.join(OUTPUT_DIR, '4_TradifyERP_System_Capabilities.pdf')
        doc = SimpleDocTemplate(filename, pagesize=letter,
                               rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)
        
        story = []
        
        # Cover
        story.extend(self.create_cover_page(
            'TradifyERP',
            'System Capabilities & Features',
            'Functional Specification'
        ))
        
        # Executive Summary
        story.append(Paragraph('<b>Executive Summary</b>', self.styles['CustomTitle']))
        story.append(Paragraph(
            '''TradifyERP is a complete enterprise resource planning system with 12 fully integrated 
            modules managing all aspects of business operations from accounting to manufacturing, 
            sales, inventory, human resources, and customer relationships.''',
            self.styles['CustomBody']
        ))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Module Capabilities
        story.append(Paragraph('<b>Module Capabilities</b>', self.styles['CustomSubtitle']))
        
        for module_key, module_data in MODULES.items():
            story.append(KeepTogether([
                Paragraph(
                    f'''<b>{module_data['icon']} {module_data['name']}</b>''',
                    self.styles['CustomSection']
                ),
                Paragraph('<b>Key Features:</b>', self.styles['CustomBody']),
                *[Paragraph(f'• {feature}', self.styles['CustomBody']) 
                  for feature in module_data['features']],
                Spacer(1, 0.2*inch)
            ]))
        
        story.append(PageBreak())
        
        # Integration Capabilities
        story.append(Paragraph('<b>Integration Capabilities</b>', self.styles['CustomSubtitle']))
        
        integrations = [
            'Real-time GL posting from all modules',
            'Automatic journal entry generation',
            'Cross-module data validation',
            'Unified reporting across modules',
            'Multi-currency support',
            'Multi-entity/company support',
            'Role-based access control',
            'Workflow automation',
            'Email notifications',
            'PDF generation & printing'
        ]
        
        for integration in integrations:
            story.append(Paragraph(f'✓ {integration}', self.styles['CustomBody']))
        
        # Build PDF
        doc.build(story)
        print(f'✅ Generated: {filename}')
        
        return filename
    
    def generate_installation_guide(self):
        """Generate Document 5: Installation Guide"""
        filename = os.path.join(OUTPUT_DIR, '5_TradifyERP_Installation_Guide.pdf')
        doc = SimpleDocTemplate(filename, pagesize=letter,
                               rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)
        
        story = []
        
        # Cover
        story.extend(self.create_cover_page(
            'TradifyERP',
            'Installation Guide',
            'Step-by-Step Setup Instructions'
        ))
        
        # Prerequisites
        story.append(Paragraph('<b>1. Prerequisites</b>', self.styles['CustomTitle']))
        
        prereq_data = [
            ['Component', 'Version', 'Purpose'],
            ['Python', '3.14+', 'Runtime environment'],
            ['PostgreSQL', '15+', 'Production database'],
            ['Git', '2.x', 'Source control'],
            ['pip', 'Latest', 'Package management'],
            ['virtualenv', 'Latest', 'Python isolation']
        ]
        
        prereq_table = Table(prereq_data, colWidths=[2*inch, 1.5*inch, 2*inch])
        prereq_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BRAND_PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, BRAND_PRIMARY),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')
        ]))
        
        story.append(prereq_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Installation Steps
        story.append(Paragraph('<b>2. Installation Steps</b>', self.styles['CustomTitle']))
        
        installation_steps = [
            ('Step 1: Clone Repository', '''
git clone https://github.com/tradifyglobal/Zubair-ERP-Project.git
cd Zubair-ERP-Project/TradifyERP
'''),
            ('Step 2: Create Virtual Environment', '''
python -m venv .venv
.venv\\Scripts\\activate  # Windows
source .venv/bin/activate  # Linux/Mac
'''),
            ('Step 3: Install Dependencies', '''
pip install -r requirements.txt
'''),
            ('Step 4: Configure Database', '''
# Edit TradifyERP/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tradifyerp',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
'''),
            ('Step 5: Run Migrations', '''
python manage.py makemigrations
python manage.py migrate
'''),
            ('Step 6: Create Superuser', '''
python manage.py createsuperuser
'''),
            ('Step 7: Collect Static Files', '''
python manage.py collectstatic
'''),
            ('Step 8: Run Development Server', '''
python manage.py runserver 0.0.0.0:8000
'''),
            ('Step 9: Access Application', '''
Navigate to: http://localhost:8000
Admin: http://localhost:8000/admin
''')
        ]
        
        for step_title, step_code in installation_steps:
            story.append(Paragraph(f'<b>{step_title}</b>', self.styles['CustomSection']))
            story.append(Paragraph(f'<font name="Courier" size="9">{step_code}</font>', 
                                 self.styles['CustomCode']))
            story.append(Spacer(1, 0.2*inch))
        
        story.append(PageBreak())
        
        # Production Deployment
        story.append(Paragraph('<b>3. Production Deployment</b>', self.styles['CustomTitle']))
        
        prod_steps = [
            ('Configure Production Settings', '''
# In settings.py
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']
SECRET_KEY = 'your-secret-key-from-environment'
'''),
            ('Setup Gunicorn (WSGI Server)', '''
pip install gunicorn
gunicorn TradifyERP.wsgi:application --bind 0.0.0.0:8000
'''),
            ('Configure Nginx (Web Server)', '''
# /etc/nginx/sites-available/tradifyerp
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static/ {
        alias /path/to/staticfiles/;
    }
}
'''),
            ('Setup SSL Certificate', '''
# Using Let's Encrypt
sudo certbot --nginx -d your-domain.com
'''),
            ('Configure Systemd Service', '''
# /etc/systemd/system/tradifyerp.service
[Unit]
Description=TradifyERP Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/TradifyERP
ExecStart=/path/to/.venv/bin/gunicorn TradifyERP.wsgi:application

[Install]
WantedBy=multi-user.target
''')
        ]
        
        for step_title, step_code in prod_steps:
            story.append(Paragraph(f'<b>{step_title}</b>', self.styles['CustomSection']))
            story.append(Paragraph(f'<font name="Courier" size="9">{step_code}</font>', 
                                 self.styles['CustomCode']))
            story.append(Spacer(1, 0.2*inch))
        
        # Build PDF
        doc.build(story)
        print(f'✅ Generated: {filename}')
        
        return filename
    
    def generate_all_documents(self):
        """Generate all documentation PDFs"""
        print('🚀 Starting TradifyERP Documentation Generation...\n')
        
        docs = [
            self.generate_system_overview,
            self.generate_knowledge_transfer,
            self.generate_technical_documentation,
            self.generate_system_capabilities,
            self.generate_installation_guide
        ]
        
        generated_files = []
        for doc_generator in docs:
            try:
                filename = doc_generator()
                generated_files.append(filename)
            except Exception as e:
                print(f'❌ Error generating document: {e}')
        
        print(f'\n✅ Successfully generated {len(generated_files)} documentation PDFs')
        print(f'📁 Output directory: {OUTPUT_DIR}')
        print('\n📄 Generated Files:')
        for i, file in enumerate(generated_files, 1):
            print(f'   {i}. {os.path.basename(file)}')
        
        return generated_files


if __name__ == '__main__':
    generator = ERPDocumentGenerator()
    generator.generate_all_documents()
