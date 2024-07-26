# 루미나리 벡엔드

[![Postman](https://img.shields.io/badge/Postman-FF6C37?style=flat-square&logo=Postman&logoColor=white)](https://aivle-5-16.postman.co/workspace/Luminari~98554664-d63c-44f0-a043-a9d9b0159655/collection/11122919-e5e0cddb-a5c2-42d9-aa93-4d7830f3e7c5?active-environment=11122919-8185b909-67ba-40d4-b97a-878b1a1302b6)

스마트 HRM 플랫폼, 루미나리 백엔드 소스코드입니다.

## 시작 가이드

### 요구사항
* Python 3.11
* PDM (https://pdm-project.org/en/latest/)
* pre-commit (https://pre-commit.com/#introduction)

### 프로젝트 설정

#### PDM 설정

1. 설치 (https://pdm-project.org/latest/#installation)

   ```
   # Linux / Mac (리눅스 / 맥)
   curl -sSL https://pdm-project.org/install-pdm.py | python3 -

   # Windows (윈도우)
   (Invoke-WebRequest -Uri https://pdm-project.org/install-pdm.py -UseBasicParsing).Content | py -
   ```

2. 프로젝트 폴더에서 파이썬 패키지 설치
   ```
   pdm install
   ```

3. 프로젝트에 새로운 패키지를 설치 / 삭제하고 싶을 시,
   ```
   # 설치
   pdm add <패키지 이름>

   # 삭제
   pdm remove <패키지 이름>
   ```

4. 가상 환경 실행
   ```
   # Mac
   eval $(pdm venv activate in-project)

   # Window
   .venv\Scripts\activate
   ```

#### pre-commit 설정
Git hook을 통해 커밋 전에 코드 스타일 등 간단한 코드 리뷰를 자동화해주는 프레임워크입니다.
1. 설치
   ```
   pre-commit install
   ```

#### Django 로컬 서버 초기 설정 및 시작
1. `.env.example`을 기반으로 `.env.local` 파일 작성
```
SECRET_KEY = ""
ALLOWED_HOSTS = ""
DEBUG = ""
CSRF_TRUSTED_ORIGINS=""
NAVER_OCR_SECRET_KEY=""
DB_NAME=""
DB_USER=""
DB_PASSWORD=""
DB_HOST=""
DB_PORT=""
OPENAI_API_KEY=""
SUPABASE_URL=""
SUPABASE_KEY=""
EMAIL_HOST_USER=""
EMAIL_HOST_PASSWORD=""
```

3. DB 마이그레이션 및 서버 시작
```
cd src
python manage.py makemigrations
python manage.py migrate
python manage.py createcustomgroup
python manage.py createptotype
python manage.py runserver
```

### 개발 중 주의사항
* __(어느 정도 안정화될 때까지) Pull Request (PR)을 통해서만 main 브랜치에 머지하기!__
