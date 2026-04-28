# reports/middleware.py
import logging
import base64
import json

logger = logging.getLogger(__name__)

class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.user_id = None
        request.user_role = None

        # Gérer OPTIONS (CORS preflight)
        if request.method == 'OPTIONS':
            response = self.get_response(request)
            return response

        auth_header = request.headers.get('Authorization')
        print(f"🔐 [Middleware] Path: {request.path}, Auth: {auth_header[:50] if auth_header else 'None'}...")

        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                # Décoder le token JWT (sans vérifier la signature)
                parts = token.split('.')
                if len(parts) >= 2:
                    # Décoder la payload
                    payload_part = parts[1]
                    # Ajouter le padding
                    payload_part += '=' * (4 - len(payload_part) % 4)
                    payload_json = base64.b64decode(payload_part).decode('utf-8')
                    payload = json.loads(payload_json)
                    
                    request.user_id = payload.get('user_id')
                    request.user_role = payload.get('role', 'user')
                    print(f"✅ [Middleware] User: id={request.user_id}, role={request.user_role}")
                    
            except Exception as e:
                print(f"❌ [Middleware] Decode error: {e}")
        
        # ⚠️ IMPORTANT: Ne pas mettre de fallback par défaut !
        # Si pas de user_id, laisser None (la permission refusera)

        response = self.get_response(request)
        return response