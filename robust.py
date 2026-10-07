import logging, time
import urllib.robotparser as rp
import requests
from bs4 import BeautifulSoup

logging.basicConfig(                     # 로그를 파일과 콘솔에 동시에
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("crawler.log", encoding="utf-8"),
              logging.StreamHandler()])
log = logging.getLogger(__name__)

robots = rp.RobotFileParser()            # robots.txt 확인 도구
robots.set_url("https://pypi.org/robots.txt")
robots.read()

def make_session():
    s = requests.Session()
    s.headers.update({"User-Agent": "Mozilla/5.0 (study-crawler)"})
    return s

def fetch(url, session, retries=3):      # 실패해도 죽지 않는 수집
    for i in range(retries):
        try:
            resp = session.get(url, timeout=10)
            resp.raise_for_status()
            return resp
        except requests.exceptions.Timeout:
            log.warning("타임아웃 재시도 %d/%d: %s", i + 1, retries, url)
        except requests.exceptions.HTTPError as e:
            log.error("HTTP 오류 %s: %s", e.response.status_code, url)
            if e.response.status_code < 500:   # 404 등은 재시도해도 소용없음
                break
        except requests.exceptions.ConnectionError:
            log.warning("연결 오류 재시도 %d/%d: %s", i + 1, retries, url)
        time.sleep(2 ** i)               # 지수 백오프 1→2→4초
    return None                          # 끝내 실패하면 None

session = make_session()
targets = [
    "https://pypi.org/project/requests/",       # 정상
    "https://pypi.org/no-such-page-xyz-123/",   # 일부러 404
    "https://pypi.org/simple/requests/",        # robots.txt가 막는 경로 (Disallow: /simple/)
]
for url in targets:
    if not robots.can_fetch("*", url):
        log.warning("robots.txt 불허 — 건너뜀: %s", url)
        continue                          # 이 주소는 건너뛰고 다음으로
    resp = fetch(url, session)
    if resp is None:                    # 세 번 시도해도 못 받았을 때
        log.error("수집 실패(건너뜀): %s", url)
        continue
    soup = BeautifulSoup(resp.text, "lxml")
    name = soup.select_one("h1.project-header__name, h1.package-header__name")
    log.info("수집 성공: %s", name.get_text(strip=True) if name else "(이름 없음)")
    time.sleep(1)

print("완료. crawler.log를 확인하세요.")