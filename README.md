# TukCommunity Backend

한국기술교육대학교 커뮤니티 백엔드 - Django REST Framework

## 🔐 Oracle Cloud Vault 설정 가이드

### 1단계: Vault 생성

1. **Oracle Cloud Console** → **Identity & Security** → **Vault**
2. **Create Vault** 클릭
   - Name: `Tukether-secret`
   - Compartment: `mocha6126 (root)`
   - ⬜ Make it a virtual private vault: 체크 안 함 (무료 티어)
3. **Create Vault** 클릭

### 2단계: Master Encryption Key 생성

1. 생성된 Vault 클릭 → **Master Encryption Keys** 탭
2. **Create Key** 클릭
   - Name: `tukether-master-key`
   - Protection Mode: `Software` (무료 티어)
   - Key Shape: `AES`
   - Key Shape Length: `256 bits`
3. **Create Key** 클릭

### 3단계: Secret 생성

#### Secret 1: Django SECRET_KEY

1. Vault → **Secrets** 탭 → **Create Secret**
   - Name: `django-secret-key`
   - Encryption Key: `tukether-master-key`
   - Secret Type Template: `Plain-Text`
   - Secret Contents: Django SECRET_KEY 값 입력
2. 생성 후 **OCID 복사** (예: `ocid1.vaultsecret.oc1...`)

#### Secret 2: DB Password

1. **Create Secret** 다시 클릭
   - Name: `db-password`
   - Encryption Key: `tukether-master-key`
   - Secret Type Template: `Plain-Text`
   - Secret Contents: MySQL 비밀번호 입력
2. 생성 후 **OCID 복사**

### 4단계: Instance Principal 설정

#### Dynamic Group 생성

1. **Identity & Security** → **Dynamic Groups**
2. **Create Dynamic Group**
   - Name: `tukether-instances`
   - Matching Rules:
     ```
     instance.compartment.id = 'your-compartment-ocid'
     ```

#### Policy 생성

1. **Identity & Security** → **Policies**
2. **Create Policy**
   - Name: `tukether-vault-policy`
   - Compartment: `mocha6126 (root)`
   - Policy Statements:
     ```
     Allow dynamic-group tukether-instances to read secret-bundles in compartment mocha6126
     Allow dynamic-group tukether-instances to read secrets in compartment mocha6126
     ```

### 5단계: 인스턴스 배포

```bash
# 1. 인스턴스 접속
ssh -i ~/.ssh/your-key.pem ubuntu@your-instance-ip

# 2. 프로젝트 클론
cd /home/ubuntu
git clone https://github.com/Tukether/BE.git
cd BE

# 3. .env.production 파일 생성
cp .env.production.example .env.production
nano .env.production

# Vault Secret OCID 입력:
# VAULT_SECRET_KEY_OCID=ocid1.vaultsecret.oc1...
# VAULT_DB_PASSWORD_OCID=ocid1.vaultsecret.oc1...

# 4. Vault 설정 스크립트 실행
chmod +x setup_vault.sh
./setup_vault.sh

# 5. 서버 실행
export DJANGO_ENV=production
python manage.py runserver 0.0.0.0:8000
```

## 🛠️ 로컬 개발 환경

로컬에서는 `.env` 파일을 사용합니다.

```bash
# 1. 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 패키지 설치
pip install -r requirements.txt

# 3. .env 파일 생성
cp .env.example .env
# .env 파일 편집하여 SECRET_KEY, DB_PASSWORD 등 입력

# 4. MySQL 데이터베이스 생성
mysql -u root -p
CREATE DATABASE tuk_community CHARACTER SET utf8mb4;

# 5. 마이그레이션
python manage.py migrate

# 6. 서버 실행
python manage.py runserver
```

## 📋 환경변수 구조

### 로컬 개발 (.env)
```env
SECRET_KEY=your-secret-key
DB_PASSWORD=your-password
DEBUG=True
```

### 프로덕션 (.env.production)
```env
DJANGO_ENV=production
VAULT_SECRET_KEY_OCID=ocid1.vaultsecret...
VAULT_DB_PASSWORD_OCID=ocid1.vaultsecret...
ALLOWED_HOSTS=your-domain.com,your-ip
```

## 🔍 문제 해결

### Vault 연결 실패 시

1. **Instance Principal 확인**
   ```bash
   # 인스턴스에서 실행
   curl http://169.254.169.254/opc/v2/instance/
   ```

2. **Dynamic Group 확인**
   - 인스턴스가 Dynamic Group에 포함되었는지 확인

3. **Policy 확인**
   - Policy가 올바른 Compartment에 적용되었는지 확인

4. **Secret OCID 확인**
   - `.env.production` 파일의 OCID가 정확한지 확인

### MySQL 연결 실패 시

```bash
# MySQL 서비스 확인
sudo systemctl status mysql

# 데이터베이스 확인
mysql -u root -p
SHOW DATABASES;
```

## 📚 기술 스택

- **Backend**: Django 5.1.3
- **API**: Django REST Framework 3.14.0
- **Database**: MySQL
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Security**: Oracle Cloud Vault
- **Server**: Gunicorn

## 🤝 팀원 가이드

1. 프로젝트 클론
2. `.env.example`을 복사하여 `.env` 생성
3. 본인의 로컬 DB 정보 입력
4. `pip install -r requirements.txt`
5. `python manage.py migrate`

**주의**: `.env` 파일은 절대 Git에 커밋하지 마세요!
