import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

def shorten_address(address: str, prefix: int = 6, suffix: int = 6) -> str:
    if len(address) < (prefix + suffix + 2):
        return address
    return f"{address[:2 + prefix]}...{address[-suffix:]}"


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
    headers = {'Authorization': f'Bearer {settings.PLUNK_API_KEY}', 'Content-Type': 'application/json'}

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
