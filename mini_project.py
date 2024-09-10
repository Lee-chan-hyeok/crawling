# 1~10 페이지 크롤링 (성공)

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time
import pymysql

# 크롬 웹드라이버 설치 경로
driver_path = ChromeDriverManager().install()
service = Service(executable_path=driver_path)
browser = webdriver.Chrome(service=service)
browser.get("https://www.jobkorea.co.kr/recruit/joblist?menucode=duty")

# 포털 사이트에서 조건 클릭
click_btn1 = browser.find_element(By.CSS_SELECTOR, "#devSearchForm > div.detailArea > div > div:nth-child(1) > dl.job.circleType.dev-tab.dev-duty.on > dd.ly_sub > div.ly_sub_cnt.colm3-ty1.clear > dl:nth-child(1) > dd > div.nano-content.dev-main > ul > li:nth-child(6) > label")
click_btn1.click()
click_btn2 = browser.find_element(By.CSS_SELECTOR, "#duty_step2_10031_ly > li:nth-child(9) > label > span")
click_btn2.click()
click_btn3 = browser.find_element(By.CSS_SELECTOR, "#dev-btn-search > span")
click_btn3.click()

time.sleep(1)

all_data = []

# 기업명 조회
cor_names = browser.find_elements(By.CSS_SELECTOR, "#dev-gi-list > div > div.tplList.tplJobList > table > tbody > tr > td.tplCo > a")
cor_name = [name.text for name in cor_names]

# 모집 내용 조회
recruitment_contents = browser.find_elements(By.CSS_SELECTOR, "#dev-gi-list > div > div.tplList.tplJobList > table > tbody > tr > td.tplTit > div > strong > a")
recruitment_content = [content.text for content in recruitment_contents]

# 채용 조건 조회
conditions = browser.find_elements(By.CSS_SELECTOR, "#dev-gi-list > div > div.tplList.tplJobList > table > tbody > tr > td.tplTit > div > p.etc")
condition = [con.text for con in conditions]

print(len(cor_names))

# 데이터 저장
for i in range(len(cor_names)):
    all_data.append([cor_name[i], recruitment_content[i], condition[i]])

for page in range(2, 11):
    # 다음 페이지로 이동
    next_page_btn = browser.find_element(By.CSS_SELECTOR, "#dvGIPaging > div > ul > li:nth-child({}) > a".format(page))
    next_page_btn.click()
    # ActionChains(browser).move_to_element(next_page_btn).click(next_page_btn).perform()
    time.sleep(2)  # 페이지 로딩을 기다립니다.
    
    # 기업명 조회
    cor_names = browser.find_elements(By.CSS_SELECTOR, "#dev-gi-list > div > div.tplList.tplJobList > table > tbody > tr > td.tplCo > a")
    cor_name = [name.text for name in cor_names]

    # 모집 내용 조회
    recruitment_contents = browser.find_elements(By.CSS_SELECTOR, "#dev-gi-list > div > div.tplList.tplJobList > table > tbody > tr > td.tplTit > div > strong > a")
    recruitment_content = [content.text for content in recruitment_contents]

    # 채용 조건 조회
    conditions = browser.find_elements(By.CSS_SELECTOR, "#dev-gi-list > div > div.tplList.tplJobList > table > tbody > tr > td.tplTit > div > p.etc")
    condition = [con.text for con in conditions]

    # 데이터 저장
    for i in range(len(cor_names)):
        all_data.append([cor_name[i], recruitment_content[i], condition[i]])
    
    time.sleep(1)

# DataFrame 생성
df = pd.DataFrame(all_data, columns=["기업명", "모집내용", "조건"])

# CSV 파일로 저장
df.to_csv("job.csv", index=False)

browser.close()

# =================== MySQL로 저장 ===================

# CSV 파일 읽기
df = pd.read_csv('job.csv')

# 테이블 생성
create_table_query = """
CREATE TABLE IF NOT EXISTS job_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(255),
    recruitment_content VARCHAR(255),
    conditions VARCHAR(255)
)
"""

# MySQL 연결 설정
conn = pymysql.connect(
    host="127.0.0.1",
    port=3306,
    user="playdata",
    password="1111",
    database="mydb"
)

# 데이터프레임을 MySQL 테이블로 저장
try:
    cursor = conn.cursor()
    
    cursor.execute(create_table_query)

    # 데이터 삽입
    for index, row in df.iterrows():
        cursor.execute(
            "INSERT INTO job_data (company_name, recruitment_content, conditions) VALUES (%s, %s, %s)",
            (row['기업명'], row['모집내용'], row['조건'])
        )

    # 변경사항 커밋
    conn.commit()
    print("Data inserted successfully")

except Exception as e:
    print(f"Error: {e}")

finally:
    # 연결 닫기
    cursor.close()
    conn.close()