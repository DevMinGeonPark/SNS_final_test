import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import quote #url encoding
import urllib.request

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# 시스템 관련 라이브러리
import time
import sys
import threading
import os
import requests

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
        
def crawling(KEYWORD, C_NUM, SAVE_PATH):
    # pixabay.com은 headless 키워드로 실행하면 봇으로 인식합니다.
    driver = UbuntuChromeDriver(headless=False)
    page_num = 1
    img_url = []
    while True:
        # 입력받은 수 이상은 필요없으므로 break
        if len(img_url) > C_NUM: 
            img_url = img_url[:C_NUM]
            break
        URL = f"https://pixabay.com/ko/images/search/{KEYWORD}?pagi={page_num}"
        
        driver.get(URL)
        driver.implicitly_wait(10)

        html = driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        
        # 이미지 태그를 가진 컨테이너 태그 선택
        container = soup.select("#app > div:nth-child(1) > div > div:nth-child(3) > div:nth-child(4) > div > div")
        
        for img_container in container:
            if len(img_url) > C_NUM: break
            # img 태그 선택
            imgs = img_container.select("div > a > img")
            for img in imgs:
                url = img['src']
                # url이 src에 없는 경우
                if not url.startswith("https://cdn.pixabay.com/photo/"):
                    url = img['data-lazy-src']
                img_url.append(url)
        
        page_num += 1
        
        
    for i, url in tqdm(enumerate(img_url), total=len(img_url), desc="Downloading images"):
            filename = f"{i+1}.jpg"
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
    print("===========================================================")
    print("pixabay 사이트에서 이미지를 검색하여 수집하는 크롤러 입니다.")
    print("===========================================================")
    KEYWORD = input("1. 크롤링할 이미지의 키워드는 무엇입니까?: ") or "고양이"
    C_NUM = int(input("2. 크롤링 할 건수는 몇건입니까?: ")) or 10
    SAVE_PATH = input(f"파일로 저장될 경로만 쓰세요. (Defult: {current_directory}/outputs): ") or f"{current_directory}/outputs"
    
        
    if not os.path.exists(SAVE_PATH):
        print("잘못된 경로입니다. 프로그램을 종료합니다.")
        sys.exit(1)
    
    # 크롤링 시작
    wait_thread = threading.Thread(target=wait_for_crawling)
    wait_thread.daemon = True  # 메인 스레드가 종료되는 경우 함께 종료되도록 설정
    wait_thread.start()
    
    # 크롤링 시작
    crawling(KEYWORD, C_NUM, SAVE_PATH)