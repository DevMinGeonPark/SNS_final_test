import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import quote #url encoding

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
        
def formatting_str(count, task, notice_num_iteration, category, notice_name,
                   url_address, announcement_agency, demand_agency,
                   contract_method, input_datetime, joint_venture,
                   bidding_status):
    formatted_str = f"""{count}번째 공고 내용을 추출합니다.~~~~
1. 업무: {task}
2. 공고번호-차수: {notice_num_iteration}
3. 분류: {category}
4. 공고명: {notice_name}
5. URL 주소: {url_address}
6. 공고기관: {announcement_agency}
7. 수요기관: {demand_agency}
8. 계약방법: {contract_method}
9. 입력일시(입찰마감일시): {input_datetime}
10. 공동수급: {joint_venture}
11. 투찰여부: {bidding_status}
"""
    return formatted_str

def to_txt(df, save_path):
    count = 1
    with open(save_path, 'w', encoding='utf-8') as f:
        for i in range(len(df)):
            formatted_str = formatting_str(
                count,
                df.iloc[i]['업무'],
                df.iloc[i]['공고번호-차수'],
                df.iloc[i]['분류'],
                df.iloc[i]['공고명'],
                df.iloc[i]['URL주소'],
                df.iloc[i]['공고기관'],
                df.iloc[i]['수요기관'],
                df.iloc[i]['계약방법'],
                df.iloc[i]['입력일시'],
                df.iloc[i]['공동수급'],
                df.iloc[i]['투찰여부']
            )
            f.write(formatted_str)
            f.write('\n')
            count += 1

        
def crawling(KEYWORD, S_DATE, E_DATE, save_path):
    driver = UbuntuChromeDriver()
    
    URL = "https://www.g2b.go.kr:8101/ep/tbid/tbidFwd.do" # 입찰정보 검색 (기존의 사이트 g2b.go.kr에서 해당 페이지를 Frame으로 빼놓은 것)
    
    driver.get(URL)
    driver.implicitly_wait(3)
    
    bidNm = driver.find_element(By.ID, "bidNm")
    bidNm.clear()
    bidNm.send_keys(KEYWORD)
    bidNm.send_keys(Keys.RETURN)
    
    fromBidDt = driver.find_element(By.ID, "fromBidDt")
    fromBidDt.clear()
    fromBidDt.send_keys(S_DATE)
    fromBidDt.send_keys(Keys.RETURN)
    
    toBidDt = driver.find_element(By.ID, "toBidDt")
    toBidDt.clear()
    toBidDt.send_keys(E_DATE)
    toBidDt.send_keys(Keys.RETURN)
    
    recordCountPerPage = driver.find_element(By.ID, "recordCountPerPage")
    recordCountPerPage.send_keys("100")
    recordCountPerPage.send_keys(Keys.RETURN)
    
    search_btn = driver.find_element(By.CSS_SELECTOR, "#buttonwrap > div > a:nth-child(1)")
    search_btn.click()


    driver.find_element(By.CSS_SELECTOR, "#resultForm > div.results > table")
    
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    notices = soup.find_all("tr")
    
    df = pd.DataFrame(columns=[
    '업무',
    '공고번호-차수',
    '분류',
    '공고명',
    'URL주소',
    '공고기관',
    '수요기관',
    '계약방법',
    '입력일시',
    '공동수급',
    '투찰여부',
    ])
    
    raw_data = []
    for notice in tqdm(notices):
        temp_data = []
        for idx, td in enumerate(notice.find_all("td")):
            if idx == 3: # url 주소 추출
                link = td.find('a')['href']
                temp_data.append(link)
                
            temp_data.append(td.text.strip())
        raw_data.append(temp_data)
    
    raw_df = pd.DataFrame(raw_data, columns=[
    '업무',
    '공고번호-차수',
    '분류',
    '공고명',
    'URL주소',
    '공고기관',
    '수요기관',
    '계약방법',
    '입력일시',
    '공동수급',
    '투찰여부',
    ])
    
    df = pd.concat([df, raw_df], ignore_index=True)
    df = df.dropna(axis=0)
    
    
    #데이터 저장
    to_txt(df, f"{save_path}/{KEYWORD} 검색결과.txt")
    df.to_csv(f'{save_path}/{KEYWORD}.csv',index=True, encoding='utf-8')
    df.to_excel(f'{save_path}/{KEYWORD}.xlsx', index=True)



if __name__ == "__main__":
    if not os.path.exists('outputs'):
        os.makedirs('outputs')
        
    current_directory = os.getcwd()
    print("현재 디렉토리:", current_directory)
    
    # 정해진 출력문
    print("===========================================================")
    KEYWORD = input("1. 공고명으로 검색할 키워드는 무엇입니까?: ")
    S_DATE = input("2. 조회 시작일자 입력(예:2019/01/01): ")
    E_DATE = input("3. 조회 종료일자 입력(예:2019/03/31): ")
    save_path = input(f"파일로 저장할 폴더 이름을 쓰세요. (Defult: {current_directory}/outputs): ") or current_directory + "/outputs"
    

    if not os.path.exists(save_path):
        print("잘못된 경로입니다. 프로그램을 종료합니다.")
        sys.exit(1)
    
    # 크롤링 시작
    wait_thread = threading.Thread(target=wait_for_crawling)
    wait_thread.daemon = True  # 메인 스레드가 종료되는 경우 함께 종료되도록 설정
    wait_thread.start()
    
    # 크롤링 시작
    crawling(KEYWORD, S_DATE, E_DATE, save_path)