#!/bin/bash
# Oracle Cloud 인스턴스에서 안전한 환경변수 설정 스크립트

set -e

echo "🔐 Django 프로덕션 환경 보안 설정 시작..."

# 1. 디렉토리 생성
echo "📁 디렉토리 생성..."
sudo mkdir -p /etc/django
sudo mkdir -p /var/log/django
sudo chown ubuntu:ubuntu /var/log/django

# 2. secrets 파일 생성
echo "🔑 Secrets 파일 생성..."
echo "SECRET_KEY를 입력하세요:"
read -s SECRET_KEY

echo "DB_PASSWORD를 입력하세요:"
read -s DB_PASSWORD

echo "ALLOWED_HOSTS를 입력하세요 (쉼표로 구분):"
read ALLOWED_HOSTS

# secrets.env 파일 작성
sudo tee /etc/django/secrets.env > /dev/null <<EOF
SECRET_KEY=$SECRET_KEY
DB_PASSWORD=$DB_PASSWORD
ALLOWED_HOSTS=$ALLOWED_HOSTS
EOF

# 3. 파일 권한 설정 (중요!)
echo "🔒 권한 설정..."
sudo chmod 600 /etc/django/secrets.env
sudo chown root:root /etc/django/secrets.env

# 4. systemd 서비스 복사
echo "⚙️  systemd 서비스 설정..."
sudo cp django.service /etc/systemd/system/django.service
sudo systemctl daemon-reload

# 5. 서비스 시작
echo "🚀 Django 서비스 시작..."
sudo systemctl enable django
sudo systemctl start django

# 6. 상태 확인
echo "✅ 설정 완료! 서비스 상태:"
sudo systemctl status django --no-pager

echo ""
echo "🔐 보안 체크:"
echo "- secrets.env 권한: $(stat -c '%a' /etc/django/secrets.env)"
echo "- secrets.env 소유자: $(stat -c '%U:%G' /etc/django/secrets.env)"
echo ""
echo "✅ 모든 설정이 완료되었습니다!"
