import psycopg2
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Database Configuration
DB_CONFIG = {
    'host': '192.168.220.17',  # Database host
    'database': 'nguccreports',  # Database name
    'user': 'postgres',  # Database user
    'password': 'Avis!123',  # Database password
    'port': 5432  # Default PostgreSQL port
}

# Email Configuration
EMAIL_CONFIG = {
    'from_email': 'jitesh@avissupport.com',
    'to_email': [
        'rohit.shrivastava@cogenteservices.com'
    ],
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'username': 'jitesh@avissupport.com',
    'password': 'wlfh jfbp czhu kutg'
}

# List of Campaign Names
CAMPAIGN_NAMES = [
    "Broadcasting2", "TRIP_NOT_START_HINDI", "VAN_NOT_REACHED_HINDI",
    "VAN_NOT_REACHED_TAMIL", "TRIP_NOT_START_KANNADA", "VAN_NOT_REACHED_MALAYALAM",
    "BROADCAST_Telugu", "VAN_NOT_REACHED_TELUGU", "Broadcasting_Ticket_Not_Closed",
    "BROADCAST_Kannada", "BROADCAST_malayalam", "VAN_NOT_REACHED_KANNADA",
    "TRIP_NOT_START_MALAYALAM", "TRIP_NOT_START_TELUGU", "BROADCAST_Tamil",
    "TRIP_NOT_START_TAMIL", "broadcast_trip_end_2"
]

# Function to Check Dialing Status
def check_dialing_status(campaign_name):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = f"""
        SELECT COUNT(*)
        FROM nr_conn_cdr
        WHERE campname = %s
          AND callstartdate >= NOW() - INTERVAL '30 minutes';
        """
        cursor.execute(query, (campaign_name,))
        result = cursor.fetchone()
        conn.close()
        return result[0] > 0  # True if dialing occurred, False otherwise
    except Exception as e:
        print(f"Database error for campaign {campaign_name}: {e}")
        return False

# Function to Send Consolidated Email Alert

def send_email_alert(campaigns_without_dialing):
    if not campaigns_without_dialing:
        print("No campaigns without dialing. No email sent.")
        return

    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['from_email']
        msg['To'] = ', '.join(EMAIL_CONFIG['to_email'])
        msg['Subject'] = 'Dialing Alert: Campaigns without activity in the last 30 minutes'

        # Create Email Body
        campaign_list = "\n".join(campaigns_without_dialing)
        body = f"""
        Alert! No numbers have been dialed in the following campaigns for the last 30 minutes:
        
        {campaign_list}

        Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        msg.attach(MIMEText(body, 'plain'))

        # Send Email
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.starttls()
        server.login(EMAIL_CONFIG['username'], EMAIL_CONFIG['password'])
        server.send_message(msg)
        server.quit()

        print("Consolidated email alert sent successfully.")
    except Exception as e:
        print(f"Email error: {e}")
        
# Main Function
def main():
    campaigns_without_dialing = []
    for campaign in CAMPAIGN_NAMES:
        dialing_status = check_dialing_status(campaign)
        if not dialing_status:
            campaigns_without_dialing.append(campaign)

# Send Consolidated Email
send_email_alert(campaigns_without_dialing)

if __name__ == "__main__":
    main()
