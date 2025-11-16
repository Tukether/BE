"""
Django settings for TukCommunityBE project.
Vault를 사용한 안전한 설정
"""

from pathlib import Path
import os
import base64

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# 환경 확인 (로컬 vs 프로덕션)
IS_PRODUCTION = os.getenv('DJANGO_ENV') == 'production'


def get_secret_from_vault(secret_ocid):
    """Oracle Cloud Vault에서 시크릿 가져오기"""
    try:
        import oci
        # Instance Principal 인증 (EC2 인스턴스에서 자동)
        signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
        secrets_client = oci.secrets.SecretsClient(config={}, signer=signer)
        
        # Secret 가져오기
        secret_bundle = secrets_client.get_secret_bundle(secret_ocid)
        base64_secret = secret_bundle.data.secret_bundle_content.content
        
        # Base64 디코딩
        secret_bytes = base64.b64decode(base64_secret)
        return secret_bytes.decode('utf-8')
    except Exception as e:
        print(f"⚠️  Vault에서 시크릿 가져오기 실패: {e}")
        return None


# 환경별 설정
if IS_PRODUCTION:
    # 🔐 프로덕션: Oracle Cloud Vault 사용
    # Vault에서 Secret을 생성한 후 OCID를 여기에 입력하세요
    SECRET_KEY = get_secret_from_vault(os.getenv('VAULT_SECRET_KEY_OCID'))
    DB_PASSWORD = get_secret_from_vault(os.getenv('VAULT_DB_PASSWORD_OCID'))
    DEBUG = False
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')
else:
    # 🛠️  로컬 개발: .env 파일 사용
    from dotenv import load_dotenv
    load_dotenv()
    SECRET_KEY = os.getenv('SECRET_KEY')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DEBUG = True
    ALLOWED_HOSTS = ['*']


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'BE',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'TukCommunityBE.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'TukCommunityBE.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.mysql'),
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

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework 설정
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}

# CORS 설정
if IS_PRODUCTION:
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')
    CORS_ALLOW_CREDENTIALS = True
else:
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOW_CREDENTIALS = True

# 보안 설정 (프로덕션)
if IS_PRODUCTION:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
