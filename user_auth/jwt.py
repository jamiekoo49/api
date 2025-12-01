from datetime import datetime

import jwt
from django.contrib.auth import authenticate, get_user_model
from jwt import DecodeError
from jwt.algorithms import RSAAlgorithm
from rest_framework_jwt.settings import api_settings

from accounts.models import Athlete, Coach


def get_username_from_payload_handler(payload):
    username = payload.get("email")
    authenticate(remote_user=username)
    return username


def cognito_jwt_decode_handler(token):
    """
    To verify the signature of an Amazon Cognito JWT, first search for the public key with a key ID that
    matches the key ID in the header of the token. (c)
    https://aws.amazon.com/premiumsupport/knowledge-center/decode-verify-cognito-json-token/

    Almost the same as default 'rest_framework_jwt.utils.jwt_decode_handler', but 'secret_key' feature is skipped
    """
    options = {"verify_exp": api_settings.JWT_VERIFY_EXPIRATION}
    unverified_header = jwt.get_unverified_header(token)
    if "kid" not in unverified_header:
        raise DecodeError("Incorrect authentication credentials.")

    kid = jwt.get_unverified_header(token)["kid"]
    try:
        # pick a proper public key according to `kid` from token header
        public_key = RSAAlgorithm.from_jwk(api_settings.JWT_PUBLIC_KEY[kid])
    except KeyError:
        # in this place we could refresh cached jwks and try again https://immoatlas.atlassian.net/browse/DEV-69
        raise DecodeError("Can't find proper public key in jwks")

    claims = jwt.decode(
        token,
        public_key,
        api_settings.JWT_VERIFY,
        options=options,
        leeway=api_settings.JWT_LEEWAY,
        audience=api_settings.JWT_AUDIENCE,
        issuer=api_settings.JWT_ISSUER,
        algorithms=[api_settings.JWT_ALGORITHM],
    )

    if not claims:
        raise DecodeError("Incorrect authentication credentials.")

    User = get_user_model()
    email = claims.get("email", "")
    account_type = claims.get("custom:account_type")
    first_name = claims.get("given_name", "")
    last_name = claims.get("family_name", "")

    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            "first_name": first_name,
            "last_name": last_name,
        },
    )

    user.last_login = datetime.now()
    user.save()

    if created:
        if account_type == "athlete":
            Athlete.objects.create(user=user)
        elif account_type == "coach":
            Coach.objects.create(user=user)
        elif account_type == "admin":
            user.is_staff = True
            user.is_superuser = True
            user.save()
    return claims
