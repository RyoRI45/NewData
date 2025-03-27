from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Student, Subject, GPA
from django.http import HttpResponseForbidden
from core.models import Student  # Student モデルのインポート
from django.conf import settings
import uuid
from django.shortcuts import get_object_or_404

# Create your views here.

def home(request):
    host = request.get_host()  # ホスト名を取得
    print(f"Request host: {request.get_host()}")  # ログにホスト名を出力
    return render(request, 'core/home.html')

#アカウント作成
def register_student(request):
    if request.method == 'POST':
        student_name = request.POST.get('student_name', '').strip()
        password = request.POST.get('password', '').strip()

        # 入力値のチェック
        if not student_name or not password:
            return render(request, 'core/register_student.html', {
                'error': '全ての項目を入力してください。'
            })

        # 学生名が重複しないかチェック
        if Student.objects.filter(student_name=student_name).exists():
            return render(request, 'core/register_student.html', {
                'error': 'この学生名は既に登録されています。'
            })

        # ランダムな student_id を生成して Student モデルに登録
        student_id = str(uuid.uuid4())[:8]  # UUIDの最初の8文字をIDに使用
        Student.objects.create(student_id=student_id, student_name=student_name, password=password)

        return redirect('home')  # 登録後はホームへリダイレクト

    return render(request, 'core/register_student.html')

# def login_view(request):
#     if request.method == 'POST':
#         username = request.POST.get('student_name')
#         password = request.POST.get('password')
#         user = authenticate(request, username=username, password=password)
        
#         if user is not None:
#             login(request, user)
            
#             # next パラメータが存在する場合、そのURLにリダイレクト
#             next_url = request.GET.get('next')
#             if next_url:
#                 return redirect(next_url)
            
#             # next がない場合、デフォルトのリダイレクト先へ
#             return redirect(settings.LOGIN_REDIRECT_URL)
#         else:
#             return render(request, 'core/login.html', {'error': '無効なユーザー名またはパスワードです。'})
    
#     # GETリクエスト時、通常のログインページを表示
#     return render(request, 'core/login.html')

# ログイン
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # 学生 ID をセッションに保存（仮の値を使用）
            request.session['student_id'] = 'A001'
            print(f"ログイン成功: セッションキー = {request.session.session_key}, student_id = {request.session.get('student_id')}")
            return redirect('student_home')
        else:
            print("ログイン失敗")
    return render(request, 'core/login.html')

# ログアウト
def logout_view(request):
    logout(request)  # ユーザーをログアウト
    request.session.flush()  # セッションを完全にクリア
    return redirect('login')  # ログイン画面にリダイレクト

# def student_home(request):
#     host = request.get_host()
#     print(f"Student home page accessed from host: {host}")

#     # セッションから student_id を取得
#     student_id = request.session.get('student_id')
#     print(f"セッション内の student_id: {student_id}")

#     if not student_id:
#         print("セッションが見つからないため、ログインページにリダイレクトします")
#         return redirect('login')

#     try:
#         student = Student.objects.get(student_id=student_id)
#         print(f"取得した学生情報: {student}")
#     except Student.DoesNotExist:
#         print("指定された student_id に一致する学生が見つかりません")
#         return redirect('login')

#     # レンダリング処理に変更
#     return render(
#         request,
#         'core/student_home.html',
#         {'student': student}  # 学生情報をテンプレートに渡す
#     )

def student_home(request):
    session_key = request.session.session_key  # 現在のセッションキー
    print(f"現在のセッションキー: {session_key}")

    student_id = request.session.get('student_id')  # セッションに保存された student_id
    print(f"セッションから取得した student_id: {student_id}")

    if not student_id:
        return redirect('login')

    # 学生情報を取得
    student = Student.objects.get(student_id=student_id)

    return render(request, 'core/student_home.html', {'student': student})

def manage_grades(request):
    host = request.get_host()  # ホスト名を取得
    print(f"Manage grades page accessed from host: {host}")  # ログにホスト名を出力
    return render(request, 'core/manage_grades.html')

@login_required
def subject_register(request):
    print(f"Logged-in user: {request.user}")  # デバッグ用
    print(f"Is authenticated: {request.user.is_authenticated}")  # 認証状態を確認

    debug_info = f"ユーザー: {request.user} | 認証状態: {request.user.is_authenticated}"

    grades = range(1, 6)  # 成績の選択肢（1〜5）

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        grade = request.POST.get('grade')
        date = request.POST.get('date')
        table = request.POST.get('table')

        # 入力チェック
        if not name or not grade or not date or not table:
            return render(request, 'core/subject_register.html', {
                'grades': grades,
                'error': '全ての項目を入力してください。',
                'debug_info': debug_info
            })

        try:
            # Student オブジェクトの取得または作成
            student, created = Student.objects.get_or_create(student_name=request.user.username)
            print(f"Student作成: {created}")  # デバッグ用
            debug_info += f" | Student作成: {created}"

            # Subject オブジェクトを作成
            Subject.objects.create(
                student=student,  # ForeignKey に Student オブジェクトを設定
                subject_name=name,
                subject_score=int(grade),
                date=date,
                table=table
            )
            return redirect('student_home')  # 成功時にリダイレクト

        except Exception as e:
            debug_info += f" | エラー: {str(e)}"
            print(f"エラー: {str(e)}")  # デバッグ用
            return render(request, 'core/subject_register.html', {
                'grades': grades,
                'error': '登録中にエラーが発生しました。',
                'debug_info': debug_info
            })

    # GETリクエスト時
    return render(request, 'core/subject_register.html', {'grades': grades, 'debug_info': debug_info})

def calculate_gpa(student_id):
    # 学生の全ての成績を取得
    subjects = Subject.objects.filter(student_id=student_id)
    if not subjects.exists():
        return 0.0

    # 成績の合計と科目数
    total_grade = sum(subject.grade for subject in subjects)
    gpa = total_grade / subjects.count()
    return round(gpa, 2)  # 小数点以下2桁で丸める

def grade_view(request):
    host = request.get_host()  # ホスト名を取得
    print(f"Grade view page accessed from host: {host}")  # ログにホスト名を出力
    
    student_id = request.session.get('student_id')
    student = Student.objects.get(student_id=student_id)
    subjects = Subject.objects.filter(student=student)

    # GPA計算
    total_score = sum(subject.subject_score for subject in subjects)
    gpa = total_score / len(subjects) if subjects else 0

    # GPAメッセージ
    if gpa >= 4.0:
        message = '今の成績を維持しましょう'
    elif 2.5 <= gpa < 4.0:
        # subject_scoreが低い科目を取得（例: スコアが2未満の科目を改善対象とする）
        low_score_subjects = subjects.filter(subject_score__lt=2)
        if low_score_subjects.exists():
            low_score_names = ', '.join([subject.subject_name for subject in low_score_subjects])
            message = f'成績の改善が必要な科目があります: {low_score_names}'
        else:
            message = '成績の改善が必要な科目があります'
    else:
        message = '履修科目を見直す必要があります'

    return render(request, 'core/grade_view.html', {
        'subjects': subjects,
        'gpa': gpa,
        'message': message
    })

def attendance_plan(request):
    host = request.get_host()  # ホスト名を取得
    print(f"Attendance plan page accessed from host: {host}")  # ログにホスト名を出力
    
    student_id = request.session.get('student_id')
    student = Student.objects.get(student_id=student_id)
    subjects = Subject.objects.filter(student=student)

    # 出席率計算
    attendance_data = []
    for subject in subjects:
        attendance_rate = (subject.attend_days / subject.lesson_count) * 100
        if attendance_rate >= 70:
            status = '現状を維持しましょう'
        elif attendance_rate == 70:
            status = '少し危険です'
        else:
            status = '警告！出席率が低下しています'
        attendance_data.append({
            'subject_name': subject.subject_name,
            'attendance_rate': attendance_rate,
            'status': status,
        })

    return render(request, 'core/attendance_plan.html', {'attendance_data': attendance_data})
