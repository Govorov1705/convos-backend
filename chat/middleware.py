from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


@database_sync_to_async
def get_user(id):
    try:
        user = User.objects.get(id=id)
        return user
    except User.DoesNotExist:
        return None
    

class JWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    def get_token(self, headers):
        cookies = dict(headers).get(b'cookie')

        if cookies:
            cookies = cookies.decode('UTF-8').split("; ")
            for cookie in cookies:
                if cookie.startswith('access'):
                    token = cookie.split('=')[1]
                    return token
        return None

    async def __call__(self, scope, receive, send):
        token = self.get_token(scope['headers'])
        if not token:
            return None
        
        try:
            user_id = AccessToken(token).get('user_id')
            user = await get_user(user_id)
            scope['user'] = user
        except Exception as e:
            print(e)
            return None
            
        return await self.app(scope, receive, send)
    