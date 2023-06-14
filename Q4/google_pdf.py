# 크롤링 관련 라이브러리
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from urllib.parse import quote #url encoding

# 시스템 관련 라이브러리
import time
import sys
import threading
import os
import re
import requests

#진행도 출력
from tqdm import tqdm


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

def crawl_google_pdf(keyword: str, count: int, save_path: str):
    driver = UbuntuChromeDriver(headless=False)
    BASE_URL = "https://www.google.com/search?"
    SEARCH_RANGE = 10  # 한 페이지에서 검색할 거리

    urls = []
    f_count = 0
    
    while len(urls) < count or f_count < 10:  # 최대 10번까지 시도
        URL = f"{BASE_URL}q={quote(KEYWORD)}+filetype%3D.pdf&sxsrf=APwXEdeHVOoEyMWEFPK5vncVRBOniRrJKA:1686696393033&ei=yfGIZJPQAdaohwOOqJKoDw&start={SEARCH_RANGE}&sa=N&ved=2ahUKEwjT2ObaqcH_AhVW1GEKHQ6UBPUQ8tMDegQIAxAE&biw=1920&bih=914&dpr=1"
        driver.get(URL)
        driver.implicitly_wait(60)
        print(f"\n[{driver.current_url}] 에 대한 크롤링을 진행합니다.")
        

        # PDF 파일 링크 추출
        elems = driver.find_elements(By.CSS_SELECTOR, "#rso > div")
        
        for elem in elems:
            try:
                soup = BeautifulSoup(elem.get_attribute("innerHTML"), 'html.parser')
                data = soup.find_all('a')
                for url_data in data:
                    url_data = url_data.get('href')
                    if url_data.index('pdf') != -1 and url_data.startswith('https://'):
                        print(url_data)
                        urls.append(url_data)
            except Exception as e:
                pass
            
                    
        print("현재 페이지 이동을 통한 검색은 reCAPTCHA로 인해 불가능합니다.")
        break
    
        # SEARCH_RANGE+=10  # 다음 페이지에서 검색할 거리를 10개씩 증가
        # f_count += 1  # 시도 횟수 증가

    # 최대 다운로드 개수를 초과하는 경우 개수를 축소
    if len(urls) > count:
        urls = urls[:count]
        
    print("직접 다운로드 불가능한 파일은 제외하였습니다.")
    print(f"총 {len(urls)}개의 PDF 파일을 다운로드합니다.")
 
    # 다운로드할 PDF 파일들을 저장할 디렉토리 생성
    os.makedirs(save_path, exist_ok=True)

    # PDF 파일 다운로드
    for i, url in tqdm(enumerate(urls), total=len(urls), desc="Downloading PDF"):
        try:
            response = requests.get(url)
            if response.status_code == 200 and response.content:
                filename = f"{i+1}.pdf"
                filepath = os.path.join(save_path, filename)
                with open(filepath, "wb") as f:
                    f.write(response.content)
        except Exception as e:
            print(f"{url} 다운로드 실패: {e}")
            continue

    # 크롬 드라이버 종료
    driver.quit()
    time.sleep(1)

    

        
    for i, url in tqdm(enumerate(urls), total=len(urls), desc="Downloading PDF"):
            filename = f"{i+1}.pdf"
            filepath = os.path.join(SAVE_PATH, filename)
            response = requests.get(url)
            with open(filepath, "wb") as f:
                f.write(response.content)



if __name__ == "__main__":
    if not os.path.exists('outputs'):
        os.makedirs('outputs')
        
    current_directory = os.getcwd()
    print("현재 디렉토리:", current_directory)
    
    # 정해진 출력문
    KEYWORD = input("1. 크롤링할 키워드는 무엇입니까?: ")
    COUNT = int(input("2. 크롤링 할 건수는 몇건입니까?(최대 1000건): "))
    SAVE_PATH = input(f"파일로 저장될 경로만 쓰세요. (Defult: {current_directory}/outputs): ") or f"{current_directory}/outputs"
    
    # 크롤링 시작
    wait_thread = threading.Thread(target=wait_for_crawling)
    wait_thread.daemon = True  # 메인 스레드가 종료되는 경우 함께 종료되도록 설정
    wait_thread.start()
    
    if not os.path.exists(SAVE_PATH):
        print("잘못된 경로입니다. 프로그램을 종료합니다.")
        sys.exit(1)
    
    crawl_google_pdf(KEYWORD, COUNT, SAVE_PATH)
