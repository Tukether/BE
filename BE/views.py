from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection
import datetime


def health_check(request):
    """
    헬스체크 API
    서버 상태와 DB 연결 상태를 확인합니다.
    """
    try:
        # DB 연결 확인
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"disconnected: {str(e)}"

    return JsonResponse({
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "database": db_status,
        "service": "TukCommunity Backend API"
    })