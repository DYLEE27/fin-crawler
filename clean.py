import re
import pandas as pd
from bs4 import BeautifulSoup

INPUT = "packages.csv"

df = pd.read_csv(INPUT)

print("[0] 읽은 데이터:", len(df), "건")
print(df[["name", "url"]])

df = df.drop_duplicates(subset=["url"])

print("\n[1] 중복 제거 후:", len(df), "건")

# 빈 값 처리 
print("\n[2] 비어 있는 칸이 있는 줄")
print(df[df["summary"].isna()][["name", "summary"]])

df["name"] = df["name"].fillna("")
df["summary"] = df["summary"].fillna("")

print("    채운 뒤 비어 있는 칸 수:", df["summary"].isna().sum())

# 2-3 HTML 태그 + 공백정리
def clean_text(raw):
    text = BeautifulSoup(raw, "lxml").get_text(" ", strip=True)
    text = re.sub(r"\s+", " ", text) # \s+ : 공백이 1개 이상 반복되는 패턴이 발견되면 공백 하나로 바꾸어라
    return text.strip()


print("\n[3] 정리 전")
print(df[["name", "summary"]].head(2))

df["name"] = df["name"].apply(clean_text)
df["summary"] = df["summary"].apply(clean_text)

print("    정리 후")
print(df[["name", "summary"]].head(2))

df.to_csv("packages_clean.csv", index=False, encoding="utf-8")

print("\n저장:", len(df), "건 → packages_clean.csv")