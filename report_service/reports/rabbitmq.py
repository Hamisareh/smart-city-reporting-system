# report_service/reports/rabbitmq.py

import pika
import json
import logging
import time

logger = logging.getLogger(__name__)

def send_notification(user_id, report_id, notification_type, new_status=None, is_for_admin=False):
    """Envoyer une notification via RabbitMQ"""
    try:
        # Connexion avec retry
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
        
        # Déclarer la queue
        channel.queue_declare(queue='notifications', durable=True)
        
        message = {
            "user_id": user_id,
            "report_id": report_id,
            "type": notification_type,
            "is_for_admin": is_for_admin,  # ✅ إضافة هذا الحقل
        }
        if new_status:
            message["new_status"] = new_status
        
        channel.basic_publish(
            exchange='',
            routing_key='notifications',
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,
            )
        )
        connection.close()
        logger.info(f"✅ Notification sent: user={user_id}, type={notification_type}, is_for_admin={is_for_admin}")
    except Exception as e:
        logger.error(f"❌ Failed to send notification: {e}")