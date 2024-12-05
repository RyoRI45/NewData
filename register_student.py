from core.models import Student

# サンプルデータを登録
students = [
    {'student_id': 'A001', 'student_name': '佐藤修太郎', 'password': 'ac003b001'},
    {'student_id': 'A002', 'student_name': '土屋大臣', 'password': 'rj011s314'},
    {'student_id': 'A003', 'student_name': '松浦徳弥', 'password': 'sn353v487'},
    {'student_id': 'A004', 'student_name': '帝塚健太', 'password': 'eg463g215'},
    {'student_id': 'A005', 'student_name': '森本雄大', 'password': 'nr209f311'},
]

for student in students:
    Student.objects.get_or_create(**student)

print("学生データを登録しました！")

