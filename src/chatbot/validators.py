from django.core.exceptions import ValidationError


def validate_file_type(file):
    valid_mime_types = ["application/pdf"]
    file_mime_type = file.content_type
    if file_mime_type not in valid_mime_types:
        raise ValidationError("Unsupported file type.")


def validate_file_size(file):
    max_file_size = 20 * 1024 * 1024  # 20MB
    if file.size > max_file_size:
        raise ValidationError("File size exceeds the maximum limit of 20MB.")
