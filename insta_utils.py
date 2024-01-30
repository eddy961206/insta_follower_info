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
        followers_info = scroll_and_fetch_follower_info(driver, follower_list_modal, max_follower_count)

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


def scroll_and_fetch_follower_info(driver, follower_list_modal, max_follower_count):
    followers_info = []
    processed_followers = set()  # 처리된 팔로워를 추적하기 위한 세트
    last_height = driver.execute_script("return arguments[0].scrollHeight", follower_list_modal)
    scroll_count = 0        

    while len(followers_info) < max_follower_count:
        random_scroll_amount = random.randint(300, 1000)  # 랜덤한 스크롤 양
        driver.execute_script(f"arguments[0].scrollTop += {random_scroll_amount}", follower_list_modal)

        # WebDriverWait(driver, 10).until(
        #     lambda d: d.execute_script("return arguments[0].scrollHeight", follower_list_modal) > last_height
        # )

        time.sleep(random.uniform(2, 3))

        new_height = driver.execute_script("return arguments[0].scrollHeight", follower_list_modal)
        if new_height <= last_height and len(followers_info) >= max_follower_count:
            break

        last_height = new_height

        # 15~20번 스크롤마다 10초~1분 랜덤으로 긴 휴식
        if scroll_count >= random.randint(15, 20):
            long_sleep_time = random.uniform(10, 60)
            print(f"스크롤링 중 봇 탐지 방지를 위해 {long_sleep_time}초 동안 긴 휴식을 취합니다...(10~60초 랜덤)")
            time.sleep(long_sleep_time)
            print("다 쉬었습니다. 다시 스크롤링 시작합니다.")
            scroll_count = 0

        # 팔로워 데이터 추출
        # 54 짜리 캔버스 하나하나가 팔로워 1명을 의미
        canvas_elements = driver.find_elements(By.CSS_SELECTOR, 'canvas[height="54"][width="54"]')
        # print(f'로드되어있는 팔로워 수(canvas) : {len(canvas_elements)}')

        # 각 팔로워 반복
        for canvas in canvas_elements:
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
        return fetch_user_info(driver)
    except StaleElementReferenceException:
        print('StaleElementReferenceException 발생')
        pass


def fetch_user_info(driver):
    canvas = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'canvas[height="66"][width="66"]'))
        )
    
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
    grand_grand_parent = canvas.find_element(By.XPATH, './ancestor::div[4]') # 고조할아버지
    next_sibling_of_sibling = grand_grand_parent.find_element(By.XPATH, 'following-sibling::div[2]') # 고조할아버지의 아래아래 동생div
    public_images = next_sibling_of_sibling.find_elements(By.CSS_SELECTOR, 'img[height="120"][width="120"]')
    account_status = "공개" if public_images else "비공개"

    follower_info = {'팔로워 ID': follower_name}
    follower_info['계정 상태'] = account_status
    follower_info['팔로워 수'] = follower_count
    follower_info['팔로잉 수'] = following_count
    follower_info['팔로워 링크'] = f"https://www.instagram.com/{follower_name}/"


    print(follower_name, follower_count, following_count, account_status)

    return follower_info

