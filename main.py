import random
import time
from program_actions import (capture_screenshot, initialize_driver, save_to_excel)
from insta_utils import (get_followers_names_from_acc, get_user_info, login_to_insta)


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

            followers_data = process_account_followers(driver, account, max_follower_cnt, index + 1, total_accounts)

            # 계정 처리 종료 시간 및 소요 시간 계산
            account_elapsed_time = time.time() - account_start_time
            print(f"\n{account} 계정 처리 소요 시간: {account_elapsed_time // 60}분 {account_elapsed_time % 60:.2f}초")
            print(f"{account} 계정에서 가져온 팔로워 수: {len(followers_data)}명")
            if len(followers_data) > 0:
                print(f"{account} 계정의 팔로워 당 평균 소요 시간: {account_elapsed_time / len(followers_data):.2f}초")

            if followers_data or followers_data != []:
                all_followers_data[account] = followers_data
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
    print(f'\n\n{account} 계정의 팔로워 정보 수집 시작 ({current_account_number}/{total_accounts})')

    # 각 계정별로 팔로워 정보를 가져오고 저장
    follower_names = get_followers_names_from_acc(driver, account, max_follower_cnt)
    
    # 팔로워 이름이 없으면 함수 종료
    if not follower_names or follower_names == []:
        return []

    followers_data = []

    # 랜덤한 개수 설정 (200개~300개 사이)
    random_count = random.randint(200, 300)
    print(f'{account} 계정의 팔로워 정보 처리중 일시정지할 랜덤 개수 : {random_count} (200개~300개 사이)')

    # 각 팔로워에 대해 정보를 추출
    for index, follower_name in enumerate(follower_names):

        try:
            # 랜덤한 개수째 팔로워 정보를 가져올 때 대기
            if (index + 1) % random_count == 0:
                # 5분에서 10분 사이의 랜덤한 시간 동안 대기
                wait_time = random.randint(300, 600)
                print(f"\n계정 잠김 방지를 위해 \n현재 {index + 1}번째 팔로워 처리 후 {wait_time / 60:.2f}분 동안 대기합니다.")
                time.sleep(wait_time)
                # 대기 후 랜덤한 개수를 다시 설정
                random_count = random.randint(200, 300)
            
            # 팔로워 정보 추출
            follower_info, follower_elapsed_time \
                = get_user_info(driver, follower_name, len(follower_names), (index+1))
            # print(follower_info)

            # 팔로워 정보 추출 소요 시간 안내
            print(f"{follower_name} 팔로워 정보 추출 소요 시간: {follower_elapsed_time:.2f}초")

            # 팔로워 정보를 데이터 리스트에 추가
            followers_data.append(follower_info)
        except Exception as e:
            print(f"\n\n**** {account} 계정의 팔로워 {follower_name}의 정보 수집 중 에러 발생: {e}\n"
                "이전까지 수집된 데이터를 엑셀로 저장합니다...")
            save_to_excel(followers_data)
            break             

    return followers_data


    
    




