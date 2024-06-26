from django.contrib.auth import login
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .service import GoogleRawFlowService
from .serializers import GoogleAPISerializer
from .models import OAuthSession, User


class PublicAPI(APIView):
    authentication_classes = ()
    permission_classes = ()


class GoogleRedirectAPI(PublicAPI):
    def get(self, request, *args, **kwargs):
        google_flow = GoogleRawFlowService()
        authorization_url, state = google_flow.get_authorization_url()
        oauth_session = OAuthSession.objects.create(session=state)
        return redirect(authorization_url)


class GoogleAPI(PublicAPI):
    def get(self, request, *args, **kwargs):
        serializer = GoogleAPISerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)

        validate_data = serializer.validated_data

        code = validate_data.get("code")
        error = validate_data.get("error")
        state = validate_data.get("state")

        if error is not None:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        if code is None or state is None:
            return Response(
                {"error": "code and state are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            oauth_session = OAuthSession.objects.get(session=state)
        except OAuthSession.DoesNotExist:
            return Response(
                {"error": "Session state not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        oauth_session.delete()

        google_flow = GoogleRawFlowService()
        google_tokens = google_flow.get_tokens(code=code)

        id_token_decoded = google_tokens.decode_id_token()
        user_info = google_flow.get_user_info(google_tokens=google_tokens)

        user_email = id_token_decoded["email"]
        user = User.objects.filter(email=user_email).first()

        if user is None:
            last_name = (
                user_info.get("family_name") if user_info.get("family_name") else ""
            )
            new_user = User.objects.create_user(
                email=user_email,
                first_name=user_info["given_name"],
                last_name=last_name,
            )

            refresh = RefreshToken.for_user(new_user)
            result = {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": str(new_user),
            }
            return Response(result)

        login(request, user)
        refresh = RefreshToken.for_user(user)
        result = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": str(user),
        }

        return Response(result)
