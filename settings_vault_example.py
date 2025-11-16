"""
Oracle Cloud Vault를 사용한 안전한 Django 설정
"""

from pathlib import Path
import os
import base64
import oci

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent


def get_secret_from_vault(secret_ocid):
    """
    Oracle Cloud Vault에서 시크릿 가져오기
    """
    try:
        # OCI 설정 로드 (인스턴스 프린시플 사용)
        signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
        secrets_client = oci.secrets.SecretsClient(config={}, signer=signer)
        
        # Secret 가져오기
        secret_bundle = secrets_client.get_secret_bundle(secret_ocid)
        base64_secret = secret_bundle.data.secret_bundle_content.content
        
        # Base64 디코딩
        secret_bytes = base64.b64decode(base64_secret)
        return secret_bytes.decode('utf-8')
    except Exception as e:
        print(f"Vault에서 시크릿을 가져오는데 실패: {e}")
        # 로컬 개발 환경에서는 환경변수 사용
        return None


# 환경 확인
IS_PRODUCTION = os.getenv('DJANGO_ENV') == 'production'

if IS_PRODUCTION:
    # 프로덕션: Oracle Cloud Vault 사용
    SECRET_KEY = get_secret_from_vault("ocid1.vaultsecret.oc1..your-secret-key-ocid")
    DB_PASSWORD = get_secret_from_vault("ocid1.vaultsecret.oc1..your-db-password-ocid")
    DEBUG = False
else:
    # 로컬 개발: 환경변수 사용
    from dotenv import load_dotenv
    load_dotenv()
    SECRET_KEY = os.getenv('SECRET_KEY')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DEBUG = True

# 나머지 설정
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',') if IS_PRODUCTION else ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'tuk_community'),
        'USER': os.getenv('DB_USER', 'root'),
        'PASSWORD': DB_PASSWORD,
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

# 보안 설정 (프로덕션)
if IS_PRODUCTION:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
