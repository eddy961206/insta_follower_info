import random
from turtle import pd
import pyperclip
import time
import traceback
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (NoSuchElementException, TimeoutException,
                                        StaleElementReferenceException)
from program_actions import find_element_with_retry
from bs4 import BeautifulSoup

def login_to_insta(driver, username, password):
    driver.get("https://www.instagram.com/accounts/login/")
    try:
        # 인스타그램 로그인을 위한 계정 정보
        username_input = find_element_with_retry(driver, By.CSS_SELECTOR, "input[name='username']")
        username_input.click()
        pyperclip.copy(username)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
        
        password_input = find_element_with_retry(driver, By.CSS_SELECTOR, "input[name='password']")
        password_input.click()
        pyperclip.copy(password)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
        
        login_button = find_element_with_retry(driver, By.CSS_SELECTOR, "button[type='submit']")
        if login_button:
            login_button.click()

            # 로그인 후 옵션 또는 설정 아이콘 확인
            # option_icon = find_element_with_retry(driver, By.CSS_SELECTOR, "svg[aria-label='옵션']", delay=10)
            settings_icon = find_element_with_retry(driver, By.CSS_SELECTOR, "svg[aria-label='설정']", delay=10)

            # if option_icon or settings_icon:
            if settings_icon:
                return True
            else:
                print("\n\n잘못된 로그인 계정정보입니다. 계정을 확인 후 프로그램을 재실행해주세요.")
                return False
                
        return True
    except NoSuchElementException:
        print("\n\n로그인 버튼을 찾을 수 없습니다.")
        return False
    except TimeoutException:
        print("\n\n로그인 페이지가 로드되는데 시간이 너무 오래 걸립니다.")
        return False
    except Exception as e:
        print(f"\n\n로그인 시도중 오류 발생 : {e}")
        return False



def get_follower_info(driver, account, max_follower_count):
    """특정 계정의 팔로워의 정보들 가져오는 가장 큰 함수"""
    if not open_followers_modal(driver, account):
        return []

    # 팔로워 모달에서 스크롤 및 수집
    try:
        child_element = find_element_with_retry(driver, By.CSS_SELECTOR, "div[style='height: auto; overflow: hidden auto;']")
        if not child_element:
            print(f"\n{account}계정의 팔로워 목록을 열 수 없습니다.")
            return []

        # 팔로워 리스트 모달 열기
        parent_element = child_element.find_element(By.XPATH, "..")
        follower_list_modal = parent_element

        # 팔로워 모달에서 각 팔로워의 정보 가져오기
        followers_info = scroll_and_fetch_follower_info(driver, follower_list_modal, max_follower_count, account)

        # print(f'\n{account} 계정에서 가져온 팔로워 수 : {len(followers_info)}명 \n(계정 페이지에 적혀있는 팔로워 수와 다를 수 있습니다.)')
        return followers_info

    except NoSuchElementException as e:
        print(f"\n{account}계정의 팔로워 정보를 가져오는 도중 필요한 요소를 찾을 수 없습니다: {e}\n")
    except TimeoutException as e:
        print(f"\n{account}계정의 팔로워 정보를 가져오는 도중 요청한 작업이 시간 내에 완료되지 않았습니다: {e}\n")
    except Exception as e:
        print(f"\n{account}계정의 팔로워 정보를 가져오는 도중 예기치 못한 오류가 발생했습니다: {e}\n")

    return []


def open_followers_modal(driver, account):
    """계정 페이지를 열고 팔로워 모달을 엽니다."""
    # 특정 계정으로 이동
    driver.get(f'https://www.instagram.com/{account}/')

    # 팔로워 버튼 클릭
    try:
        followers_button = find_element_with_retry(driver, By.PARTIAL_LINK_TEXT, "팔로워")
        if followers_button:
            followers_button.click()
            return True
        else:
            print(f"\n\n{account}계정의 팔로워 버튼을 누를 수 없습니다.")
            return False
    except NoSuchElementException:
        print(f"\n\n{account}계정이 비공개 계정이라서 팔로워 목록을 가져올 수 없습니다. 다음 계정으로 넘어갑니다..")
        return False


def scroll_and_fetch_follower_info(driver, follower_list_modal, max_follower_count, account):
    followers_info = []
    processed_followers = set()  # 처리된 팔로워를 추적하기 위한 세트
    last_height = driver.execute_script("return arguments[0].scrollHeight", follower_list_modal)
    scroll_count = 0        
    random_browsing_interval = random.randint(30, 40)  # 100~150명의 팔로워를 처리한 후 랜덤 브라우징 실행
    print(f'팔로워 데이터 추출 중 랜덤 행동을 시작할 순번 : {random_browsing_interval}\n')
    account_status_counter = 1  # 초기값 설정

    while len(followers_info) < max_follower_count:
        random_scroll_amount = random.randint(300, 1000)  # 랜덤한 스크롤 양
        driver.execute_script(f"arguments[0].scrollTop += {random_scroll_amount}", follower_list_modal)
        time.sleep(random.uniform(2, 3))

        new_height = driver.execute_script("return arguments[0].scrollHeight", follower_list_modal)
        if new_height <= last_height and len(followers_info) >= max_follower_count:
            break

        last_height = new_height

        # 15~20번 스크롤마다 10초~1분 랜덤으로 긴 휴식
        if scroll_count >= random.randint(2, 3):
            long_sleep_time = random.uniform(10, 60)
            print(f"스크롤링 중 봇 탐지 방지를 위해 {long_sleep_time}초 동안 긴 휴식을 취합니다...(10~60초 랜덤)")
            time.sleep(long_sleep_time)
            print("다 쉬었습니다. 다시 스크롤링 시작합니다.")
            scroll_count = 0

        # 팔로워 데이터 추출
        # 모든 canvas 요소 선택
        canvas_elements = driver.find_elements(By.TAG_NAME, 'canvas')
        # 높이와 너비가 50대인 canvas 요소만 필터링
        filtered_canvas_elements = [
            canvas for canvas in canvas_elements
            if 50 <= int(canvas.get_attribute('height')) <= 59 and 50 <= int(canvas.get_attribute('width')) <= 59
        ]

        # canvas_elements = driver.find_elements(By.CSS_SELECTOR, 'canvas[height="54"][width="54"]')
        # print(f'로드되어있는 팔로워 수(canvas) : {len(canvas_elements)}')

        # 각 팔로워 반복
        for canvas in filtered_canvas_elements:
            # 랜덤한 행동 실행 후 팔로워 정보 수집 재개
            if len(followers_info) >= random_browsing_interval:
                random_browsing_actions(driver)  # 랜덤 브라우징 활동 실행
                # 새롭게 로드된 팔로워 정보를 가져올 때까지 스크롤
                while True:
                    # 스크롤 다운
                    driver.execute_script("arguments[0].scrollTop += 1000", follower_list_modal)
                    time.sleep(random.uniform(2, 3))

                    # 새롭게 로드된 팔로워 정보가 있으면 중단
                    new_followers_loaded = check_new_followers_loaded(driver, follower_list_modal, processed_followers)
                    if new_followers_loaded:
                        break

                random_browsing_interval += random.randint(30, 40)  # 다음 랜덤 브라우징 실행까지의 인터벌 갱신
                print(f'\n팔로워 데이터 추출 중 랜덤 행동을 시작할 순번 : {random_browsing_interval}\n')

            if len(followers_info) >= max_follower_count:
                break
            
            # 'a/img' 또는 'span/img' 요소를 찾기 (호버링 전 프사)
            images = canvas.find_elements(By.XPATH, 'following-sibling::*[self::a or self::span]/img')
            if images:
                follower_name = images[0].get_attribute('alt').split('님의 프로필 사진')[0]
                # 팔로워가 이미 처리되었는지 확인
                if follower_name not in processed_followers:
                    follower_data = process_follower_element(driver, images[0])
                    followers_info.append(follower_data)
                    processed_followers.add(follower_name)  # 처리됨으로 표시  
                    
                    print(f"{account} - {account_status_counter} : {follower_name}, {follower_data['팔로워 수']}, {follower_data['팔로잉 수']}, {follower_data['계정 상태']}")
                    account_status_counter += 1
        # print(f"가져온 팔로워 정보 수 : {len(followers_info)}")
        scroll_count += 1

        new_height = driver.execute_script("return arguments[0].scrollHeight", follower_list_modal)

        # 스크롤이 더 이상 진행되지 않거나 최대 수에 도달한 경우 종료
        if new_height == last_height or len(followers_info) >= max_follower_count:
            break
        last_height = new_height

    return followers_info 


def process_follower_element(driver, element):
    try:
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        ActionChains(driver).move_to_element_with_offset(element, -50, 0).perform()
        time.sleep(0.5)
        ActionChains(driver).move_to_element(element).perform()
        time.sleep(2)
        return fetch_user_info(driver)
    except StaleElementReferenceException:
        print('StaleElementReferenceException 발생')
        pass


def fetch_user_info(driver):
    # 모든 canvas 요소 선택
    canvas_elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, 'canvas'))
    )

    # 높이와 너비가 60대인 canvas 요소 찾기
    canvas = next(
        (canvas for canvas in canvas_elements
            if 60 <= int(canvas.get_attribute('height')) <= 69 and 60 <= int(canvas.get_attribute('width')) <= 69),
        None
    )

    if canvas is None:
        raise Exception("적절한 크기의 canvas 요소를 찾을 수 없습니다.")
    
    image = canvas.find_element(By.XPATH, 'following-sibling::*[self::a or self::span]/img')

    follower_name = image.get_attribute('alt').split('님의 프로필 사진')[0]

    follower_count = following_count = None

    spans = driver.find_elements(By.XPATH, "//span[text()='팔로워' or text()='팔로잉']")
    
    for span in spans:
        sibling_span = span.find_element(By.XPATH, '../preceding-sibling::div/span')
        if '팔로워' in span.text:
            follower_count = sibling_span.text
        elif '팔로잉' in span.text:
            following_count = sibling_span.text

        if follower_count and following_count:
            break

    # 공개/비공개 여부 확인
    # grand_grand_parent = canvas.find_element(By.XPATH, './ancestor::div[4]') # 고조할아버지
    # next_sibling_of_sibling = grand_grand_parent.find_element(By.XPATH, 'following-sibling::div[2]') # 고조할아버지의 아래아래 동생div
    # public_images = next_sibling_of_sibling.find_elements(By.CSS_SELECTOR, 'img[height="120"][width="120"]')
    # account_status = "공개" if public_images else "비공개"

    # '비공개 계정입니다' 텍스트를 포함하는 요소 찾기
    private_account_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '비공개 계정입니다')]")
    account_status = "비공개" if private_account_elements else "공개"

    follower_info = {'팔로워 ID': follower_name}
    follower_info['계정 상태'] = account_status
    follower_info['팔로워 수'] = follower_count
    follower_info['팔로잉 수'] = following_count
    follower_info['팔로워 링크'] = f"https://www.instagram.com/{follower_name}/"

    return follower_info



def random_browsing_actions(driver):
    # 현재 탭의 핸들을 저장
    main_window_handle = driver.current_window_handle

    # 새 탭을 열고 랜덤 브라우징 수행
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])

    page_url = random.choice(["https://www.instagram.com/", 
                              "https://www.instagram.com/reels", 
                              "https://www.instagram.com/explore/"])
    driver.get(page_url)

    # 3~10초 사이의 랜덤 대기 시간 설정
    wait_time = random.uniform(3, 5)
    page_name = "릴스" if "reels" in page_url else "탐색 탭" if "explore" in page_url else "피드"
    time.sleep(wait_time)

    scroll_duration_time = random.randint(30, 60)
    print(f'\n봇 인식 방지를 위해 {scroll_duration_time:.2f}초 동안 {page_name}을/를 방문하여 랜덤 행동을 수행합니다.')

    end_time = time.time() + scroll_duration_time

    if "reels" in page_url:
        # 릴스 페이지의 경우 페이지 다운 키를 사용한 스크롤링
        while time.time() < end_time:
            ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
            time.sleep(random.uniform(3, 10))
    else:
        # 다른 페이지의 경우 일반 스크롤링
        while time.time() < end_time:
            scroll_by = random.randint(200, 700)
            driver.execute_script(f"window.scrollBy(0, {scroll_by});")
            time.sleep(random.uniform(3, 10))

    print('\n랜덤 행동을 마쳤습니다. 데이터 추출을 다시 시작합니다.\n')       

    # 새 탭을 닫고 원래 탭으로 돌아가기
    driver.close()
    driver.switch_to.window(main_window_handle)


def check_new_followers_loaded(driver, follower_list_modal, processed_followers):
    # 팔로워 리스트에서 새롭게 로드된 팔로워가 있는지 확인
    canvas_elements = driver.find_elements(By.CSS_SELECTOR, 'canvas[height="54"][width="54"]')
    for canvas in canvas_elements:
        images = canvas.find_elements(By.XPATH, 'following-sibling::*[self::a or self::span]/img')
        if images:
            follower_name = images[0].get_attribute('alt').split('님의 프로필 사진')[0]
            if follower_name not in processed_followers:
                print(f'새 팔로워 발견됨! : {follower_name}')
                return True
    return False