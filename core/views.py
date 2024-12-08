from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .models import Student, Subject, GPA
from django.http import HttpResponseForbidden
from core.models import Student  # Student モデルのインポート

# Create your views here.

def home(request):
    host = request.get_host()  # ホスト名を取得
    print(f"Request host: {request.get_host()}")  # ログにホスト名を出力
    return render(request, 'core/home.html')

def register_student(request):
    if request.method == 'POST':
        # 登録処理を追加（例: データベースに保存）
        pass
    return render(request, 'core/register_student.html')

@login_required
def login_view(request):
    host = request.get_host()  # ホスト名を取得
    print(f"Login page accessed from host: {host}")  # ログにホスト名を出力
    
    if request.method == 'POST':
        student_name = request.POST['student_name']
        password = request.POST['password']
        try:
            student = Student.objects.get(student_name=student_name, password=password)
            request.session['student_id'] = student.student_id
            return redirect('student_home')
        except Student.DoesNotExist:
            return render(request, 'core/login.html', {'error': 'ログインに失敗しました'})
    return render(request, 'core/login.html')

def logout_view(request):
    logout(request)  # ユーザーをログアウト
    request.session.flush()  # セッションを完全にクリア
    return redirect('login')  # ログイン画面にリダイレクト

def student_home(request):
    host = request.get_host()  # ホスト名を取得
    print(f"Student home page accessed from host: {host}")  # ログにホスト名を出力

    student_id = request.session.get('student_id')
    if not student_id:
        # セッションが無い場合はログインページにリダイレクト
        return redirect('login')

    # 学生情報を取得
    student = Student.objects.get(student_id=student_id)

    # キャッシュ無効化ヘッダーを追加
    response = render(request, 'core/student_home.html', {'student': student})
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'

    return response

def manage_grades(request):
    host = request.get_host()  # ホスト名を取得
    print(f"Manage grades page accessed from host: {host}")  # ログにホスト名を出力
    return render(request, 'core/manage_grades.html')

def subject_register(request):
    host = request.get_host()  # ホスト名を取得
    print(f"Subject register page accessed from host: {host}")  # ログにホスト名を出力
    
    if request.method == 'POST':
        student_id = request.session.get('student_id')
        student = Student.objects.get(student_id=student_id)
        subject_class = request.POST['subject_class']
        subject_name = request.POST['subject_name']

        # 科目数チェック
        subject_count = Subject.objects.filter(student=student).count()
        if subject_count >= 5:
            return render(request, 'core/subject_register.html', {'error': '登録可能な科目数は最大5件です'})

        # 成績と授業回数設定
        if subject_count in [0]: #1科目
            subject_score = 1
            lesson_count = 4
            attend_days = 1
        elif subject_count in [1]: #2科目
            subject_score = 2
            lesson_count = 8
            attend_days = 3
        elif subject_count in [2,]: #3科目
            subject_score = 3
            lesson_count = 7
            attend_days = 4
        elif subject_count in [3]: #4科目
            subject_score = 4
            lesson_count = 9
            attend_days = 7
        else:
            subject_score = 4
            lesson_count = 11
            attend_days = 9

        Subject.objects.create(
            student=student,
            subject_name=subject_name,
            subject_class=subject_class,
            subject_score=subject_score,
            lesson_count=lesson_count,
            attend_days=attend_days,
        )
        return redirect('manage_grades')

    return render(request, 'core/subject_register.html')

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
