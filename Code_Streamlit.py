# 필요한 라이브러리
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

import time

# 잡코리아 크롤링 함수
def get_jobkorea_data():
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 10)

    driver.get('https://www.jobkorea.co.kr/')
    try:
        popup_close_btn = wait.until(EC.element_to_be_clickable((By.ID, 'layerSystemCheck')))
        popup_close_btn.click()
    except:
        pass

    search_box = wait.until(EC.presence_of_element_located((By.ID, 'stext')))
    search_box.send_keys("데이터분석")

    search_button = wait.until(EC.element_to_be_clickable((By.ID, 'common_search_btn')))
    search_button.click()

    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    target_section = soup.select_one('section.content-recruit.on')
    job_cards = target_section.select('article.list-item')

    result_list = []
    for job in job_cards:
        try:
            site = "Job_Korea"
            company_tag = job.select_one('.list-section-corp a[target]')
            company = company_tag.text.strip() if company_tag else None

            title_tag = job.select_one('.list-section-information .information-title a')
            title = title_tag.text.strip() if title_tag else None

            detail_tags = job.select('.chip-information-group li')
            details = ' / '.join([li.text.strip() for li in detail_tags]) if detail_tags else None

            url_tail = job.get('data-gavirturl')
            full_url = f"https:{url_tail}" if url_tail else None

            result_list.append({
                'Site': site,
                'Col_Company': company,
                'Col_Recruit': title,
                'Col_detail': details,
                'Col_url': full_url
            })
        except:
            continue

    driver.quit()
    return pd.DataFrame(result_list)

# 사람인 크롤링 함수
def get_saramin_data():
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 10)

    driver.get('https://www.saramin.co.kr/')

    search_btn = wait.until(EC.element_to_be_clickable((By.ID, 'btn_search')))
    search_btn.click()

    search_input = wait.until(EC.presence_of_element_located((By.ID, 'ipt_keyword_recruit')))
    search_input.send_keys("데이터분석")

    submit_btn = wait.until(EC.element_to_be_clickable((By.ID, 'btn_search_recruit')))
    submit_btn.click()

    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    job_section = soup.select_one('section.section_search#recruit_info')
    job_list = job_section.select('div#recruit_info_list > div.content > div.item_recruit')

    result_list = []
    for job in job_list:
        try:
            site = "Saramin"
            company_tag = job.select_one('div.area_corp strong.corp_name a')
            company = company_tag.text.strip() if company_tag else None

            title_tag = job.select_one('h2.job_tit a')
            title = title_tag.get('title').strip() if title_tag else None

            keyword_tags = job.select('div.job_condition span')
            details = ' / '.join([span.get_text(strip=True) for span in keyword_tags]) if keyword_tags else None

            url_tail = title_tag.get('href') if title_tag else None
            full_url = f"https://www.saramin.co.kr{url_tail}" if url_tail else None

            result_list.append({
                'Site': site,
                'Col_Company': company,
                'Col_Recruit': title,
                'Col_detail': details,
                'Col_url': full_url
            })
        except:
            continue

    driver.quit()
    return pd.DataFrame(result_list)

# Streamlit 앱 시작
st.set_page_config(layout="centered")
st.title("Title")

# 버튼 클릭 시 크롤링 실행
if st.button("Recruit Searching"):
    jobkorea_df = get_jobkorea_data()
    saramin_df = get_saramin_data()

    merged_df = pd.concat([jobkorea_df, saramin_df], ignore_index=True)

    with st.container():
        st.dataframe(merged_df)

        site_ratio = merged_df['Site'].value_counts().reset_index()
        site_ratio.columns = ['Site', 'Count']
        site_ratio['Ratio'] = round(site_ratio['Count'] / site_ratio['Count'].sum() * 100, 2)

        st.dataframe(site_ratio)

        # 파이차트
        fig, ax = plt.subplots(figsize=(6, 4))
        colors = ['royalblue', 'lightskyblue']
        wedges, texts, autotexts = ax.pie(
            site_ratio['Ratio'],
            labels=None,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            textprops=dict(color="white")
        )

        # 범례는 항목명만, 박스 없애기
        ax.legend(
            site_ratio['Site'],
            loc='center left',
            bbox_to_anchor=(1, 0.5),
            frameon=False
        )

        ax.set_title("Recruitment Ratio")
        st.pyplot(fig)


# 실행코드 ; streamlit run Code_streamlit.py