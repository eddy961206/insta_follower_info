import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from program_actions import initialize_driver
from insta_utils import get_user_info, login_to_insta
from main import main_logic


# 웹드라이버 초기화
driver = initialize_driver()

id = 'skykum2004@gmail.com'
pw = 'Fbtmdxor96!'

# 로그인
if not login_to_insta(driver, id, pw):
    print(f"\n계정 {id}으로 로그인에 실패했습니다. 프로그램을 종료합니다.")
    input()
else :
    print(f"\n계정 {id}으로 로그인 하였습니다.")


follower_name = 'jjj___xx' # 비공개 
# follower_name = 'dfadsaf437' # 게시물 X
# follower_name = '8o1o1_2' # 팔로워 18개, 게시물 X

follower_info = get_user_info(driver, follower_name)

print(follower_info)






