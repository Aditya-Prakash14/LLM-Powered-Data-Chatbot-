import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
import io
import pandas as pd
from datetime import datetime

def send_email_report(recipient_email: str, sender_email: str, sender_password: str, 
                      subject: str, messages: list, chart_data: dict = None) -> bool:
    """Send conversation report via email."""
    try:
        # Create email message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = recipient_email
        
        # Create HTML content
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                <div style="max-width: 600px; background-color: white; padding: 20px; border-radius: 8px;">
                    <h2 style="color: #333;">DataBot Analysis Report</h2>
                    <p style="color: #666;">Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <hr>
                    
                    <h3>Conversation History:</h3>
                    <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px;">
        """
        
        # Add messages to HTML
        for msg_item in messages:
            role = "User" if msg_item["role"] == "user" else "Assistant"
            style = "color: #0066cc;" if msg_item["role"] == "user" else "color: #009933;"
            html_content += f"""
                        <p><strong style="{style}">{role}:</strong></p>
                        <p style="margin-left: 20px; color: #333;">{msg_item['content']}</p>
            """
        
        html_content += """
                    </div>
                    
                    <hr>
                    <p style="color: #999; font-size: 12px;">
                        This is an automated report from DataBot. Do not reply to this email.
                    </p>
                </div>
            </body>
        </html>
        """
        
        # Attach HTML content
        msg.attach(MIMEText(html_content, "html"))
        
        # Send email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        
        return True
    except Exception as e:
        print(f"Email send error: {str(e)}")
        return False

def generate_pdf_report(messages: list, dataset_name: str = "Dataset") -> bytes:
    """Generate PDF report from conversation."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=1
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#333333'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Add title
    story.append(Paragraph("DataBot Analysis Report", title_style))
    story.append(Paragraph(f"Dataset: {dataset_name}", styles['Normal']))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Add conversation
    story.append(Paragraph("Conversation Transcript", heading_style))
    
    for msg_item in messages:
        role = "User" if msg_item["role"] == "user" else "Assistant"
        content = msg_item["content"]
        
        # Create paragraph with role
        role_paragraph = Paragraph(f"<b>{role}:</b>", styles['Normal'])
        story.append(role_paragraph)
        
        # Add content with indentation
        content_style = ParagraphStyle(
            'Content',
            parent=styles['Normal'],
            leftIndent=0.25*inch,
            rightIndent=0.25*inch,
            fontSize=10,
            textColor=colors.HexColor('#555555')
        )
        story.append(Paragraph(content[:500], content_style))
        story.append(Spacer(1, 0.1*inch))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def generate_excel_report(messages: list, dataset_name: str = "Dataset") -> bytes:
    """Generate Excel report from conversation."""
    # Create dataframe from messages
    data = {
        "Role": [msg["role"].capitalize() for msg in messages],
        "Content": [msg["content"][:200] for msg in messages],
        "Timestamp": [datetime.now().isoformat()] * len(messages)
    }
    
    df = pd.DataFrame(data)
    
    # Create Excel file in memory
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Conversation', index=False)
        
        # Add summary sheet
        summary_data = {
            "Metric": ["Total Messages", "User Queries", "Assistant Responses", "Dataset"],
            "Value": [
                len(messages),
                len([m for m in messages if m["role"] == "user"]),
                len([m for m in messages if m["role"] == "assistant"]),
                dataset_name
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    buffer.seek(0)
    return buffer.getvalue()

def export_to_csv(data: dict, filename: str = "export.csv") -> bytes:
    """Export data to CSV format."""
    if isinstance(data, dict):
        df = pd.DataFrame([data])
    else:
        df = pd.DataFrame(data)
    
    buffer = io.BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return buffer.getvalue()
