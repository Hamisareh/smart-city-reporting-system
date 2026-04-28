# notification_service/notification/middleware.py
import logging
import jwt
from datetime import datetime

logger = logging.getLogger(__name__)

# Utiliser la MÊME clé secrète que auth_service
SECRET_KEY = 'django-insecure-)8zcijxs&q$w&jv@d1$x9eff3#g2!+jq(w!8sl51&$z9t($if5'

class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.user_id = None
        request.user_role = None

        # Gérer OPTIONS (CORS)
        if request.method == 'OPTIONS':
            response = self.get_response(request)
            return response

        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                # Décoder le token sans vérification de signature (pour développement)
                # En production, utiliser la vérification complète
                payload = jwt.decode(token, options={'verify_signature': False})
                request.user_id = payload.get('user_id')
                request.user_role = payload.get('role', 'user')
                print(f"✅ [NOTIF] User extracted: {request.user_id} (role: {request.user_role})")
            except Exception as e:
                print(f"❌ [NOTIF] JWT decode error: {e}")
        
        # Fallback pour le développement
        if request.user_id is None and auth_header:
            # Essayer d'extraire sans décodage (dernier recours)
            import base64
            try:
                # Les tokens JWT ont 3 parties séparées par des points
                parts = token.split('.')
                if len(parts) >= 2:
                    # Décoder la payload (partie 2)
                    payload_part = parts[1]
                    # Ajouter padding si nécessaire
                    payload_part += '=' * (4 - len(payload_part) % 4)
                    payload_json = base64.b64decode(payload_part).decode('utf-8')
                    import json
                    payload = json.loads(payload_json)
                    request.user_id = payload.get('user_id')
                    request.user_role = payload.get('role', 'user')
                    print(f"🔓 [NOTIF] Extracted from base64: user_id={request.user_id}")
            except Exception as e:
                print(f"❌ [NOTIF] Base64 extraction failed: {e}")
        
        # Dernier recours pour le test
        if request.user_id is None:
            request.user_id = 1
            request.user_role = 'user'
            print(f"🔓 [NOTIF] Using default user_id=1")

        response = self.get_response(request)
        return response