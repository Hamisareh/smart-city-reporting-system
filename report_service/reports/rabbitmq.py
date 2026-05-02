# report_service/reports/rabbitmq.py

import pika
import json
import logging
import time

logger = logging.getLogger(__name__)

def send_notification(user_id, report_id, notification_type,
                      new_status=None, is_for_admin=False,
                      category_name=None, reporter_username=None):
    """
    Envoyer une notification via RabbitMQ.
    ✅ category_name and reporter_username are now included in the message
       so the consumer can write rich, human-readable notification text.
    """
    try:
        max_retries = 3
        retry_count = 0
        connection = None

        while connection is None and retry_count < max_retries:
            try:
                credentials = pika.PlainCredentials('guest', 'guest')
                parameters = pika.ConnectionParameters(
                    host='rabbitmq',
                    port=5672,
                    credentials=credentials,
                    heartbeat=30
                )
                connection = pika.BlockingConnection(parameters)
            except Exception as e:
                logger.warning(f"RabbitMQ connection attempt {retry_count+1} failed: {e}")
                retry_count += 1
                time.sleep(2)

        if connection is None:
            logger.error("Could not connect to RabbitMQ after retries")
            return

        channel = connection.channel()
        channel.queue_declare(queue='notifications', durable=True)

        message = {
            "user_id": user_id,
            "report_id": report_id,
            "type": notification_type,
            "is_for_admin": is_for_admin,
        }
        if new_status:
            message["new_status"] = new_status
        # ✅ Include human-readable context so consumer builds rich messages
        if category_name:
            message["category_name"] = category_name
        if reporter_username:
            message["reporter_username"] = reporter_username

        channel.basic_publish(
            exchange='',
            routing_key='notifications',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
        logger.info(f"✅ Notification sent: user={user_id}, type={notification_type}, "
                    f"category={category_name}, reporter={reporter_username}")
    except Exception as e:
        logger.error(f"❌ Failed to send notification: {e}")