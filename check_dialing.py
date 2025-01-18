import psycopg2
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Configuration
DB_CONFIG = {
    'host': '192.168.220.17',  # Database host
    'database': 'ngucc',  # Database name
    'user': 'postgres',  # Database user
    'password': 'Avis!123',  # Database password
    'port': 5432  # Default PostgreSQL port
}

EMAIL_CONFIG = {
    'from_email': 'jitesh@avissupport.com',
    'to_email': [
        'rohit.shrivastava@cogenteservices.com'
],
    'smtp_server': 'smtp.gmail.com',  # Replace with your SMTP server
    'smtp_port': 587,  # SMTP port (587 for TLS)
    'username': 'jitesh@avisupport.com',  # Email server username
    'password': 'khushi@!$#'  # Email server password
}

# Function to fetch active campaigns
def fetch_active_campaigns():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = "SELECT name FROM campaigns WHERE is_active = TRUE;"
        cursor.execute(query)
        campaigns = [row[0] for row in cursor.fetchall()]
        conn.close()
        return campaigns
    except Exception as e:
        print(f"Error fetching campaigns: {e}")
        return []

# Function to check dialing status for a campaign
def check_dialing_status(campaign_name):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = f"""
        SELECT COUNT(*)
        FROM call_logs
        WHERE campaign = %s
          AND call_time >= NOW() - INTERVAL '30 minutes';
        """
        cursor.execute(query, (campaign_name,))
        result = cursor.fetchone()
        conn.close()
        return result[0] > 0  # True if dialing occurred, False otherwise
    except Exception as e:
        print(f"Database error for campaign {campaign_name}: {e}")
        return False

# Function to send email alert
def send_email_alert(campaign_name):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['from_email']
        msg['To'] = ', '.join(EMAIL_CONFIG['to_email'])
        msg['Subject'] = f'Dialing Alert: No activity detected in {campaign_name}'

        # Email body
        body = f"""
        Alert! No numbers have been dialed in the campaign "{campaign_name}" for the last 30 minutes.
        Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        msg.attach(MIMEText(body, 'plain'))

        # Connect to SMTP server and send email
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.starttls()  # Enable TLS
        server.login(EMAIL_CONFIG['username'], EMAIL_CONFIG['password'])
        server.send_message(msg)
        server.quit()

        print(f"Email alert sent successfully for campaign: {campaign_name}.")
    except Exception as e:
        print(f"Email error for campaign {campaign_name}: {e}")

# Main function
def main():
    campaigns = fetch_active_campaigns()
    if not campaigns:
        print("No active campaigns found.")
        return

    for campaign in campaigns:
        dialing_status = check_dialing_status(campaign)
        if not dialing_status:
            send_email_alert(campaign)

if __name__ == "__main__":
    main()
