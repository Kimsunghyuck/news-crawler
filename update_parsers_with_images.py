"""
parser.py 파일의 모든 파서 함수에 image_url 필드를 추가하는 스크립트
"""

import re

# parser.py 파일 읽기
with open('parser.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 각 함수에서 image_url 추출 코드 추가할 위치 찾기 및 수정
patterns_to_add_image_extraction = [
    # 동아일보 스포츠
    (r"(def parse_donga_sports.*?if not title or len\(title\) < 10:\s+continue\s+)",
     r"\1\n                # 이미지 URL 추출\n                image_url = extract_image_url(link, \"https://www.donga.com\")\n                "),
    # 조선일보 스포츠
    (r"(def parse_chosun_sports.*?if not title or len\(title\) < 10:\s+continue\s+)",
     r"\1\n            # 이미지 URL 추출\n            image_url = extract_image_url(link, \"https://www.chosun.com\")\n            "),
    # 중앙일보 스포츠 - 순위 기사
    (r"(def parse_joongang_sports.*?if title and len\(title\) >= 10 and not title\.isdigit\(\):\s+)",
     r"\1# 이미지 URL 추출\n                                        image_url = extract_image_url(link, \"https://www.joongang.co.kr\")\n                                        "),
    # 중앙일보 스포츠 - 보충 기사
    (r"(# 5개가 안 되면 일반 스포츠 기사로 보충.*?if not title or len\(title\) < 10 or title\.isdigit\(\):\s+continue\s+)",
     r"\1\n            # 이미지 URL 추출\n            image_url = extract_image_url(link, \"https://www.joongang.co.kr\")\n            "),
    # 동아일보 경제
    (r"(def parse_donga_economy.*?if not title or len\(title\) < 10:\s+continue\s+)",
     r"\1\n                # 이미지 URL 추출\n                image_url = extract_image_url(link, \"https://www.donga.com\")\n                "),
    # 조선일보 경제
    (r"(def parse_chosun_economy.*?if not title or len\(title\) < 10:\s+continue\s+)",
     r"\1\n            # 이미지 URL 추출\n            image_url = extract_image_url(link, \"https://www.chosun.com\")\n            "),
    # 중앙일보 경제 - 순위 기사
    (r"(def parse_joongang_economy.*?if title and len\(title\) >= 10 and not title\.isdigit\(\):\s+)",
     r"\1# 이미지 URL 추출\n                                        image_url = extract_image_url(link, \"https://www.joongang.co.kr\")\n                                        "),
    # 중앙일보 경제 - 보충 기사
    (r"(# 5개가 안 되면 일반 경제 기사로 보충.*?if not title or len\(title\) < 10 or title\.isdigit\(\):\s+continue\s+)",
     r"\1\n            # 이미지 URL 추출\n            image_url = extract_image_url(link, \"https://www.joongang.co.kr\")\n            "),
]

# news_item 딕셔너리에 image_url 필드 추가
patterns_to_add_field = [
    # 기존에 image_url이 없는 모든 news_item에 추가
    (r"(news_item = \{[^}]*'source': '동아일보',\s+)('scraped_at')",
     r"\1'image_url': image_url,\n                    \2"),
    (r"(news_item = \{[^}]*'source': '조선일보',\s+)('scraped_at')",
     r"\1'image_url': image_url,\n            \2"),
    (r"(news_item = \{[^}]*'source': '중앙일보',\s+)('scraped_at')",
     r"\1'image_url': image_url,\n                                    \2"),
    # 보충 기사용
    (r"(# 5개가 안 되면.*?news_item = \{[^}]*'source': '중앙일보',\s+)('scraped_at')",
     r"\1'image_url': image_url,\n            \2"),
]

print("파서 파일 업데이트 중...")
print("=" * 60)

# 백업 생성
with open('parser_backup.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ 백업 파일 생성: parser_backup.py")

# 수정 적용
modified = False
for pattern, replacement in patterns_to_add_image_extraction + patterns_to_add_field:
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        modified = True
        print(f"✓ 패턴 적용 완료")

if modified:
    # 수정된 내용 저장
    with open('parser.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("=" * 60)
    print("✓ parser.py 파일 업데이트 완료!")
    print("\n이제 크롤러를 실행하면 이미지 URL도 함께 수집됩니다.")
else:
    print("⚠ 수정할 패턴을 찾지 못했습니다. 이미 수정되었거나 파일 구조가 변경되었을 수 있습니다.")
