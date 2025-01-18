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
    'from_email': 'cogent656@gmail.com',
    'to_email': [
        'rohit.shrivastava@cogenteservices.com'
    ],
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'username': 'cogent656@gmail.com',
    'password': 'mfadmyczyevfkpfl'
}

# List of Campaign Names
CAMPAIGN_NAMES = [
    "VAN_NOT_REACHED_KANNADA", "TRIP_NOT_START_HINDI", "BROADCAST_Tamil",
    "VAN_NOT_REACHED_TAMIL", "BROADCAST_Telugu", "Broadcasting",
    "VAN_NOT_REACHED_TELUGU", "Broadcast_Registration", "BROADCAST_Kannada",
    "BroadcastingTripStart", "Broadcasting_Ticket_Not_Closed", "VAN_NOT_REACHED_MALAYALAM",
    "VAN_Not_Reached_TELUGU", "Vecv_Registration", "TRIP_NOT_START_KANNADA",
    "TRIP_NOT_START_TELUGU", "TRIP_NOT_START_TAMIL", "VAN_NOT_REACHED_HINDI",
    "broadcast_trip_end_2", "Broadcasting_VAN_Not_Reached", "TICKET_NOT_CLOSED_KANNADA",
    "TICKET_NOT_CLOSED_TELUGU", "TRIP_NOT_START_MALAYALAM", "TICKET_NOT_CLOSED_MALAYALAM",
    "BROADCAST_malayalam", "TICKET_NOT_CLOSED_TAMIL"
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

# Function to Send Email Alert
def send_email_alert(campaign_name):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['from_email']
        msg['To'] = ', '.join(EMAIL_CONFIG['to_email'])
        msg['Subject'] = f'Dialing Alert: No activity detected in {campaign_name}'

        # Email Body
        body = f"""
        Alert! No numbers have been dialed in the campaign "{campaign_name}" for the last 30 minutes.
        Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        msg.attach(MIMEText(body, 'plain'))

        # Send Email
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.starttls()
        server.login(EMAIL_CONFIG['username'], EMAIL_CONFIG['password'])
        server.send_message(msg)
        server.quit()

        print(f"Email alert sent successfully for campaign: {campaign_name}.")
    except Exception as e:
        print(f"Email error for campaign {campaign_name}: {e}")

# Main Function
def main():
    for campaign in CAMPAIGN_NAMES:
        dialing_status = check_dialing_status(campaign)
        if not dialing_status:
            send_email_alert(campaign)

if __name__ == "__main__":
    main()
