# 크롤링 관련 라이브러리
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

# 시스템 관련 라이브러리
import time
import sys
import threading
import os
import re

# 크롬 드라이버 관련 라이브러리(직접 개발한 것)
from UbuntuChromeDriver import UbuntuChromeDriver

def remove_dash(date_str):
    return re.sub('-', '', date_str)

def wait_for_crawling():
    while True:
        sys.stdout.write("\r...")
        time.sleep(1)
        sys.stdout.write("\r  ")
        time.sleep(1)
        sys.stdout.flush()

def posts_loading(driver: UbuntuChromeDriver):
    """
    블로그 검색 결과를 끝까지 로딩
    """
    last_page_height = driver.execute_script("return document.documentElement.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(3.0)
        new_page_height = driver.execute_script("return document.documentElement.scrollHeight")

        if new_page_height == last_page_height:
            break
        last_page_height = new_page_height

def crawl_naver_blogs(keyword: str, include_txt: str, exclude_txt: str, start_date: str, end_date: str, count: int, save_path: str):
    
    driver = UbuntuChromeDriver()
    BASE_URL = "https://search.naver.com"
    URL = f"{BASE_URL}/search.naver?query={keyword}&nso=so:r,p:from{start_date}to{end_date}&where=blog&sm=tab_opt"
    print(f"\n[{URL}]에 대한 크롤링을 진행합니다.")
    driver.get(URL)
    driver.implicitly_wait(3)
    
    # 블로그 검색 결과 로딩
    posts_loading(driver)
    
    post_elems = driver.find_elements(By.CSS_SELECTOR, "#_view_review_body_html > div > more-contents > div > ul > li")

    # num, title, content, date, nickname = []
    info = {
        'count': [],
        'link': [],
        'content': [],
        'date': [],
        'nickname': [],
    }

    counter = 1
    idx = 0
    while counter <= count and idx < len(post_elems):
        post = post_elems[idx]
        info['count'].append(counter)
        info['link'].append(post.find_element(By.CSS_SELECTOR, "div.total_wrap.api_ani_send > a.thumb_single").get_attribute('href'))
        info['nickname'].append(post.find_element(By.CSS_SELECTOR, "div.total_info > div.total_sub > span > span > span.elss.etc_dsc_inner > a").text)
        info['date'].append(post.find_element(By.CSS_SELECTOR, "div.total_info > div.total_sub > span > span > span.etc_dsc_area > span").text)
        info['content'].append(post.find_element(By.CSS_SELECTOR, "div.total_group > div > a > div").text)
        counter += 1
        idx += 1
            

    # dict to df
    df = pd.DataFrame()
    df['번호'] = info['count']
    df['블로그주소'] = info['link']
    df['닉네임'] = info['nickname']
    df['작성일자'] = info['date']
    df['블로그내용'] = info['content']

    with open(os.path.join(save_path, f'{keyword}.txt'), 'w') as f:
        for index, row in df.iterrows():
            f.write(f"총 {COUNT}건 중 {index+1}번째 블로그 데이터를 수집합니다============ \n")
            f.write(f"1. 블로그주소: {row['블로그주소']}\n")
            f.write(f"2. 작성자 닉네임: {row['닉네임']}\n")
            f.write(f"3. 작성 일자: {row['작성일자']}\n")
            f.write(f"4. 블로그내용: {row['블로그내용']}\n")
            f.write("\n")
    df.to_csv(f'{save_path}/{keyword}.csv',index=False, encoding='utf-8')
    df.to_excel(f'{save_path}/{keyword}.xlsx', index=False)
 
    # 크롬 드라이버 종료
    driver.quit()
    time.sleep(1)

if __name__ == "__main__":
    if not os.path.exists('outputs'):
        os.makedirs('outputs')
        
    current_directory = os.getcwd()
    print("현재 디렉토리:", current_directory)
    
    # 정해진 출력문
    print("===========================================================")
    print(" 연습문제 6-5 블로그 크롤러 : ver Ubuntu")
    print("========================================================")
    KEYWORD = input("1.크롤링할 키워드는 무엇입니까?(예: 여행): ") or "여행"
    include_txt = input('2. 결과에서 반드시 포함하는 단어를 입력하세요(예: 국내, 바닷가)\n \
(여러개일 경우 , 로 구분해서 입력하고 없으면 엔터 입력하세요): ')
    exclude_txt = input('3. 결과에서 제외할 단어를 입력하세요(예: 분양권, 해외)\n \
(여러개일 경우 , 로 구분해서 입력하고 없으면 엔터 입력하세요): ')
    start_date = input('4. 조회를 시작할 날짜를 입력하세요(예:2017-01-01) : ')
    start_date = remove_dash(start_date)
    end_date = input('5. 조회를 종료할 날짜를 입력하세요(예:2017-12-31) : ')
    end_date = remove_dash(end_date)
    COUNT = int(input('6. 크롤링 할 건수는 몇건입니까?(최대 1000건): '))
    save_path = input(f'7. 파일을 저장할 폴더명만 쓰세요(default: {current_directory}/outputs) : ') or current_directory + '/outputs'
    
    # 크롤링 진행사항을 알려주는 스레드
    wait_thread = threading.Thread(target=wait_for_crawling)
    wait_thread.daemon = True  # 메인 스레드가 종료되는 경우 함께 종료되도록 설정
    wait_thread.start()
    
    # 크롤링 시작
    crawl_naver_blogs(KEYWORD, include_txt, exclude_txt, start_date, end_date, COUNT, save_path)
