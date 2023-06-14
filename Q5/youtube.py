#크롤링 관련 라이브러리
import pandas as pd
from bs4 import BeautifulSoup

# 시스템 관련 라이브러리
import time
import sys
import threading
import os

# 진행사항 관련 라이브러리
from tqdm import tqdm

# 크롬 드라이버 관련 라이브러리(직접 개발한 것)
from UbuntuChromeDriver import UbuntuChromeDriver


def wait_for_crawling():
    while True:
        sys.stdout.write("\r...")
        time.sleep(1)
        sys.stdout.write("\r  ")
        time.sleep(1)
        sys.stdout.flush()
        
        
def youtube_lodaing(driver: UbuntuChromeDriver):
    """_summary_:
        유튜브 검색 결과를 끝까지 로딩
    """
    last_page_height = driver.execute_script("return document.documentElement.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(3.0)
        new_page_height = driver.execute_script("return document.documentElement.scrollHeight")

        if new_page_height == last_page_height:
            break
        last_page_height = new_page_height
        
                
def formatting_str(v_count: int, c_count: int, url: str, id: str, date: str, comment: str):
    comment_title = f"{v_count} 번째 영상의 {c_count} 번째 댓글"
    comment_url = f"1. URL 주소: {url}"
    comment_id = f"2. 댓글 작성자명 : {id}"
    comment_date = f"3. 댓글 작성일자: {date}"
    comment = f"4. 댓글 내용: {comment}"
    
    return f"{comment_title}\n--------------------------------------------------\n{comment_url}\n{comment_id}\n{comment_date}\n{comment}\n\n"


def to_txt(df, comment_count: str, save_path: str):
    with open(save_path, 'w', encoding='utf-8') as f:
        v_count = 1
        c_count = 1
        for i in range(len(df)):
            if c_count == comment_count+1: 
                c_count=1
                v_count+=1
            formatted_str = formatting_str(v_count, c_count, df.iloc[i]['URL 주소'], df.iloc[i]['댓글작성자명'], df.iloc[i]['댓글작성일자'], df.iloc[i]['댓글내용'])
            f.write(formatted_str)
            f.write('\n')
            c_count+=1
            
            
def crawl_youtube_comments(keyword: str, video_count: int, comment_count: int, save_path: str):
    
    driver = UbuntuChromeDriver()
    BASE_URL = "https://www.youtube.com"
    URL = f"{BASE_URL}/results?search_query={keyword}"
    print(f"\n[{URL}]에 대한 크롤링을 진행합니다.")
    driver.get(URL)
    driver.implicitly_wait(3)
    
    print("\n검색 결과를 끝까지 로딩합니다.")
    youtube_lodaing(driver);

    print("\n검색 결과의 URL 수집을 시작합니다.")
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    urls = []
    
    print("\nherf 전처리를 시작합니다.")
    for index, herf in tqdm(enumerate(soup.select('#dismissible > ytd-thumbnail > a')), desc=f"herf preprocessing progress ({video_count} videos)"):
        if index == video_count: # video_count 만큼만 수집
            break
        url = 'https://www.youtube.com' + herf['href']
        urls.append(url)
        
    # pandas 객체 생성
    df = pd.DataFrame(columns=['URL 주소','댓글작성자명', '댓글작성일자', '댓글내용'])

    # 각 URL에서 댓글 데이터 수집
    print("\nCrawling start")
    for url in tqdm(urls, desc="Crawling progress"):
        driver.get(url)
        driver.implicitly_wait(3)

        # 유튜브 댓글 끝까지 로딩
        youtube_lodaing(driver);

        # 유튜브 대댓글 열기
        elements = driver.find_elements_by_css_selector("#more-replies")
        for element in elements :
            driver.execute_script("arguments[0].click();", element)

        # 파싱
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        comments = soup.find_all("ytd-comment-thread-renderer", class_="style-scope ytd-item-section-renderer")

        # 댓글 데이터를 큰 pandas 객체로 변환하여 추가
        comment_data = []
        for comment in comments[:comment_count]:
            comment_text = comment.find("yt-formatted-string", id="content-text").text
            comment_id = comment.find("a", id="author-text").text.strip()
            comment_date = comment.find("yt-formatted-string", class_="published-time-text").text
            comment_data.append([url, comment_id, comment_date, comment_text])

        page_df = pd.DataFrame(comment_data, columns=['URL 주소','댓글작성자명', '댓글작성일자', '댓글내용'])
        df = pd.concat([df, page_df], ignore_index=True)

    # 데이터 저장
    print("data save start")
    to_txt(df, comment_count, f"{save_path}/{keyword} 검색결과(댓글 {video_count*comment_count}개).txt")
    df.to_csv(f'{save_path}/{keyword}.csv',index=True, encoding='utf-8')
    df.to_excel(f'{save_path}/{keyword}.xlsx', index=True)
    
    time.sleep(10)
 
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
    print(" 연습문제 8-3 유튜브 영상의 댓글 수집하기 : ver Ubuntu")
    print("========================================================")
    KEYWORD = input("유튜브에서 검색할 주제 키워드를 입력하세요(Defult: 올리브영): ") or "올리브영"
    VIDEO_COUNT = int(input("위 주제로 댓글을 크롤링할 유튜브 영상은 몇건 입니까?: "))
    COMMENT_COUNT = int(input("각 동영상에서 추출할 댓글은 몇건입니까?: "))
    save_path = input(f"크롤링 결과를 저장할 폴더명만 쓰세요. (Defult: {current_directory}/outputs): ") or f"{current_directory}/outputs"
    
    # 크롤링 진행사항을 알려주는 스레드
    wait_thread = threading.Thread(target=wait_for_crawling)
    wait_thread.daemon = True  # 메인 스레드가 종료되는 경우 함께 종료되도록 설정
    wait_thread.start()
    
    # 크롤링 시작
    crawl_youtube_comments(KEYWORD, VIDEO_COUNT, COMMENT_COUNT, save_path)