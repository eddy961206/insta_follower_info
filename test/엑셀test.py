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

# # 함수 호출 및 엑셀 파일 생성 테스트
# save_to_excel(data_example)

# 딕셔너리 형태의 모의 데이터
mock_data_dict = {
    "account1": [
        {"팔로워 ID": "follower1", "팔로워 수": "100", "팔로잉 수": "200", "계정 상태": "공개", "팔로워 링크": "https://www.instagram.com/follower1/"},
        {"팔로워 ID": "follower2", "팔로워 수": "150", "팔로잉 수": "250", "계정 상태": "비공개", "팔로워 링크": "https://www.instagram.com/follower2/"}
    ],
    "account2": [
        {"팔로워 ID": "follower3", "팔로워 수": "200", "팔로잉 수": "300", "계정 상태": "공개", "팔로워 링크": "https://www.instagram.com/follower3/"}
    ]
}

# 리스트 형태의 모의 데이터
mock_data_list = [
    {"팔로워 ID": "follower4", "팔로워 수": "250", "팔로잉 수": "350", "계정 상태": "공개", "팔로워 링크": "https://www.instagram.com/follower4/"},
    {"팔로워 ID": "follower5", "팔로워 수": "300", "팔로잉 수": "400", "계정 상태": "비공개", "팔로워 링크": "https://www.instagram.com/follower5/"}
]

# 함수 호출 예시
save_to_excel(mock_data_dict)  # 딕셔너리 데이터를 사용하여 함수 호출
# save_to_excel(mock_data_list)  # 리스트 데이터를 사용하여 함수 호출