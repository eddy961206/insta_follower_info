import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from program_actions import save_to_excel




# 예제 데이터
data_example = {
    'gayeon3737': [
        {'팔로워 ID': 'kveong_an32', '팔로워 수': '78', '팔로잉 수': '1964', '계정 상태': '공개', '팔로워 링크': 'https://www.instagram.com/kveong_an32/'},
        {'팔로워 ID': 'a01058404656', '팔로워 수': '2438', '팔로잉 수': '4579', '계정 상태': '공개', '팔로워 링크': 'https://www.instagram.com/a01058404656/'},
        {'팔로워 ID': 'a01058404656', '팔로워 수': '2438', '팔로잉 수': '4579', '계정 상태': '공개', '팔로워 링크': 'https://www.instagram.com/a01058404656/'},
        {'팔로워 ID': 'a01058404656', '팔로워 수': '2438', '팔로잉 수': '4579', '계정 상태': '공개', '팔로워 링크': 'https://www.instagram.com/a01058404656/'}
    ],
    'dfsdfsdfs': [
        {'팔로워 ID': 'asd', '팔로워 수': '78', '팔로잉 수': '1964', '계정 상태': '공개', '팔로워 링크': 'https://www.instagram.com/kveong_an32/'},
        {'팔로워 ID': '12321412', '팔로워 수': '2438', '팔로잉 수': '4579', '계정 상태': '공개', '팔로워 링크': 'https://www.instagram.com/a01058404656/'}
    ]
}

# 함수 호출 및 엑셀 파일 생성 테스트
save_to_excel(data_example)

