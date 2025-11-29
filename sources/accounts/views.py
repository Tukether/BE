from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework import permissions
from .serializers import LogoutSerializer

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,) # 로그인 안 한 상태에서도 가입 가능
    serializer_class = RegisterSerializer

    # 가입 성공 시 응답 메시지 커스터마이징
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        # 유효성 검사 (실패 시 400 Bad Request 자동 반환)
        serializer.is_valid(raise_exception=True) 
        
        # DB 저장
        user = serializer.save()
        
        return Response(
            {
                "message": "회원가입이 완료되었습니다.",
                "user": {
                    "email": user.email,
                    "student_num": user.student_num,
                    "nickname": user.nickname
                }
            },
            status=status.HTTP_201_CREATED
        )
    

# 로그아웃 뷰
class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            {"message": "로그아웃이 성공적으로 완료되었습니다."}, 
            status=status.HTTP_200_OK
        )