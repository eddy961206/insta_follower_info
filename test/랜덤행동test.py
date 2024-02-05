import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from insta_utils import login_to_insta, random_browsing_actions

from program_actions import initialize_driver


# 웹드라이버 초기화
driver = initialize_driver()

id = 'skykum2019@gmail.com'
pw = '3susdksdpdnjf1djr'

# 로그인
if not login_to_insta(driver, id, pw):
    print(f"\n계정 {id}으로 로그인에 실패했습니다. 프로그램을 종료합니다.")
else :
    print(f"\n계정 {id}으로 로그인 하였습니다.")


random_browsing_actions(driver)

input('종료 : 아무거나 입력')
