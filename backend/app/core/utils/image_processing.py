import base64


def image_bytes_to_base64(image_bytes: bytes) -> str:
    """
    Convert raw image bytes to base64 string
    suitable for vision model inline_data.
    """
    return base64.b64encode(image_bytes).decode("utf-8")
