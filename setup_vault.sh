#!/bin/bash
# Oracle Cloud Vault 연동 설정 스크립트
# Oracle Cloud 인스턴스에서 실행하세요

set -e

echo "🔐 Oracle Cloud Vault 연동 설정 시작..."

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. 현재 디렉토리 확인
if [ ! -f "manage.py" ]; then
    echo -e "${RED}❌ manage.py 파일을 찾을 수 없습니다. Django 프로젝트 디렉토리에서 실행하세요.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Django 프로젝트 디렉토리 확인${NC}"

# 2. .env.production 파일 확인
if [ ! -f ".env.production" ]; then
    echo -e "${YELLOW}⚠️  .env.production 파일이 없습니다. 생성합니다...${NC}"
    cp .env.production.example .env.production
    echo -e "${YELLOW}📝 .env.production 파일을 편집하여 Vault Secret OCID를 입력하세요!${NC}"
    echo -e "${YELLOW}   편집: nano .env.production${NC}"
    exit 1
fi

echo -e "${GREEN}✅ .env.production 파일 확인${NC}"

# 3. 가상환경 확인
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  가상환경이 없습니다. 생성합니다...${NC}"
    python3 -m venv venv
fi

echo -e "${GREEN}✅ 가상환경 활성화${NC}"
source venv/bin/activate

# 4. 패키지 설치
echo -e "${YELLOW}📦 패키지 설치 중...${NC}"
pip install -r requirements.txt

# 5. 환경변수 로드
source .env.production

# 6. Vault 연결 테스트
echo -e "${YELLOW}🔍 Vault 연결 테스트...${NC}"
python3 << EOF
import os
import sys
os.environ['DJANGO_ENV'] = 'production'

try:
    from TukCommunityBE.settings import SECRET_KEY, DB_PASSWORD
    
    if SECRET_KEY and DB_PASSWORD:
        print("${GREEN}✅ Vault에서 시크릿을 성공적으로 가져왔습니다!${NC}")
        print(f"${GREEN}   SECRET_KEY: {SECRET_KEY[:10]}...${NC}")
        print(f"${GREEN}   DB_PASSWORD: ****${NC}")
    else:
        print("${RED}❌ Vault에서 시크릿을 가져오지 못했습니다.${NC}")
        sys.exit(1)
except Exception as e:
    print(f"${RED}❌ 오류: {e}${NC}")
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Vault 연결 실패. 다음을 확인하세요:${NC}"
    echo "  1. Instance Principal 설정이 되어 있는가?"
    echo "  2. Dynamic Group에 인스턴스가 포함되어 있는가?"
    echo "  3. Policy가 올바르게 설정되어 있는가?"
    echo "  4. Secret OCID가 정확한가?"
    exit 1
fi

# 7. 마이그레이션
echo -e "${YELLOW}🗄️  데이터베이스 마이그레이션...${NC}"
export DJANGO_ENV=production
python manage.py migrate

# 8. Static 파일 수집
echo -e "${YELLOW}📁 Static 파일 수집...${NC}"
python manage.py collectstatic --noinput

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Vault 연동 설정 완료!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "다음 명령어로 서버를 시작하세요:"
echo -e "${YELLOW}  export DJANGO_ENV=production${NC}"
echo -e "${YELLOW}  python manage.py runserver 0.0.0.0:8000${NC}"
echo ""
echo "또는 systemd 서비스로 실행:"
echo -e "${YELLOW}  sudo systemctl start django${NC}"
