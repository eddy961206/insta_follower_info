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
    followers_button = find_element_with_retry(driver, By.PARTIAL_LINK_TEXT, "팔로워")
    if followers_button:
        followers_button.click()
        return True
    else:
        print(f"\n\n{account}계정의 팔로워 버튼을 누를 수 없습니다.")
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
        followers = get_followers_names_from_acc_from_modal(driver)

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

        print(f'\n{account}계정에서 가져온 팔로워 수 : {len(followers)}')
        return followers

    except NoSuchElementException:
        print("\n팔로워 이름을 가져오는 도중 필요한 요소를 찾을 수 없습니다.\n")
    except TimeoutException:
        print("\n팔로워 이름을 가져오는 도중 요청한 작업이 시간 내에 완료되지 않았습니다.\n")
    except Exception as e:
        print(f"\n팔로워 이름을 가져오는 도중 예기치 못한 오류가 발생했습니다: {e}\n")
    return []


def get_followers_names_from_acc_from_modal(driver):
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
    time.sleep(random.uniform(3, 4))  # 랜덤한 시간으로 대기 (체류시간 늘리기)

    # 현재 진행 상황을 출력합니다.
    print(f'https://www.instagram.com/{follower_name}/')
    print(f'{current_index}/{total_followers} - ({(current_index/total_followers)*100:.2f}%)')
    

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

    # 비공개 계정이고 팔로워 수와 팔로잉 수 정보 못가져오면 로그인 한 계정이 일시정지 당한 것으로 간주
    if is_private and follower_info['팔로워 수'] == '정보 없음' and follower_info['팔로잉 수'] == '정보 없음':
        print("**** 경고 )) 현재 로그인한 계정이 일시적으로 정지 상태일 수 있습니다. ****")
        raise Exception("계정 정지 상태로 인해 더이상 진행할 수 없기에 프로그램이 종료됩니다...")

    # 팔로워 링크 추가
    follower_info['팔로워 링크'] = f"https://www.instagram.com/{follower_name}/"


    return follower_info



































def set_search_sorting(driver, sorting_preference):
    """블로그 검색 결과 페이지에서 정렬 방식 설정"""
    try:
        sorting_preference = 'date' if sorting_preference == '최신순' else 'sim'
        sort_select = Select(driver.find_element(By.CSS_SELECTOR, "select.select__IkE09"))
        sort_select.select_by_value(sorting_preference)
    except Exception as e:
        print(f"블로그 검색결과 정렬 방식 설정 중 오류 발생: {e}")


def get_feed_blog_links(driver, max_count):
    """블로그 피드 링크 추출"""
    feed_url = "https://m.blog.naver.com/FeedList.naver"
    link_selector = "a.link__iGhdI"
    context = "서로이웃 피드"
    return fetch_blog_links(driver, feed_url, link_selector, max_count, context)


def search_blog_by_keyword(driver, keyword, max_count, sorting_preference):
    """키워드로 블로그 검색하고 링크 추출"""
    search_url = f"https://m.blog.naver.com/SectionPostSearch.naver?orderType=sim&searchValue={keyword}"
    link_selector = "a.link__OVpnJ"
    context = "키워드 검색 결과"
    return fetch_blog_links(driver, search_url, link_selector, max_count, context, sorting_preference)


def fetch_blog_links(driver, url, link_selector, max_count, context, sorting_preference=None):
    """공통 링크 추출 함수"""
    try:
        driver.get(url)

        time.sleep(2)
        # 키워드로 블로그 검색할 때만 정렬순서 세팅
        if sorting_preference:
            set_search_sorting(driver, sorting_preference)

        time.sleep(2)
    except Exception as e:
        print(f"{context} 링크 추출 페이지로 이동하는데 실패했습니다: {e}")
        return None

    link_list = scroll_to_bottom(driver, link_selector, max_count, context)

    if len(link_list) < max_count:
        print(f"{context}에서 충분한 수의 링크를 찾지 못했습니다.")

    return link_list


def navigate_to_comment_page(driver, link):
    """블로그 글의 댓글 페이지로 이동"""
    try:
        # URL을 분해하여 댓글 페이지의 링크 생성
        url_parts = link.split('&')  # https://m.blog.naver.com/PostView.naver?blogId=u_many_yeon&logNo=223316337997&navType=by -> https://m.blog.naver.com/CommentList.naver?blogId=u_many_yeon&logNo=223316337997
        comment_page_link = link.replace("PostView.naver", "CommentList.naver").split('&')[0] + '&' + url_parts[1]
        driver.get(comment_page_link)

        # 댓글 입력창이 로드될 때까지 최대 10초 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".u_cbox_inbox"))
        )
        
        return True
    except Exception as e:
        print(f"댓글 페이지로 이동하는 도중 오류가 발생했습니다: {e}")
        return False


def is_already_commented(driver, link, nickname):
    """특정 닉네임의 존재 여부 확인(댓글 이미 달았는지)"""
    try:
        # 댓글 페이지로 이동
        navigate_to_comment_page(driver, link)

        # 스크롤을 맨 위로 이동
        scroll_to_top(driver)     

        # 닉네임이 페이지에 존재하는지 확인
        return bool(driver.find_element(By.XPATH, f"//span[@class='u_cbox_nick' and contains(text(), '{nickname}')]"))

    except UnexpectedAlertPresentException:
        # 댓글 페이지에서 경고창이 나타나면 처리
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            alert.accept()
            raise CommentNotAllowedException(f"댓글을 달 수 없는 블로그 글입니다: {alert_text}")
        except NoAlertPresentException:
            print("경고창을 처리하는 중 오류 발생")
        return False
    except NoSuchElementException:
        # 닉네임 요소 자체가 페이지에 없으면 False 반환
        return False
    except Exception as e:
        print(f"이미 댓글 단 블로그인지 확인하는 도중 에러 발생 : {str(e)}")
        return False


def like_blog_post(driver, link, likeminPauseTime, likemaxPauseTime, like_count, not_need_like_count):
    """좋아요 클릭"""
    driver.get(link)  # 블로그 본문 페이지로 이동

#   #### 클라이언트의 요청. 체류시간 상관 없어하심. 체류시간 중요하지만 #####
    # time.sleep(1)
    # scroll_through_post(driver, likeminPauseTime, likemaxPauseTime)
#   #### 클라이언트의 요청. 체류시간 상관 없어하심. 체류시간 중요하지만 #####

    try:
        heart_btn_selector = "a.u_likeit_list_btn._button._sympathyBtn"
        # 좋아요 버튼이 있는지 먼저 확인
        if driver.find_elements(By.CSS_SELECTOR, heart_btn_selector):
            heart_btn = find_element_with_retry(driver, By.CSS_SELECTOR, heart_btn_selector)
            time.sleep(0.2)

            if heart_btn and heart_btn.get_attribute("aria-pressed") == "false":
                driver.execute_script("arguments[0].click();", heart_btn)
                time.sleep(0.5)
                like_count = handle_alert(driver, like_count)
            else:
                print('\n이미 좋아요가 눌려있습니다.')
                not_need_like_count += 1
        else:
            print("\n좋아요 할 수 없는 블로그 글입니다.")
    except UnexpectedAlertPresentException as e:
        print(f'\n좋아요 클릭 중 오류 발생: {str(e)}')

    return like_count, not_need_like_count


def handle_alert(driver, like_count):
    """좋아요 버튼 예외시 alert 확인 처리"""
    try:
        alert = driver.switch_to.alert
        alert.accept()
        print("\n해당 컨텐츠에 더 이상 좋아요 할 수 없습니다.")
    except NoAlertPresentException:
        like_count += 1
        print("\n좋아요 눌림")
    
    return like_count


def scroll_to_bottom(driver, link_selector, max_count, context):
    """페이지 끝까지 스크롤하며 링크 수집"""
    link_list = []
    last_link = None
    wait = WebDriverWait(driver, 10)

    while len(link_list) < max_count:
        # 페이지 끝으로 스크롤
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # 새로운 콘텐츠 로드 대기
        try:
            wait.until(lambda d: d.find_element(By.CSS_SELECTOR, link_selector) != last_link)
        except TimeoutException:
            print(f"{context}에서 충분한 수의 링크를 찾지 못했습니다.")
            break

        # 현재 페이지의 모든 링크 가져오기
        current_links = driver.find_elements(By.CSS_SELECTOR, link_selector)
        
        # 마지막 링크 업데이트
        last_link = current_links[-1] if current_links else None

        # 새로운 링크만 추출
        new_links = [link.get_attribute("href") for link in current_links if link.get_attribute("href") not in link_list]

        # 새로운 링크 추가
        link_list.extend(new_links)

        if len(link_list) >= max_count:
            print(f"\n{context}에서 찾은 글이 지정하신 최대 글 수 {max_count}개에 도달했습니다.")
            break

    return link_list[:max_count]

 

def extract_blog_content(driver):
    """Extract the blog content from a blog post."""
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    blog_content_div = soup.find("div", class_="se-main-container")
    if not blog_content_div:
        return None, "\n블로그 본문을 찾을 수 없습니다.\n다음 글로 넘어갑니다."
    
    blog_content = ''
    for element in blog_content_div.descendants:
        if element.name == 'span':
            if element.string:
                blog_content += element.string.strip() + ' '
    
    if not blog_content:
        return None, "\n블로그 본문 내용이 비어있습니다.\n다음 글로 넘어갑니다."
    
    print(f'\n본문 글 : \n{blog_content}')
    
    return blog_content, None


def extract_author_name(driver):
    """Extract the author's nickname from the blog post."""
    try:
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        author_div = soup.find("div", class_="blog_author")
        if author_div and author_div.find("strong", class_="ell"):
            author_name = author_div.find("strong", class_="ell").get_text().strip()
        else:
            author_name = " "
    except Exception as e:
        print(f'\n작성자 닉네임 추출중 오류 발생: {str(e)}')
        author_name = " "

    print("\n작성자 : ", author_name)

    return author_name


def generate_comment_with_ai(openai_client, blog_content, author_name, additional_comment):
    """Generate a comment for a blog post using OpenAI."""
    try:
        comment = openai_client.generate_comment(blog_content, author_name, additional_comment)

        print(f"\n생성된 댓글 : \n{comment}")

        return comment, None
    except Exception as e:
        return None, f'댓글 생성 중 오류 발생: {str(e)}\n 다음 글로 넘어갑니다..'


def post_comment(driver, link, comment, index):
    """Post a comment on a blog post and return True if successful."""
    try:
        if not navigate_to_comment_page(driver, link):
            return False
        
        comment_box = find_element_with_retry(driver, By.CSS_SELECTOR, "#naverComment__write_textarea")
        
        comment_box.clear()
        comment_box.send_keys(comment)

        submit_button = find_element_with_retry(driver, By.CSS_SELECTOR, ".u_cbox_btn_upload")
        time.sleep(0.5)
        submit_button.click()
        print(f'\n\n{index}번째 블로그 글에 댓글 등록이 완료됐습니다.')
        print('--------------------------------------')

        return True
    except Exception as e:
        print(f'\n\n{index}번째 블로그 글에 댓글 등록이 실패했습니다 : {e}')
        traceback.print_exc()
        return False


def logout_of_naver(driver):
    """Logs out of Naver."""
    try:
        driver.get("https://www.naver.com/")
        logout_button = find_element_with_retry(driver, By.CSS_SELECTOR, ".MyView-module__btn_logout___bsTOJ")
        time.sleep(0.3)
        logout_button.click()
    except NoSuchElementException:
        print("로그아웃 버튼을 찾을 수 없습니다.")
    except ElementClickInterceptedException:
        print("로그아웃 버튼을 클릭할 수 없습니다.")


class CommentNotAllowedException(Exception):
    """예외 클래스: 댓글을 달 수 없는 블로그 글을 나타냄"""
    def __init__(self, message="댓글을 달 수 없는 블로그 글입니다. 다음 블로그 링크로 넘어갑니다."):
        self.message = message
        super().__init__(self.message)