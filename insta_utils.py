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
                                        ElementClickInterceptedException, UnexpectedAlertPresentException,
                                        NoAlertPresentException)
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


def scroll_followers_modal(driver, follower_list_modal, max_follower_count):
    """팔로워 모달에서 스크롤을 진행하며 팔로워 목록을 추출합니다."""
    followers = []
    last_height = driver.execute_script("return arguments[0].scrollHeight", follower_list_modal)
    scroll_count = 0

    while len(followers) < max_follower_count:
        # 랜덤한 횟수(10~20)만큼 스크롤
        random_scroll_times = random.randint(10, 20)
        for _ in range(random_scroll_times):
            # 스크롤
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", follower_list_modal)
            time.sleep(random.uniform(2, 3))  # 스크롤 후 랜덤 대기

            # 스크롤이 더 이상 진행되지 않으면 종료
            new_height = driver.execute_script("return arguments[0].scrollHeight", follower_list_modal)
            if new_height == last_height:
                break
            last_height = new_height

        # 스크롤 완료 후 팔로워 목록 추출
        followers = fetch_follower_names(driver)

        followers = list(set(followers))[:max_follower_count]  # 중복 제거 및 최대 팔로워 수 조정

        # 팔로워 수가 이미 충분하거나 스크롤이 더 이상 진행되지 않는 경우 종료
        scroll_count += random_scroll_times
        if len(followers) >= max_follower_count or new_height == last_height:
            break

    return followers



def get_followers_names_from_acc(driver, account, max_follower_count):
    """특정 계정의 팔로워 목록을 가져옵니다."""
    if not open_followers_modal(driver, account):
        return []

    # 팔로워 모달에서 스크롤 및 수집
    try:
        child_element = find_element_with_retry(driver, By.CSS_SELECTOR, "div[style='height: auto; overflow: hidden auto;']")
        if not child_element:
            print(f"\n{account}계정의 팔로워 목록을 열 수 없습니다.")
            return []

        parent_element = child_element.find_element(By.XPATH, "..")
        follower_list_modal = parent_element
        followers = scroll_followers_modal(driver, follower_list_modal, max_follower_count)

        print(f'\n{account} 계정에서 가져온 팔로워 수 : {len(followers)}명 \n(계정 페이지에 적혀있는 팔로워 수와 다를 수 있습니다.)')
        return followers

    except NoSuchElementException:
        print("\n팔로워 이름을 가져오는 도중 필요한 요소를 찾을 수 없습니다.\n")
    except TimeoutException:
        print("\n팔로워 이름을 가져오는 도중 요청한 작업이 시간 내에 완료되지 않았습니다.\n")
    except Exception as e:
        print(f"\n팔로워 이름을 가져오는 도중 예기치 못한 오류가 발생했습니다: {e}\n")
    return []


def fetch_follower_names(driver):
    """자바스크립트를 실행하여 '회원님을 위한 추천' 섹션을 제외한 'dir="auto"' 속성을 가진 span의 텍스트를 리스트로 반환"""
    get_follower_names_by_js = """
    var recommendationSpan = Array.from(document.querySelectorAll('span')).find(span => span.textContent.includes('회원님을 위한 추천'));
    var skipSection = recommendationSpan ? recommendationSpan.parentElement.nextElementSibling : null;
    var followers_names = [];
    
    document.querySelectorAll('span[dir="auto"]').forEach(function(span) {
        if (!skipSection || !skipSection.contains(span)) {
            if (span.parentElement && 
                span.parentElement.parentElement && 
                span.parentElement.parentElement.parentElement && 
                span.parentElement.parentElement.parentElement.tagName === 'A') {
                followers_names.push(span.textContent.trim());
            }
        }
    });
    return followers_names;
    """
    followers_names = driver.execute_script(get_follower_names_by_js)
    return followers_names



def get_user_info(driver, follower_name, total_followers, current_index):

    # 팔로워 페이지로 이동
    driver.get(f"https://www.instagram.com/{follower_name}/")

    # 팔로워 정보 추출 시작 시간
    follower_start_time = time.time()

    # 랜덤 스크롤링
    random_scroll(driver, 3, 4)
    # time.sleep(random.uniform(3, 4))  # 랜덤한 시간으로 대기 (체류시간 늘리기)

    # 현재 진행 상황을 출력합니다.
    print(f'\nhttps://www.instagram.com/{follower_name}/')
    print(f'{current_index} / {total_followers} - ({(current_index/total_followers)*100:.2f}%)')
    

    # 팔로워 정보를 담을 딕셔너리
    follower_info = {'팔로워 ID': follower_name}
    
    # 공개/비공개 여부 추출
    try:
        driver.find_element(By.XPATH, "//span[contains(text(), '게시물')]")
        is_private = False
    except NoSuchElementException:
        is_private = True

    follower_info['계정 상태'] = '비공개' if is_private else '공개'

    # 팔로워 수 추출
    try:
        if is_private:
            followers_count_element = driver.find_element(By.XPATH, "//li[contains(., '팔로워')]/descendant::span[text()]")
        else:
            followers_count_element = find_element_with_retry(driver, By.XPATH, "//a[contains(., '팔로워')]/descendant::span[text()]")
        
        follower_info['팔로워 수'] = followers_count_element.text
    except NoSuchElementException:
        follower_info['팔로워 수'] = '정보 없음'

    # 팔로잉 수 추출
    try:
        if is_private:
            following_count_element = driver.find_element(By.XPATH, "//li[contains(., '팔로우')]/descendant::span[text()]")
        else:
            following_count_element = find_element_with_retry(driver, By.XPATH, "//a[contains(., '팔로우')]/descendant::span[text()]")               
        
        follower_info['팔로잉 수'] = following_count_element.text
    except NoSuchElementException:
        follower_info['팔로잉 수'] = '정보 없음'

    # 팔로워 정보 추출 종료 시간
    follower_end_time = time.time()

    # 비공개 계정이고 팔로워 수와 팔로잉 수 정보 못가져오면 로그인 한 계정이 일시정지 당한 것으로 간주
    if is_private and follower_info['팔로워 수'] == '정보 없음' and follower_info['팔로잉 수'] == '정보 없음':
        print("**** 경고 )) 현재 로그인한 계정이 일시적으로 정지 상태일 수 있습니다. ****")
        raise Exception("계정 정지 상태로 인해 더이상 진행할 수 없기에 프로그램이 종료됩니다...")

    # 팔로워 링크 추가
    follower_info['팔로워 링크'] = f"https://www.instagram.com/{follower_name}/"

    follower_elapsed_time = follower_end_time - follower_start_time

    return follower_info, follower_elapsed_time


def random_scroll(driver, min, max):
    # 한 팔로워 페이지에 머무는 총 시간을 랜덤으로 설정
    total_time = random.uniform(min, max)
    start_time = time.time()

    # 지정된 시간 동안 스크롤을 랜덤하게 진행
    while (time.time() - start_time) < total_time:
        # 스크롤 양과 대기 시간을 랜덤으로 설정
        scroll_amount = random.uniform(300, 600)  # 랜덤 스크롤 양
        wait_time = random.uniform(1, 2)  # 랜덤 대기 시간
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        time.sleep(wait_time)
