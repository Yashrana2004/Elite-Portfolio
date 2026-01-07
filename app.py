from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- STEP 1: INITIALIZE APP ---
app = Flask(__name__)
CORS(app)

# Configuration
DB_FILE = "messages.csv"
MY_GMAIL = "bharatrn95@gmail.com"
# Cleaned: Removed spaces for the SMTP login logic
MY_APP_PASSWORD = "rlsvzoghzijdeamp" 

# --- EMAIL HELPER FUNCTION ---
def send_auto_reply(receiver_email, receiver_name):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = '🚀 Thank you for contacting Yash Rana!'
    msg['From'] = MY_GMAIL
    msg['To'] = receiver_email

    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="background-color: #0b1020; padding: 20px; text-align: center;">
                <h1 style="color: #00f2ff;">YASH RANA</h1>
            </div>
            <div style="padding: 20px;">
                <h2>Hi {receiver_name},</h2>
                <p>Thank you for reaching out through my portfolio! I have received your message and will review it shortly.</p>
                <p>I usually respond within 24 hours. In the meantime, feel free to check out my latest work on GitHub.</p>
                <br>
                <p>Best regards,</p>
                <p><strong>Yash Rana</strong><br>Developer & Tech Lead</p>
            </div>
            <div style="background-color: #f4f4f4; padding: 10px; text-align: center; font-size: 12px; color: #777;">
                Sent from Yash Rana's Elite Portfolio Backend
            </div>
        </body>
    </html>
    """
    msg.attach(MIMEText(html_body, 'html'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(MY_GMAIL, MY_APP_PASSWORD)
            server.send_message(msg)
        print(f"📧 Auto-reply sent to {receiver_email}")
    except Exception as e:
        print(f"❌ Email Error: {e}")

# --- STEP 2: ROUTES ---

@app.route('/')
def home():
    return "<h1>Python Backend is Running!</h1><p>Visit /admin?pw=yash123 to see messages.</p>"

@app.route('/admin')
def view_messages():
    password = request.args.get('pw')
    if password != "yash123": 
        return "<h1>Unauthorized Access!</h1>", 403

    if not os.path.isfile(DB_FILE):
        return "<h1>No messages yet!</h1>"
    
    html_content = """
    <html>
    <head>
        <style>
            body { font-family: sans-serif; background: #0b1020; color: white; padding: 40px; }
            table { width: 100%; border-collapse: collapse; background: rgba(255,255,255,0.05); }
            th, td { border: 1px solid #444; padding: 12px; text-align: left; }
            th { background: #00f2ff; color: black; }
            tr:hover { background: rgba(255,255,255,0.1); }
        </style>
    </head>
    <body>
        <h1>📩 Contact Form Submissions</h1>
        <table>
            <tr><th>Name</th><th>Email</th><th>Phone</th><th>Message</th></tr>
    """
    with open(DB_FILE, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        try:
            next(reader) # Skip header
            for row in reader:
                # SAFETY CHECK: Only process rows that have all 4 columns
                if len(row) >= 4:
                    html_content += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td></tr>"
                else:
                    continue # Skip empty lines that cause IndexErrors
        except StopIteration:
            pass # Handle case where file is empty
    
    html_content += "</table><br><a href='/' style='color:#00f2ff;'>Back Home</a></body></html>"
    return html_content

@app.route('/api/contact', methods=['POST'])
def handle_contact():
    try:
        data = request.json
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        message = data.get('message')

        # 1. Save to CSV Database
        file_exists = os.path.isfile(DB_FILE)
        with open(DB_FILE, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['Name', 'Email', 'Phone', 'Message'])
            writer.writerow([name, email, phone, message])
        print(f"✅ Success: Message from {name} saved.")

        # 2. Send Auto-Reply
        send_auto_reply(email, name)

        return jsonify({"success": True, "message": "Victory! Message saved and email sent."}), 200
    except Exception as e:
        print(f"❌ Server Error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)