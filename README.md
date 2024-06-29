# 루미나리 벡엔드
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
   $ curl -sSL https://pdm-project.org/install-pdm.py | python3 -

   # Windows (윈도우)
   $ (Invoke-WebRequest -Uri https://pdm-project.org/install-pdm.py -UseBasicParsing).Content | py -
   ```

2. 프로젝트 폴더에서 파이썬 패키지 설치
   ```
   $ pdm install
   ```

3. 프로젝트에 새로운 패키지를 설치 / 삭제하고 싶을 시,
   ```
   # 설치
   $ pdm add <패키지 이름>

   # 삭제
   $ pdm remove <패키지 이름>
   ```

4. 가상 환경 실행
   ```
   $ eval $(pdm venv activate in-project)
   ```

#### pre-commit 설정
Git hook을 통해 커밋 전에 코드 스타일 등 간단한 코드 리뷰를 자동화해주는 프레임워크입니다.
1. 설치
   ```
   pre-commit install
   ```
