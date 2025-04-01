import logging

# from urllib.parse import urlparse
# from django.core.files.storage import default_storage
from django.db import transaction
from django.db.utils import DatabaseError
from dotenv import load_dotenv
from rest_framework import status

# from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from common.helpers import format_file_url, remove_file, upload_file

from .models import Account
from .serializers import AccountSerializer, CreateAccountSerializer

load_dotenv()
logger = logging.getLogger(__name__)


class WalletTokenObtainView(APIView):
    permission_classes = []
    def post(self, request):
        address = request.data.get('address')

        if not address:
            return Response({
                "error": "address: This field is required.",
                "success": False
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                user, _ = Account.objects.get_or_create(address=address)

                # Generate tokens for the user
                refresh = RefreshToken.for_user(user)

                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'success': True
                })

        except DatabaseError as e:
            return Response({
                "error": str(e),
                "success": False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AccountView(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = []

    def post(self, request):
        """Create a new account or update existing one based on wallet address"""
        serializer = CreateAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        logger.info("here with no problem")
        address = serializer.validated_data['address']

        # Try to find existing account or create new one
        try :
            with transaction.atomic():
                account, created = Account.objects.get_or_create(
                    address=address
                )
        except DatabaseError as e:
            return Response({
                "error": str(e),
                "success": False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Update fields
        if 'username' in request.data:
            account.username = request.data['username']

        if 'profile_picture' in request.FILES:
            # If updating, delete the old picture url first from db then the file from supabase bucket
            if account.profile_picture_url:
                data = remove_file(account.profile_picture_url)
                if not data:
                    logger.error(f"Failed to remove file: {account.profile_picture_url}")  # noqa: G004
                    return Response(
                        {'error': 'Failed to remove profile picture'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

            try:
                account.profile_picture_url = upload_file(request.FILES['profile_picture'])
            except Exception as e:
                logger.exception(f"Failed to upload file: {e}")  # noqa: G004, TRY401
                return Response(
                    {'error': 'Failed to upload profile picture'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        account.save()
        serializer = AccountSerializer(account)

        return Response({
            'data': serializer.data,
            'message': 'account created successfully!'
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        """Get account by address"""
        address = request.query_params.get('address')

        if not address:
            return Response({'error': 'Wallet address is required'},
                           status=status.HTTP_400_BAD_REQUEST)

        try:
            account = Account.objects.get(address=address)
            serializer = AccountSerializer(account)

            serializer.data['profile_picture_url'] = format_file_url(account.profile_picture_url)
            return Response(
                status= status.HTTP_200_OK,
                data={
                    'address': serializer.data['address'],
                    'username': serializer.data['username'],
                    'profile_picture_url': format_file_url(account.profile_picture_url),
                    'created_at': serializer.data['created_at'],
                    'updated_at': serializer.data['updated_at']
                }
            )
        except Account.DoesNotExist:
            return Response({'error': 'Account not found'},
                           status=status.HTTP_404_NOT_FOUND)

#TODO: Update profile
    # def put(self, request, *args, **kwargs):
    #     """Update an existing account"""
    #     address = request.data.get('address')

    #     if not address:
    #         return Response({'error': 'Wallet address is required'},
    #                        status=status.HTTP_400_BAD_REQUEST)

    #     try:
    #         account = Account.objects.get(address=address)

    #         # Update fields
    #         if 'username' in request.data:
    #             account.username = request.data['username']

    #         if 'profile_picture' in request.FILES:
    #             if account.profile_picture:
    #                 account.profile_picture.delete(save=False)

    #             account.profile_picture = request.FILES['profile_picture']

    #         account.save()

    #         serializer = AccountSerializer(account)
    #         return Response(serializer.data)

    #     except Account.DoesNotExist:
    #         return Response({'error': 'Account not found'},
    #                        status=status.HTTP_404_NOT_FOUND)

