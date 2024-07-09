

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from users.models import Employee  # 실제 장고 앱 이름으로 수정해야 합니다.

def create_test_users():
    # 테스트용 사용자 데이터
    users_data = [
        {
            'email': 'test1@example.com',
            'employee_id': 'EMP001',
            'gender': Employee.MALE,
            'employment_status': Employee.ACTIVE,
            'job_title': 'Software Engineer',
            'phone_number': '123-456-7890',
            'start_date': timezone.now(),
            'end_date': None,
            'password': '123',  # 비밀번호 설정
            'is_staff': True,
            'is_superuser': True,  # 슈퍼유저 권한
        },
        {
            'email': 'test2@example.com',
            'employee_id': 'EMP002',
            'gender': Employee.FEMALE,
            'employment_status': Employee.ON_LEAVE,
            'job_title': 'Project Manager',
            'phone_number': '987-654-3210',
            'start_date': timezone.now(),
            'end_date': None,
            'password': '123',  # 비밀번호 설정
            'is_staff': True,
            'is_superuser': False,
        },
        {
            'email': 'test3@example.com',
            'employee_id': 'EMP003',
            'gender': Employee.FEMALE,
            'employment_status': Employee.ON_LEAVE,
            'job_title': 'Project Manager',
            'phone_number': '987-654-3210',
            'start_date': timezone.now(),
            'end_date': None,
            'password': '123',  # 비밀번호 설정
            'is_staff': True,
            'is_superuser': False,
        },
        # 추가적인 사용자 데이터를 필요에 맞게 추가할 수 있습니다.
    ]

    # 사용자 생성 및 저장
    for user_data in users_data:
        user = Employee.objects.create_user(**user_data)
        print(f'Created user: {user.email}')

# 함수 호출
create_test_users()