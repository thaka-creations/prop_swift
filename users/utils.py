import jwt
import pytz
import requests
from datetime import timedelta, datetime
from django.db import transaction
from django.conf import settings
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from rest_framework import authentication, status, exceptions
from oauth2_provider.generators import generate_client_id, generate_client_secret
from oauth2_provider.models import get_application_model
from oauth2_provider.oauth2_backends import get_oauthlib_core
from .models import User

CALLBACK_URL = settings.SERVICES_URLS['CALLBACK_URL']


class ApplicationUser:

    @staticmethod
    def create_application_user(user):
        with transaction.atomic():
            username = user.username
            try:
                data = {
                    'client_id': generate_client_id(),
                    'client_secret': generate_client_secret(),
                    'client_type': 'confidential',
                    'skip_authorization': False,
                    'name': username,
                    'user': user,
                    'redirect_uris': '',
                    'authorization_grant_type': 'password'
                }

                get_application_model().objects.create(**data)
            except Exception as e:
                raise exceptions.APIException(e)

    @staticmethod
    def get_client_details(payload):
        url = CALLBACK_URL + 'o/token/'
        resp = requests.post(url, data=payload)

        if resp.status_code == 200:
            return resp.json()
        return False

    @staticmethod
    def logout(token, user_id):
        try:
            user_details = get_application_model().objects.get(user_id=user_id)
        except (ValidationError, ObjectDoesNotExist):
            return False, "User does not exist"
        revoke_url = CALLBACK_URL + 'o/revoke_token/'
        payload_data = {
            'token': token,
            'client_id': user_details.client_id,
            'client_secret': user_details.client_secret,
        }
        response = requests.post(revoke_url, data=payload_data)
        if response.status_code == 200:
            return True, "Logout Successful"
        return False, "Could Not Log you Out"

    @staticmethod
    def get_user_roles(user):
        user_roles = [role.name for role in user.groups.all()]
        return user_roles

    def generate_jwt_token(self, user):
        timezone = pytz.timezone(settings.TIME_ZONE)
        time = datetime.now(tz=timezone)
        access_token_expiry = time + timedelta(seconds=int(settings.ACCESS_TOKEN_EXPIRY))

        payload = {
            'user': str(user.id),
            'roles': self.get_user_roles(user),
            'exp': access_token_expiry,
            'iat': time,
            "aud": "urn:jst"
        }
        encoded = jwt.encode(payload, settings.TOKEN_SECRET_KEY, algorithm='HS512')
        return encoded


class SystemAuthentication(authentication.BaseAuthentication):

    def __init__(self):
        self.authentication_header_prefix = 'Bearer'

    @staticmethod
    def get_jwt_header(request):
        auth = request.headers.get('JWTAUTH', b'')
        return auth

    def authenticate(self, request):
        request.user = None
        oauthlib_core = get_oauthlib_core()
        valid, r = oauthlib_core.verify_request(request, scopes=[])

        if not valid:
            return None

        jwt_header = self.get_jwt_header(request).split()
        header_prefix = self.authentication_header_prefix.lower()
        if not jwt_header:
            return None
        if len(jwt_header) == 1 or len(jwt_header) > 2:
            raise exceptions.NotAuthenticated(
                {"message": "Could Not Authenticate User", "status_code": status.HTTP_401_UNAUTHORIZED}
            )

        try:
            prefix = jwt_header[0]
            token = jwt_header[1]
        except Exception:
            raise exceptions.NotAcceptable(
                {"message": "No Token Present", "status_code": status.HTTP_406_NOT_ACCEPTABLE})

        if prefix.lower() != header_prefix:
            return None
        return self.authenticate_credentials(request, token)

    @staticmethod
    def authenticate_credentials(request, token):
        try:
            decoded = jwt.decode(token, settings.TOKEN_SECRET_KEY, audience="urn:jst", algorithms=['HS512'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed(
                {"message": "User Logged Out.Please Try Again",
                 "status_code":
                     status.HTTP_401_UNAUTHORIZED})

        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed(
                {"message": "Please Login Again",
                 "status_code":
                     status.HTTP_401_UNAUTHORIZED})

        except Exception as e:
            print(e)
            raise exceptions.AuthenticationFailed(
                {"message": "Invalid Verification",
                 "status_code": status.HTTP_401_UNAUTHORIZED})

        try:
            user = User.objects.get(id=decoded['user'])
        except User.DoesNotExist:

            raise exceptions.AuthenticationFailed(
                {"message": "Invalid User",
                 "status_code":
                     status.HTTP_401_UNAUTHORIZED})
        return user, token
