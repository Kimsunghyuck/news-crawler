"""
기존 데이터를 타임스탬프 포함 파일명으로 복사하는 스크립트
"""
import os
import shutil
from pathlib import Path

def convert_data_files():
    """
    data 폴더의 모든 news_{date}.json 파일을
    news_{date}_09-20.json, news_{date}_15-00.json, news_{date}_19-00.json 형식으로 복사
    """
    data_dir = Path('data')
    docs_data_dir = Path('docs/data')

    # 타임스탬프 리스트
    timestamps = ['09-20', '15-00', '19-00']

    # 모든 카테고리 폴더 탐색
    categories = ['politics', 'sports', 'economy', 'society', 'international', 'culture']
    sources = ['donga', 'chosun', 'joongang']

    converted_count = 0

    for category in categories:
        for source in sources:
            source_dir = data_dir / category / source
            docs_source_dir = docs_data_dir / category / source

            if not source_dir.exists():
                continue

            # 디렉토리 생성
            docs_source_dir.mkdir(parents=True, exist_ok=True)

            # news_*.json 파일 찾기
            for json_file in source_dir.glob('news_*.json'):
                # 파일명에서 날짜 추출
                filename = json_file.name

                # 이미 타임스탬프가 있는 파일은 건너뛰기
                if filename.count('_') > 1:
                    print(f"Skip (already has timestamp): {json_file}")
                    continue

                # news_2025-12-08.json -> 2025-12-08
                date_str = filename.replace('news_', '').replace('.json', '')

                # 각 타임스탬프별로 파일 복사
                for timestamp in timestamps:
                    new_filename = f"news_{date_str}_{timestamp}.json"

                    # data 폴더에 복사
                    dest_file = source_dir / new_filename
                    shutil.copy2(json_file, dest_file)
                    print(f"Copied: {json_file.name} -> {new_filename}")

                    # docs 폴더에도 복사
                    docs_dest_file = docs_source_dir / new_filename
                    shutil.copy2(json_file, docs_dest_file)

                    converted_count += 1

    print(f"\nConversion complete! Total {converted_count} files created")
    return converted_count

if __name__ == '__main__':
    print("=" * 60)
    print("Data file conversion started")
    print("=" * 60)
    convert_data_files()
