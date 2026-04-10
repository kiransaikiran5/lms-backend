import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .config import settings
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

def send_email_sync(to_email: str, subject: str, body: str):
    """Synchronous email sending function"""
    try:
        message = MIMEMultipart()
        message["From"] = settings.EMAIL_FROM
        message["To"] = to_email
        message["Subject"] = subject
        
        message.attach(MIMEText(body, "html"))
        
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(message)
        
        logger.info(f"✅ Email sent to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to send email to {to_email}: {str(e)}")
        return False

async def send_email(to_email: str, subject: str, body: str):
    """Asynchronous email sending wrapper"""
    import asyncio
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, send_email_sync, to_email, subject, body)
    return result

# ============ PAYMENT SUCCESS EMAIL ============
async def send_payment_success_email(user_email: str, user_name: str, course_title: str, amount: float):
    """Send payment success confirmation email"""
    
    transaction_id = str(uuid.uuid4())[:8].upper()
    payment_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    
    subject = f"💰 Payment Successful - {course_title}"
    
    body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background: #ffffff;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                border: 1px solid #e0e0e0;
            }}
            .header {{
                background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
            }}
            .header p {{
                margin: 10px 0 0 0;
                opacity: 0.9;
            }}
            .content {{
                background-color: white;
                padding: 30px;
            }}
            .greeting {{
                font-size: 18px;
                margin-bottom: 20px;
            }}
            .payment-details {{
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                padding: 25px;
                border-radius: 10px;
                margin: 20px 0;
                text-align: center;
            }}
            .amount {{
                font-size: 48px;
                font-weight: bold;
                color: #43e97b;
                margin: 10px 0;
            }}
            .course-name {{
                font-size: 20px;
                font-weight: bold;
                color: #333;
                margin: 10px 0;
            }}
            .details-table {{
                width: 100%;
                margin: 20px 0;
                border-collapse: collapse;
            }}
            .details-table td {{
                padding: 10px;
                border-bottom: 1px solid #ddd;
            }}
            .details-table td:first-child {{
                font-weight: bold;
                width: 40%;
            }}
            .transaction-id {{
                background-color: #f0f0f0;
                padding: 10px;
                border-radius: 5px;
                font-family: monospace;
                font-size: 14px;
                text-align: center;
                margin: 20px 0;
            }}
            .button {{
                display: inline-block;
                padding: 12px 30px;
                background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
                font-weight: bold;
            }}
            .footer {{
                background-color: #f8f9fa;
                padding: 20px;
                text-align: center;
                font-size: 12px;
                color: #666;
                border-top: 1px solid #e0e0e0;
            }}
            .success-icon {{
                font-size: 64px;
                margin-bottom: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="success-icon">✅</div>
                <h1>Payment Successful!</h1>
                <p>Thank you for your purchase</p>
            </div>
            <div class="content">
                <div class="greeting">
                    Dear <strong>{user_name}</strong>,
                </div>
                
                <p>Your payment has been processed successfully. You now have full access to your course.</p>
                
                <div class="payment-details">
                    <div class="amount">${amount:.2f}</div>
                    <div class="course-name">📚 {course_title}</div>
                </div>
                
                <table class="details-table">
                    <tr>
                        <td>Transaction ID:</td>
                        <td><strong>{transaction_id}</strong></td>
                    </tr>
                    <tr>
                        <td>Payment Date:</td>
                        <td><strong>{payment_date}</strong></td>
                    </tr>
                    <tr>
                        <td>Payment Status:</td>
                        <td><strong style="color: #43e97b;">✓ Completed</strong></td>
                    </tr>
                    <tr>
                        <td>Payment Method:</td>
                        <td><strong>Credit Card / Online Banking</strong></td>
                    </tr>
                </table>
                
                <div class="transaction-id">
                    Transaction Reference: {transaction_id}
                </div>
                
                <p>What's next?</p>
                <ul>
                    <li>Login to your account</li>
                    <li>Go to "My Courses" section</li>
                    <li>Start learning immediately</li>
                    <li>Track your progress</li>
                </ul>
                
                <div style="text-align: center;">
                    <a href="http://localhost:8000/docs" class="button">🎓 Go to My Courses</a>
                </div>
                
                <p style="margin-top: 20px; font-size: 14px; color: #666;">
                    Keep this email for your records. If you have any questions, contact our support team.
                </p>
            </div>
            <div class="footer">
                <p>This is an automated payment confirmation. Please do not reply to this email.</p>
                <p>&copy; 2024 LMS Platform. All rights reserved.</p>
                <p>Transaction ID: {transaction_id}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    result = await send_email(user_email, subject, body)
    if result:
        logger.info(f"✅ Payment success email sent to {user_email} for ${amount}")
    else:
        logger.warning(f"❌ Failed to send payment email to {user_email}")
    return result

# ============ ENROLLMENT CONFIRMATION EMAIL ============
async def send_enrollment_email(user_email: str, user_name: str, course_title: str):
    """Send enrollment confirmation email"""
    subject = f"🎓 Course Enrollment Confirmation - {course_title}"
    
    body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background: #ffffff;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                border: 1px solid #e0e0e0;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
            }}
            .content {{
                padding: 30px;
            }}
            .course-details {{
                background-color: #f0f0ff;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
                border-left: 4px solid #667eea;
            }}
            .button {{
                display: inline-block;
                padding: 12px 30px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .footer {{
                background-color: #f8f9fa;
                padding: 20px;
                text-align: center;
                font-size: 12px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✨ Enrollment Confirmed! ✨</h1>
            </div>
            <div class="content">
                <p>Dear <strong>{user_name}</strong>,</p>
                <p>Congratulations! You have successfully enrolled in:</p>
                <div class="course-details">
                    <h2 style="margin: 0; color: #667eea;">📚 {course_title}</h2>
                </div>
                <p>You can now:</p>
                <ul>
                    <li>Access all course materials</li>
                    <li>Track your learning progress</li>
                    <li>Complete lessons at your own pace</li>
                </ul>
                <div style="text-align: center;">
                    <a href="http://localhost:8000/docs" class="button">Start Learning Now</a>
                </div>
                <p>Happy learning! 🚀</p>
            </div>
            <div class="footer">
                <p>This is an automated message. Please do not reply.</p>
                <p>&copy; 2024 LMS Platform. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    result = await send_email(user_email, subject, body)
    if result:
        logger.info(f"✅ Enrollment email sent to {user_email}")
    return result