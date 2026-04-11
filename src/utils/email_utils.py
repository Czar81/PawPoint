import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def send_order_confirmation(customer_email, customer_name, order_id, products, total):
    """
    Sends an order confirmation email to the customer.
    """
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    sender_email = os.getenv("SENDER_EMAIL")

    if not all([smtp_server, smtp_port, smtp_user, smtp_password, sender_email]):
        print("Email configuration missing. Skipping email sending.")
        return False

    # Create message
    message = MIMEMultipart("alternative")
    message["Subject"] = f"Order Confirmation #{order_id} - PawStore"
    message["From"] = sender_email
    message["To"] = customer_email

    # Create HTML content
    items_html = "".join([
        f"<li>{item['name']} x {item['quantity']} - ₡{item['subtotal']}</li>"
        for item in products
    ])

    html = f"""
    <html>
      <body style="font-family: sans-serif; color: #333;">
        <h2 style="color: #6a5acd;">Thank you for your purchase, {customer_name}!</h2>
        <p>We are excited to let you know that we have received your order <strong>#{order_id}</strong>.</p>
        <h3>Order Summary:</h3>
        <ul>
            {items_html}
        </ul>
        <p><strong>Total: ₡{total}</strong></p>
        <hr>
        <p>If you have any questions, please contact us at support@pawstore.com</p>
        <p>Best regards,<br>The PawStore Team</p>
      </body>
    </html>
    """

    part = MIMEText(html, "html")
    message.attach(part)

    try:
        with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(sender_email, customer_email, message.as_string())
        print(f"Confirmation email sent to {customer_email}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
