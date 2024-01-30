import random
import time
from program_actions import (capture_screenshot, initialize_driver, save_to_excel)
from insta_utils import (get_follower_info, login_to_insta)


likeminPauseTime = 0.5 
likemaxPauseTime = 6.5

# 메인 로직 함수
def main_logic(id, pw, accounts, max_follower_cnt):
    # 프로그램 전체 실행 시작 시간
    program_start_time = time.time()
    
    try:
            
        print('\n\n===============  프로그램 작동중.... ===============')
        print('\n\n=== 화면은 가려져도 되지만 크롬 창 최소화는 하지 말아주세요 ===')

        # 웹드라이버 초기화
        driver = initialize_driver()
        
        # 로그인
        if not login_to_insta(driver, id, pw):
            print(f"\n계정 {id}으로 로그인에 실패했습니다. 프로그램을 종료합니다.")
            return
        else :
            print(f"\n계정 {id}으로 로그인 하였습니다.")

        
        # 모든 계정의 팔로워 데이터를 저장할 딕셔너리
        all_followers_data = {}

        total_accounts = len(accounts)

        # 각 계정을 순회하며 팔로워 목록을 가져오기
        for index, account in enumerate(accounts):
            # 계정 처리 시작 시간
            account_start_time = time.time()

            followers_info = process_account_followers(driver, account, max_follower_cnt, index + 1, total_accounts)

            account_elapsed_time = time.time() - account_start_time
            print(f"\n{account} 계정 처리 소요 시간: {account_elapsed_time // 60}분 {account_elapsed_time % 60:.2f}초")
                        
            if followers_info or followers_info != []:
                all_followers_data[account] = followers_info
            else:
                print(f"\n계정 {account}의 팔로워 데이터가 없습니다. {account}계정의 엑셀 시트를 만들지 않고 넘어갑니다...")

        # 결과 엑셀에 저장
        save_to_excel(all_followers_data)

        # 프로그램 전체 실행 종료 시간 및 소요 시간 계산
        program_elapsed_time = time.time() - program_start_time
        print(f"\n프로그램 전체 실행 소요 시간: {program_elapsed_time // 60}분 {program_elapsed_time % 60:.2f}초")

        print('===== ***** ===== *****  ===== ***** ===== *****')
        print(f'\n팔로워 추출 및 엑셀 저장이 완료되었습니다.')
                
        driver.quit()

    except Exception as e:
               
        print(f"\n\n**** 프로그램 실행 오류 : {e}\n"
              "\n프로그램이 예기치 못하게 중단되었습니다...")

        capture_screenshot(driver, str(e))  # 에러 발생 시 스크린샷 캡처


def process_account_followers(driver, account, max_follower_cnt, 
                              current_account_number, total_accounts):
    
    print('\n-------------------------------------')
    print(f'\n\n{account} 계정의 팔로워 정보 수집 시작 ({current_account_number}/{total_accounts})\n')
    

    # # 랜덤한 개수 설정 (200개~300개 사이)
    # random_count = random.randint(200, 300)
    # print(f'{account} 계정의 팔로워 정보 처리중 일시정지할 랜덤 개수 : {random_count} (200개~300개 사이)')

    try:
        # 팔로워 정보 추출
        followers_info = get_follower_info(driver, account, max_follower_cnt)
        
        # 팔로워 정보를 데이터nd(followers_info)
    except Exception as e:
        print(f"\n\n**** {account} 계정의 팔로워 정보 수집 중 에러 발생: {e}\n"
            "이전까지 수집된 데이터를 엑셀로 저장합니다...")
        save_to_excel(followers_info)

    return followers_info


    
    




