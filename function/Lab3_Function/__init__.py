## This folder will contains the Azure function code.

## Note:

import logging
import azure.functions as func
import psycopg2
import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def main(msg: func.ServiceBusMessage):

    notification_id = int(msg.get_body().decode('utf-8'))
    logging.info('Python ServiceBus queue trigger processed message: %s',notification_id)

    db_host = os.environ['POSTGRES_URL']
    db_name = os.environ['techconfdb']
    db_user = os.environ['techconfdb']
    db_password = os.environ['POSTGRES_PW']

    conn = psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password
    )

    try:
        sg_api_key = "your_sendgrid_api_key"
        sg = SendGridAPIClient(api_key=sg_api_key)
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM notification WHERE id = %s", (notification_id,))
            noti = cursor.fetchone()
            cursor.execute("SELECT email, name FROM attendee")
            attendees = cursor.fetchall()
            
            for attendee in attendees:
                message = Mail(
                    from_email="dichle187@gmail.com",
                    to_emails=attendee[1],
                    subject=noti[5],
                    plain_text_content= noti[2]
                )
                sg.send(message)

            cursor.execute("UPDATE notification SET status= 'Notified %s attendees', completed_date= %s WHERE id = %s", (attendees.count(), datetime.now(), notification_id,))
        
        conn.commit()
        print('ok')
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        conn.close()