from django.contrib.auth.hashers import make_password
from core.models import Student

# 学生名とパスワードを入力として受け取る
student_name = input("学生名を入力: ")
password = input("パスワードを入力: ")

# パスワードをハッシュ化する
hashed_password = make_password(password)

# 学生データの登録
student, created = Student.objects.get_or_create(
    student_name=student_name,
    defaults={"password": hashed_password},
)

if created:
    print(f"学生 '{student_name}' が登録されました。")
else:
    print(f"学生 '{student_name}' は既に存在しています。")
