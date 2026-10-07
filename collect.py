import csv
import time
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

def make_session():                          # 재시도·헤더를 붙인 세션
    session = requests.Session()
    retry = Retry(total=5, backoff_factor=1, # 크롤링을 5번 실행하겠다
                  status_forcelist=[429, 500, 502, 503, 504],
                  allowed_methods=["GET"])
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.headers.update({"User-Agent": "Mozilla/5.0 (study-crawler)"})
    return session

session = make_session()
packages = ["requests", "beautifulsoup4", "psycopg", "lxml", "flask"]  # 수집 대상
collected = []                                # 결과를 담을 리스트

for pkg in packages:                          # 대상을 하나씩 순회
    url = f"https://pypi.org/project/{pkg}/"
    resp = session.get(url, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    # 쉼표로 두 선택자를 나열 — 새 구조·옛 구조 어느 쪽이 와도 찾는다(교재 05 §2.3)
    name = soup.select_one("h1.project-header__name, h1.package-header__name")
    desc = soup.select_one("p.project-header__summary, p.package-description__summary")
    collected.append({
        "name": name.get_text(strip=True) if name else "",        # None 대비
        "summary": desc.get_text(strip=True) if desc else "",
        "url": url,
    })
    time.sleep(1)                             # 예의: 요청 사이 1초 쉬기

with open("packages.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "summary", "url"])
    writer.writeheader()
    writer.writerows(collected)

print(len(collected), "건 수집 완료")