import logging

from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from dotenv import load_dotenv
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.helpers import shorten_address

from .models import Account
from .serializers import AccountSerializer, CreateAccountSerializer

load_dotenv()
logger = logging.getLogger(__name__)


class AccountView(APIView):
    permission_classes = [IsAuthenticated]

    def upload_file(self, address, file: UploadedFile):
        # Save the file to S3
        file_path = f"profile_picture//{shorten_address(address)}/{file}"
        return default_storage.save(file_path, file)

    def post(self, request):
        """Create a new account or update existing one based on wallet address"""
        serializer = CreateAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        address = serializer.validated_data['email_address']

        # Try to find existing account or create new one
        account, created = Account.objects.get_or_create(
            address=address
        )

        # Update fields
        if 'username' in request.data:
            account.username = request.data['username']

        if 'profile_picture' in request.FILES:
            # If updating, delete the old picture url first from db then the file from S3
            if account.profile_picture_url:
                account.profile_picture_url.delete(save=False)
                # TODO: remove this line
                logger.info(f"Deleting file from S3: {account.profile_picture_url}")  # noqa: G004
                default_storage.delete(account.profile_picture_url)

            account.profile_picture_url = self.upload_file(address, request.FILES['profile_picture'])

        account.save()
        serializer = AccountSerializer(account)

        return Response({
            'data': serializer.data,
            'message': 'account created successfully!'
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def get(self, request):
        """Get account by address"""
        address = request.query_params.get('address')

        if not address:
            return Response({'error': 'Wallet address is required'},
                           status=status.HTTP_400_BAD_REQUEST)

        try:
            account = Account.objects.get(address=address)
            serializer = AccountSerializer(account)
            return Response(serializer.data)
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

