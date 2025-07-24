import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm
import re
from collections import defaultdict

# ✅ Mac 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

# 1. CSV 불러오기
df = pd.read_csv("train_data.csv")

# 2. 식사율 계산
df["중식_식사율"] = df["중식계"] / df["본사정원수"]
df["석식_식사율"] = df["석식계"] / df["본사정원수"]

# 3. 메뉴 분리 함수
def split_menus(menu_string):
    if pd.isna(menu_string):
        return []
    menu_string = re.sub(r"[^\uAC00-\uD7A3a-zA-Z0-9\s]", "", menu_string)
    return list(set(menu_string.strip().split()))

df["중식_메뉴리스트"] = df["중식메뉴"].apply(split_menus)
df["석식_메뉴리스트"] = df["석식메뉴"].apply(split_menus)

# 4. 메뉴별 식사율 수집
lunch_ratios = defaultdict(list)
dinner_ratios = defaultdict(list)

for _, row in df.iterrows():
    for menu in row["중식_메뉴리스트"]:
        lunch_ratios[menu].append(row["중식_식사율"])
    for menu in row["석식_메뉴리스트"]:
        dinner_ratios[menu].append(row["석식_식사율"])

# 5. 평균 식사율 계산 (5회 이상 등장한 메뉴만)
lunch_avg = {m: sum(v)/len(v) for m, v in lunch_ratios.items() if len(v) >= 5}
dinner_avg = {m: sum(v)/len(v) for m, v in dinner_ratios.items() if len(v) >= 5}

# 6. 상위 10개씩 추출
top_lunch = sorted(lunch_avg.items(), key=lambda x: x[1], reverse=True)[:10]
top_dinner = sorted(dinner_avg.items(), key=lambda x: x[1], reverse=True)[:10]

# 7. 시각화용 데이터 프레임 구성
plot_df = pd.DataFrame(top_lunch + top_dinner, columns=["메뉴", "식사율"])
plot_df["식사종류"] = ["중식"] * 10 + ["석식"] * 10

# 8. 시각화
plt.figure(figsize=(14, 10))
ax = sns.barplot(data=plot_df, x="식사율", y="메뉴", hue="식사종류", dodge=True, palette="Set2")

# Bar에 식사율 표시
for container in ax.containers:
    ax.bar_label(container, fmt='%.2f', label_type='edge', fontsize=10)

plt.title("중식 / 석식 식사율 TOP 10 메뉴", fontsize=14)
plt.xlabel("식사율")
plt.ylabel("메뉴")
plt.xlim(0, 1.05)
plt.legend(title="식사종류")
plt.tight_layout()
plt.show()