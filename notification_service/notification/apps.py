# notification_service/notification/apps.py
from django.apps import AppConfig
import threading
import os
import sys
import time

class NotificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notification'
    
    def ready(self):
        # Only run in the main process, not in the reloader
        if os.environ.get('RUN_MAIN', 'false') == 'true':
            # Give Django time to fully initialize
            time.sleep(2)
            
            # Check if we should start the consumer
            # Avoid starting multiple consumers in development
            if not hasattr(self, '_consumer_started'):
                self._consumer_started = True
                print("🚀 [Django] Starting RabbitMQ consumer...")
                sys.stdout.flush()
                
                # Start consumer in a separate daemon thread
                consumer_thread = threading.Thread(
                    target=self._run_consumer,
                    daemon=True,
                    name="RabbitMQConsumer"
                )
                consumer_thread.start()
    
    def _run_consumer(self):
        """Wrapper to run consumer with retry logic"""
        max_retries = 5
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                from . import consumer
                consumer.start_consumer()
                break  # If successful, this will run until interrupted
            except Exception as e:
                print(f"❌ Failed to start consumer (attempt {attempt + 1}/{max_retries}): {e}")
                sys.stdout.flush()
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    print("❌ Could not start consumer after all retries")
                    sys.stdout.flush()