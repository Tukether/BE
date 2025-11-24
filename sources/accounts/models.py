# sources/accounts/models.py

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# 1. Role 테이블 매핑
class Role(models.Model):
    role_id = models.BigAutoField(primary_key=True)
    # authority: 0=기본유저, 1=관리자
    authority = models.IntegerField(default=0) 
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False  # Django가 테이블을 생성/수정하지 않음 (SQL로 관리)
        db_table = 'Role'

    def __str__(self):
        return f"Role({self.authority})"


# 2. 커스텀 유저 매니저 (회원가입 로직 처리를 위해 필수)
class UserManager(BaseUserManager):
    def create_user(self, email, student_num, department, password=None, **extra_fields):
        if not email:
            raise ValueError('이메일은 필수입니다.')
        
        email = self.normalize_email(email)
        # 기본 Role 설정 (DB에 Role 데이터가 미리 INSERT 되어 있어야 함)
        default_role = Role.objects.get(role_id=1) # 1번이 일반 유저라고 가정
        
        user = self.model(
            email=email,
            student_num=student_num,
            department=department,
            role=default_role,
            **extra_fields
        )
        
        user.set_password(password) # 비밀번호 암호화
        user.save(using=self._db)
        return user

    def create_superuser(self, email, student_num, department, password=None, **extra_fields):
        # 관리자 Role 가져오기
        admin_role = Role.objects.get(role_id=2) # 2번이 관리자라고 가정
        
        extra_fields.setdefault('nickname', 'Admin')
        
        user = self.create_user(
            email, student_num, department, password, **extra_fields
        )
        user.role = admin_role
        user.save(using=self._db)
        return user


# 3. User 테이블 매핑
class User(AbstractBaseUser):
    # SQL 컬럼명과 일치시킴
    user_id = models.BigAutoField(primary_key=True)
    role = models.ForeignKey(Role, on_delete=models.RESTRICT, db_column='role_id')
    email = models.EmailField(max_length=100, unique=True)
    student_num = models.IntegerField(unique=True)
    department = models.CharField(max_length=50)
    nickname = models.CharField(max_length=30, null=True, blank=True)
    
    # AbstractBaseUser가 password, last_login 필드는 기본적으로 가짐
    # 하지만 SQL 스키마엔 last_login이 없으므로 모델에는 정의하되 DB엔 없다고 처리하거나
    # SQL에 last_login 컬럼을 추가해주는 게 좋습니다. (로그인 시 Django가 업데이트함)
    # 여기서는 SQL을 건드리지 않기 위해 last_login은 사용하지 않도록 설정하거나 무시합니다.
    last_login = None 

    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    # 로그인 시 사용할 ID 필드
    USERNAME_FIELD = 'email' 
    # 슈퍼유저 생성 시 입력받을 필수 필드
    REQUIRED_FIELDS = ['student_num', 'department']

    @property
    def id(self):
        return self.user_id

    @property
    def pk(self):
        return self.user_id

    class Meta:
        managed = False # 이미 DB에 테이블이 있으므로 False
        db_table = 'User'

    def __str__(self):
        return self.email

    # Django Admin 접속 권한 제어 (SQL의 authority 이용)
    @property
    def is_staff(self):
        return self.role.authority == 1

    @property
    def is_superuser(self):
        return self.role.authority == 1

    # 권한 관련 필수 메서드 (단순화)
    def has_perm(self, perm, obj=None):
        return self.role.authority == 1

    def has_module_perms(self, app_label):
        return self.role.authority == 1
    