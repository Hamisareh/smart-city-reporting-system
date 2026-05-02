# reports/middleware.py
import logging
import base64
import json

logger = logging.getLogger(__name__)

class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # ✅ تجاهل media / static / admin
        if (
            request.path.startswith('/media/') or
            request.path.startswith('/static/') or
            request.path.startswith('/admin/')
        ):
            return self.get_response(request)

        request.user_id = None
        request.user_role = None

        if request.method == 'OPTIONS':
            return self.get_response(request)

        auth_header = request.headers.get('Authorization')

        print(f"🔐 [Middleware] Path: {request.path}, Auth: {auth_header[:50] if auth_header else 'None'}...")

        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                parts = token.split('.')
                if len(parts) >= 2:
                    payload_part = parts[1]
                    payload_part += '=' * (4 - len(payload_part) % 4)
                    payload_json = base64.b64decode(payload_part).decode('utf-8')
                    payload = json.loads(payload_json)

                    request.user_id = payload.get('user_id')
                    request.user_role = payload.get('role', 'user')

                    print(f"✅ [Middleware] User: id={request.user_id}, role={request.user_role}")

            except Exception as e:
                print(f"❌ [Middleware] Decode error: {e}")

        return self.get_response(request)
        