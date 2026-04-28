# notification_service/notification/consumer.py

import pika
import json
import time
import os
import sys
from .models import Notification
import logging

logger = logging.getLogger(__name__)

def start_consumer():
    rabbitmq_host = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
    rabbitmq_port = int(os.environ.get('RABBITMQ_PORT', 5672))
    
    # Infinite reconnection loop
    while True:
        try:
            _run_consumer(rabbitmq_host, rabbitmq_port)
        except KeyboardInterrupt:
            print("👋 [Consumer] Shutting down...")
            sys.stdout.flush()
            break
        except Exception as e:
            print(f"❌ [Consumer] Consumer crashed: {e}")
            sys.stdout.flush()
            print(f"🔄 [Consumer] Reconnecting in 10 seconds...")
            sys.stdout.flush()
            time.sleep(10)

def _run_consumer(rabbitmq_host, rabbitmq_port):
    print(f"🔌 [Consumer] Trying to connect to RabbitMQ at {rabbitmq_host}:{rabbitmq_port}...")
    sys.stdout.flush()
    
    connection = None
    max_retries = 30
    retry_count = 0
    
    while connection is None and retry_count < max_retries:
        try:
            credentials = pika.PlainCredentials('guest', 'guest')
            parameters = pika.ConnectionParameters(
                host=rabbitmq_host,
                port=rabbitmq_port,
                credentials=credentials,
                heartbeat=60,
                blocked_connection_timeout=300,
                connection_attempts=10,
                retry_delay=5
            )
            connection = pika.BlockingConnection(parameters)
            print(f"✅ [Consumer] Connected to RabbitMQ at {rabbitmq_host}:{rabbitmq_port}")
            sys.stdout.flush()
        except Exception as e:
            print(f"❌ [Consumer] Failed to connect (attempt {retry_count+1}/{max_retries}): {e}")
            sys.stdout.flush()
            retry_count += 1
            if retry_count < max_retries:
                time.sleep(5)
    
    if connection is None:
        print("❌ [Consumer] Could not connect to RabbitMQ after all retries")
        sys.stdout.flush()
        return
    
    channel = connection.channel()
    channel.queue_declare(queue='notifications', durable=True)
    
    def callback(ch, method, properties, body):
        try:
            data = json.loads(body)
            print(f"📬 [Consumer] Processing: {data}")
            sys.stdout.flush()
            
            # ✅ Messages en français
            if data["type"] == "REPORT_CREATED":
                # Pour l'utilisateur normal
                msg = "✅ Votre signalement a été créé avec succès"
                
            elif data["type"] == "NEW_REPORT_CREATED":
                # Pour l'administrateur
                msg = f"📝 Nouveau signalement #{data['report_id']} - En attente de traitement"
                
            elif data["type"] == "REPORT_STATUS_CHANGED":
                # Pour le propriétaire du signalement
                status_text = {
                    'pending': 'en attente',
                    'in_progress': 'en cours de traitement',
                    'resolved': 'résolu'
                }.get(data.get('new_status'), data.get('new_status', 'mis à jour'))
                msg = f"🔄 Le statut de votre signalement a été mis à jour : {status_text}"
                
            elif data["type"] == "REPORT_ASSIGNED":
                # Si vous avez ce type
                msg = f"👤 Un administrateur a été assigné à votre signalement #{data['report_id']}"
                
            elif data["type"] == "REPORT_COMMENT":
                # Si vous avez ce type
                msg = f"💬 Nouveau commentaire sur votre signalement #{data['report_id']}"
                
            else:
                msg = f"📢 Mise à jour: {data.get('type', 'Notification')}"
            
            # ✅ Vérifier d'ignorer les notifications admin pour REPORT_CREATED
            if data.get("is_for_admin", False) and data["type"] == "REPORT_CREATED":
                print(f"⚠️ Ignoring admin notification for REPORT_CREATED type")
                sys.stdout.flush()
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
            
            # Sauvegarder la notification dans la base de données
            try:
                notification = Notification.objects.create(
                    user_id=data["user_id"],
                    report_id=data.get("report_id"),
                    type=data["type"],
                    message=msg
                )
                print(f"✅ [Consumer] Notification saved: id={notification.id}, user={data['user_id']}, type={data['type']}")
                sys.stdout.flush()
            except Exception as db_error:
                print(f"❌ [Consumer] Database error: {db_error}")
                sys.stdout.flush()
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                return
            
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            print(f"❌ [Consumer] Error processing message: {e}")
            sys.stdout.flush()
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='notifications', on_message_callback=callback)
    
    print("🚀 [Consumer] Notification Service listening for messages...")
    sys.stdout.flush()
    
    try:
        channel.start_consuming()
    except pika.exceptions.ConnectionClosedByBroker as e:
        print(f"⚠️ [Consumer] Connection closed by broker: {e}")
        sys.stdout.flush()
        connection.close()
        raise
    except pika.exceptions.StreamLostError as e:
        print(f"⚠️ [Consumer] Stream lost: {e}")
        sys.stdout.flush()
        connection.close()
        raise
    except Exception as e:
        print(f"❌ [Consumer] Unexpected error: {e}")
        sys.stdout.flush()
        if connection and not connection.is_closed:
            connection.close()
        raise