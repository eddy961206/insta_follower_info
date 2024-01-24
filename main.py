from program_actions import (initialize_driver_test, read_account_data_from_xlsx, initialize_driver, get_feed_blog_count,
                          get_keyword_and_count,fetch_single_data_from_account_datas, print_final_output)
from insta_utils import (get_followers, login_to_insta, login_to_naver, get_feed_blog_links, save_to_excel, search_blog_by_keyword, is_already_commented,
                          CommentNotAllowedException, like_blog_post, extract_blog_content, 
                          extract_author_name, generate_comment_with_ai, post_comment, 
                          logout_of_naver)
from api import OpenAIChatClient

likeminPauseTime = 0.5 
likemaxPauseTime = 6.5

# 메인 로직 함수
def main_logic():
    
    try:
            
        print('\n\n===============  프로그램 작동중.... ===============')
        print('\n\n=== 화면은 가려져도 되지만 크롬 창 최소화는 하지 말아주세요 ===')

        # 웹드라이버 초기화
        # driver = initialize_driver()
        driver = initialize_driver_test()
        
        # 로그인
        if not login_to_insta(driver, id, pw):
            print(f"\n계정 {id}으로 로그인에 실패했습니다. 프로그램을 종료합니다.")
            return
        else :
            print(f"\n계정 {id}으로 로그인 하였습니다.")


        accounts = ['hanok_meatrestaurant', 'jyong2']

        # 여기에 각 계정을 순회하며 팔로워 목록을 가져오는 로직을 구현
        for account in accounts:

            # 각 계정별로 팔로워 정보를 가져오고 저장
            followers_data = get_followers(driver, account)

            # 데이터를 엑셀로 저장
            save_to_excel(followers_data, account)



        ### 진행상황을 사용자에게 상세히 print 해줘야 함. 프로그램 진행되고 나면 이게 잘 진행되고 있는지 알기 힘들기 때문. 
        ### 입력받은 계정들 중 몇번째 계정을 진행중인지, 가져온 팔로워의 명수는 몇 명인지, 마지막엔 전체 입력받은 계정 개수 대비 몇 개가 성공하고 실패했는지, 그리고 그 백분율 등.
            
        # 각 입력받았던 계정정보들로 이동 (반복문) 예 : 'https://www.instagram.com/계정이름/'
            
            # '팔로워' 버튼 클릭 (팔로워 목록 다 뜰때까지 나올때까지 대기)

            # 팔로워 목록이 다 떴으면 아래로 끝까지 스크롤 하며 목록 안의 닉네임들을 추출 (스크롤 속도는 입력받은 두개의 숫자(최소, 최대)안의 랜덤한 시간으로 스크롤.)
        
            # 닉네임 하나하나마다 반복문 돌며 해당 팔로워의 페이지로 이동. 예 : ''https://www.instagram.com/닉네임/''
                
                # 팔로워의 페이지가 열리면 [닉네임,  팔로워 수, 팔로우 수, 아이디 공개 비공개 여부, 계정 링크] 정보를 추출해서 저장

        # 각 입력받았던 계정별로 시트를 따로 해서 엑셀로 저장
        # '계정A 분석', '팔로워 ID', '팔로워 수', '팔로잉 수', '공개, 비공개 여부', 'ID링크' 컬럼으로. 


        print('===== ***** ===== *****  ===== ***** ===== *****')
        print('\n댓글 달기 및 좋아요 누르기 프로그램 실행이 모두 완료되었습니다.')
                
        driver.quit()

    except Exception as e:
        print(f"\n\n**** 프로그램 실행 오류 : {e}\n"
              "\n프로그램이 예기치 못하게 중단 되었습니다.")


# 계정마다 반복
def process_account(driver, id, pw, nickname, openai_client, additional_comment,
                    feed_blog_count, keyword, keyword_blog_count, sorting_preference):

    ##########################################################
    # 블로그 글 하나씩 반복  
    comment_count = 0
    like_count = 0
    not_need_comment_count = 0
    not_need_like_count = 0
    
    for index, link in enumerate(link_list, start=1):
        
        # 진행상황 표시
        progress_percentage = (index / len(link_list)) * 100
        print('\n------------------------------------------------')
        print(f'{len(link_list)}개 중 {index}번째 링크 처리 중 ({progress_percentage:.1f}%):\n{link}')

        # 이미 댓글이 작성된 글인지 확인
        try:
            if is_already_commented(driver, link, nickname):
                print(f"\n'{id}'계정에 해당하는 댓글이 이미 존재합니다(닉네임-{nickname}). 다음 블로그 링크로 넘어갑니다.")
                not_need_comment_count += 1
                continue
        except CommentNotAllowedException as e:
            print(e)
            continue

        # 좋아요 처리
        like_count, not_need_like_count \
            = like_blog_post(driver, link, likeminPauseTime, likemaxPauseTime, 
                             like_count, not_need_like_count)
        
        # 글 내용 추출
        blog_content, error = extract_blog_content(driver)
        if error:
            print(error)
            continue
        
        # 작성자 이름 추출
        author_name = extract_author_name(driver)

        # AI를 통한 댓글 생성
        comment, error = generate_comment_with_ai(openai_client, blog_content, author_name, additional_comment)
        if error:
            print(error)
            continue
        
        # 댓글 등록
        if post_comment(driver, link, comment, index):
            comment_count += 1
        else:
            print(f'\n댓글 등록 실패 링크 : {link}. 다음 글로 넘어갑니다.')

    # 결과 출력
    print_final_output(id, len(link_list), not_need_comment_count, 
                       comment_count, like_count, not_need_like_count)
    
    # 로그아웃
    logout_of_naver(driver)


