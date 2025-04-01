import logging
from uuid import uuid4

import requests
from django.core.files.uploadedfile import UploadedFile

from yapa_backend.settings import SUPABASE_BUCKET, SUPABASE_URL, SUPERBASE_CLIENT

logger = logging.getLogger(__name__)

PLUNK_API_KEY= "your_plunk_api_key"  # TODO: Replace with your actual Plunk API key

class FileUploadError(Exception):
    """Custom exception for file upload errors."""

def shorten_address(address: str, prefix: int = 6, suffix: int = 6) -> str:
    if len(address) < (prefix + suffix + 2):
        return address
    return f"{address[:2 + prefix]}...{address[-suffix:]}"

def upload_file(file: UploadedFile) -> str:
        file_ext = file.name.split(".")[-1]
        file_name = f"{uuid4()}.{file_ext}"

        file_bytes = file.read()

        response = SUPERBASE_CLIENT.storage.from_(SUPABASE_BUCKET).upload(
             file_name, file_bytes, {"content-type": file.content_type}
        )

        if not response:
            msg = "Failed to upload avatar"
            raise FileUploadError(msg)

        return file_name

def remove_file(file_name: str):
     data = SUPERBASE_CLIENT.storage.from_(SUPABASE_BUCKET).remove([file_name])
     logger.info(f"File removed: {data}")  # noqa: G004
     return data

# TODO: when giving frontend :- f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}
def format_file_url(file_name: str) -> str:
    """
    Format the file URL for Supabase storage.

    Args:
        file_name (str): The name of the file stored in Supabase.

    Returns:
        str: The formatted URL for the file.
    """
    return f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{file_name}"

def send_email(to: str, subject: str, html: str) -> dict:
    """
    Send an email using the Plunk API.

    Args:
        to (str or list): The recipient's email address(es).
        subject (str): The subject of the email.
        html (str): The HTML content of the email.
    """
    logger.info(f'Sending email to {to} with subject: {subject}')  # noqa: G004

    url = 'https://api.useplunk.com/v1/send'
    headers = {'Authorization': f'Bearer {PLUNK_API_KEY}', 'Content-Type': 'application/json'}

    payload = {
        'subject': subject,
        'body': html,
        'to': to,
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        logger.info(f'Email sent successfully to {to}')  # noqa: G004
    except requests.RequestException:
        logger.exception('Failed to send email')
