
import random
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def get_system_user_agent():
    """시스템의 현재 user-agent를 가져옵니다."""
    temp_driver = webdriver.Chrome()
    temp_driver.get("about:blank")
    user_agent = temp_driver.execute_script("return navigator.userAgent;")
    temp_driver.quit()
    return user_agent


def initialize_driver():
    """user-agent를 사용하여 크롬 드라이버 초기화"""
    user_agent = get_system_user_agent()
    options = Options()
    options.add_argument(f"user-agent={user_agent}")

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    return driver

def initialize_driver_test():
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=options)
    return driver


def get_feed_blog_count():
    """사용자로부터 피드 개수 입력받기"""
    feed_blog_input = input("\n서로이웃의 피드에서 작업할 블로그 글 개수를 입력해주세요\n(빈 값 입력시 피드에서 작업 생략): ")
    return int(feed_blog_input) if feed_blog_input.isdigit() else 0


def get_keyword_and_count():
    """사용자로부터 키워드, 키워드 검색 개수 입력받기"""
    keyword = input("\n키워드를 통한 블로그 검색 작업 시 사용할 키워드를 입력해주세요\n(빈 값 입력시 키워드 검색 생략): ")
    if keyword:
        keyword_blog_input = input("\n키워드 검색에서 작업할 블로그 글 개수를 입력해주세요\n(빈 값 입력시 키워드 검색 생략): ")
        keyword_blog_count = int(keyword_blog_input) if keyword_blog_input.isdigit() else 0

        if keyword_blog_count > 0:
            print("\n블로그 검색 결과 정렬 방식을 숫자로 선택해주세요:\n 1: 최신순 (기본값)\n 2: 정확도순\n(빈 값 입력시 최신순으로 자동 선택)")
            sorting_choice = input() or "1"
            sorting_preference = 'date' if sorting_choice != "2" else 'sim'
        else:
            sorting_preference = None
    else:
        keyword_blog_count = 0
        sorting_preference = None

    return keyword, keyword_blog_count, sorting_preference
   

def scroll_to_top(driver):
    """브라우저 스크롤을 맨 위로 이동하고 새로운 컨텐츠 로드될 때까지 반복"""
    while True:
        # 현재 스크롤 위치 저장
        current_scroll_position = driver.execute_script("return window.pageYOffset;")
        
        # 스크롤을 맨 위로 이동
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.5)  # 짧은 대기 시간

        # 새로운 스크롤 위치 확인
        new_scroll_position = driver.execute_script("return window.pageYOffset;")

        # 스크롤 위치가 변하지 않았다면 중단
        if current_scroll_position == new_scroll_position:
            break        



def find_element_with_retry(driver, by, value, delay=5):
    """요소가 나타날 때까지 찾기"""
    try:
        element = WebDriverWait(driver, delay).until(
            EC.element_to_be_clickable((by, value))
        )
        return element
    except TimeoutException:
        # 요소가 지정된 시간 내에 나타나지 않으면 None 반환하거나 예외 발생
        return None
        # 또는 필요에 따라 예외를 발생시킬 수 있습니다:
        # raise NoSuchElementException(f"요소가 {delay}초 동안 나타나지 않았습니다: {value}")
    
def find_elements_with_retry(driver, by, value, delay=5):
    """요소들이 나타날 때까지 찾기"""
    try:
        elements = WebDriverWait(driver, delay).until(
            EC.presence_of_all_elements_located((by, value))
        )
        return elements
    except TimeoutException:
        # 요소들이 지정된 시간 내에 나타나지 않으면 빈 리스트 반환
        return []




def scroll_through_post(driver, likeminPauseTime, likemaxPauseTime):
    """포스트 글 안에서 천천히 스크롤(체류시간 중요함)"""
    document_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.find_element(By.XPATH, "//body").send_keys(Keys.PAGE_DOWN)
        time.sleep(random.uniform(likeminPauseTime, likemaxPauseTime))
        now_scroll_height = driver.execute_script("return window.scrollY + window.innerHeight")
        if now_scroll_height >= document_height:
            break
        document_height = driver.execute_script("return document.body.scrollHeight")
    

def print_final_output(naver_id, link_list_total, not_need_comment_count, 
                       comment_count, like_count, not_need_like_count):
    # 좋아요 눌러야 할 블로그 수
    need_like_count = link_list_total - not_need_like_count

    # 좋아요 완수율 계산
    if need_like_count > 0:
        like_completion_rate = (like_count / need_like_count) * 100
    else:
        like_completion_rate = 0

    # 댓글 달아야 할 블로그 수
    need_comment_count = link_list_total - not_need_comment_count

    # 댓글 달기 완수율 계산
    if need_comment_count > 0:
        comment_completion_rate = (comment_count / need_comment_count) * 100
    else:
        comment_completion_rate = 0

    # 좋아요 완수율 계산
    if need_comment_count > 0:
        like_completion_rate = (like_count / need_comment_count) * 100
    else:
        like_completion_rate = 0

    # 결과 출력
    print('------------------------------------------------')
    print(f'\n\n{naver_id} 계정으로 블로그 댓글 달기가 완료되었습니다.\n\n'
        f'피드에서 긁어온 블로그 : {link_list_total}개\n'
        f'댓글이 안 달려있던 블로그 : {need_comment_count}개\n'
        f'좋아요가 안 달려있던 블로그 : {need_like_count}개\n\n'
        f'작성한 댓글 : {comment_count}개\n'
        f'좋아요 : {like_count}개\n')
    print(f'- 댓글 달기 완수율 : {comment_completion_rate:.1f}%')
    print(f'- 좋아요 완수율    : {like_completion_rate:.1f}%')
    print('------------------------------------------------')
