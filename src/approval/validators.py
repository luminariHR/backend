from rest_framework import serializers


def validate_file_size(value):
    max_size = 10 * 1024 * 1024
    if value.size > max_size:
        raise serializers.ValidationError("파일이 30MB을 초과할 수 없습니다.")
