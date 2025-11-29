from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # 프론트엔드에서 받을 필드 목록 (email 포함)
        fields = ('email', 'password', 'student_num', 'department', 'nickname')
        extra_kwargs = {
            'password': {'write_only': True}, # 비밀번호는 응답에 포함 X
            'email': {'required': True}       # 이메일 필수 입력
        }

    # (옵션) 이메일 중복 체크 커스텀
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("이미 가입된 이메일입니다.")
        return value

    # (옵션) 학번 중복 체크 커스텀
    def validate_student_num(self, value):
        if User.objects.filter(student_num=value).exists():
            raise serializers.ValidationError("이미 가입된 학번입니다.")
        return value

    def create(self, validated_data):
        # User 모델의 create_user 메서드를 통해 DB에 저장
        # (비밀번호 암호화 자동 처리)
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            student_num=validated_data['student_num'],
            department=validated_data['department'],
            nickname=validated_data.get('nickname', '')
        )
        return user
    

# 로그아웃 시리얼라이저
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            pass