#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
대화형 어휘 학습 HTML 뷰어 생성기
지정된 폴더에서 word_table.json과 stories.json을 읽어 단일 HTML 파일을 생성합니다.
"""

import argparse
import json
import os
import sys
import re


def load_json_file(file_path):
    """JSON 파일을 로드하고 비표준 공백을 처리합니다."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # 비표준 공백(\u00a0)을 표준 공백으로 치환
            content = content.replace('\u00a0', ' ')
            return json.loads(content)
    except FileNotFoundError:
        print(f"오류: 파일을 찾을 수 없습니다: {file_path}")
        sys.exit(1)
    except PermissionError:
        print(f"오류: 파일 읽기 권한이 없습니다: {file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"오류: JSON 파싱 실패 ({file_path}): {e}")
        sys.exit(1)
    except Exception as e:
        print(f"오류: 파일 읽기 중 예상치 못한 오류 ({file_path}): {e}")
        sys.exit(1)


def process_word_tags(text, is_english=True):
    """문장 내의 <word> 태그를 처리하여 적절한 HTML 태그로 변환합니다."""
    if is_english:
        # 영어 문장: onclick 없이 data 속성만 사용
        pattern = r'<word\s+id=[\'"]([^\'"]+)[\'"]\s+class=[\'"]word-eng-link[\'"]>([^<]+)</word>'
        replacement = r'<span class="word-link" data-word-id="\1">\2</span>'
    else:
        # 한국어 문장: <word id='...' class='word-target-kr'>단어</word> -> <span class='word-target-kr'>단어</span>
        pattern = r'<word\s+id=[\'"]([^\'"]+)[\'"]\s+class=[\'"]word-target-kr[\'"]>([^<]+)</word>'
        replacement = r'<span class="word-target-kr">\2</span>'

    return re.sub(pattern, replacement, text)


def generate_word_data_js(words_data):
    """단어 데이터를 JavaScript 객체로 변환합니다."""
    # 중복 ID 처리: 마지막에 등장하는 항목을 사용
    word_dict = {}
    for word in words_data:
        word_dict[word['id']] = word

    # JavaScript 객체 생성
    js_lines = []
    for word_id, word_info in word_dict.items():
        # 특수문자 이스케이프 처리
        term = json.dumps(word_info['term'])
        kor_meaning = json.dumps(word_info['kor_meaning'])
        synonyms_text = json.dumps(", ".join(word_info.get('synonyms', [])))

        js_lines.append(f'        "{word_id}": {{')
        js_lines.append(f'            term: {term},')
        js_lines.append(f'            kor_meaning: {kor_meaning},')
        js_lines.append(f'            synonyms: {synonyms_text}')
        js_lines.append(f'        }},')

    return "{\n" + "\n".join(js_lines) + "\n        }"


def generate_chapters_html(stories_data):
    """챕터 데이터로부터 HTML을 생성합니다."""
    chapters_html = ""
    number_navigation = ""
    index_navigation = ""

    for idx, chapter in enumerate(stories_data):
        # chapter_num이 없거나 유효하지 않은 경우 인덱스 사용
        chapter_num = chapter.get('chapter_num')
        if chapter_num is None or not isinstance(chapter_num, int):
            chapter_num = idx
            print(f"경고: 챕터 '{chapter.get('chapter_title', f'Chapter {idx+1}')}'의 chapter_num이 유효하지 않아 인덱스 {idx}를 사용합니다.")

        chapter_title = chapter.get('chapter_title', f'Chapter {chapter_num + 1}')

        # 숫자 네비게이션 생성 (1, 2, 3, ...)
        active_class = "active" if idx == 0 else ""
        number_navigation += f'<a href="javascript:void(0)" class="chapter-link {active_class}" onclick="showChapter({idx})">{idx + 1}</a>'

        # 인덱스 네비게이션 생성 (1. Title, 2. Title, ...)
        index_navigation += f'                <div class="index-item" onclick="showChapter({idx})">\n'
        index_navigation += f'                    <span class="index-number">{idx + 1}.</span>\n'
        index_navigation += f'                    <span class="index-title">{chapter_title}</span>\n'
        index_navigation += f'                </div>\n'

        # 챕터 콘텐츠 생성
        visible_style = "" if idx == 0 else " style='display: none;'"
        chapters_html += f'''
        <div id="chapter-{idx}" class="chapter-content"{visible_style}>
            <h2>{chapter_title}</h2>
            <div class="story-content">'''

        # 문장 쌍들 처리
        for sentence_pair in chapter.get('story_sentences', []):
            english_sentence = process_word_tags(sentence_pair.get('english', ''), is_english=True)
            korean_sentence = process_word_tags(sentence_pair.get('korean', ''), is_english=False)

            chapters_html += f'''
                <div class="sentence-pair">
                    <p class="english-text">{english_sentence}</p>
                    <p class="korean-text" style="display: none;">{korean_sentence}</p>
                </div>'''

        chapters_html += '''
            </div>
        </div>'''

    return number_navigation.strip(), index_navigation.strip(), chapters_html


def generate_html(words_data, stories_data, output_filename):
    """완전한 HTML 문서를 생성합니다."""

    number_navigation, index_navigation, chapters_html = generate_chapters_html(stories_data)
    word_data_js = generate_word_data_js(words_data)

    html_template = f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>대화형 어휘 학습 뷰어</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
        }}

        .container {{
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
        }}

        .header {{
            background: white;
            padding: 10px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}

        .navigation {{
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 15px;
            margin-bottom: 0px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }}

        .nav-label {{
            font-weight: 600;
            color: #495057;
            font-size: 14px;
        }}

        .chapter-link {{
            display: inline-block;
            padding: 8px 12px;
            margin: 0 3px;
            text-decoration: none;
            color: #007bff;
            /* border: 1px solid #007bff; 제거 */
            /* border-radius: 50%; 제거 */
            border: none; /* 다른 테두리 제거 */
            border-bottom: 1px solid #007bff; /* 밑줄 추가 */
            font-weight: 500;
            font-size: 10px;
            transition: all 0.3s ease;
            min-width: 35px;
            text-align: center;
        }}

        .chapter-link:hover {{
            background: #007bff;
            color: white;
            border-bottom-color: white; /* hover 시 밑줄 색상 변경 */
            transform: scale(1.1);
        }}

        .chapter-link.active {{
            background: #007bff;
            color: white;
            border-bottom-color: white; /* active 시 밑줄 색상 변경 */
        }}

        .toggle-index-btn {{
            background: #6c757d;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-left: auto;
        }}

        .toggle-index-btn:hover {{
            background: #5a6268;
        }}

        .index-navigation {{
            display: none;
            margin-top: 15px;
            padding: 15px;
            background: white;
            border-radius: 8px;
            border: 1px solid #dee2e6;
        }}

        .index-navigation.show {{
            display: block;
        }}

        .index-item {{
            display: flex;
            align-items: center;
            padding: 8px 12px;
            margin-bottom: 5px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
        }}

        .index-item:hover {{
            background: #f8f9fa;
        }}

        .index-number {{
            font-weight: 600;
            color: #007bff;
            margin-right: 12px;
            min-width: 25px;
        }}

        .index-title {{
            color: #495057;
            font-size: 14px;
        }}

        .chapter-btn {{
            padding: 10px 20px;
            border: 2px solid #007bff;
            background: white;
            color: #007bff;
            border-radius: 25px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.3s ease;
        }}

        .chapter-btn:hover {{
            background: #007bff;
            color: white;
            transform: translateY(-2px);
        }}

        .chapter-btn.active {{
            background: #007bff;
            color: white;
        }}

        .controls {{
            text-align: center;
            margin-bottom: 20px;
        }}
        .translate-icon-btn {{
            background-color: transparent; /* 버튼 배경 투명하게 */
            border: none;                 /* 버튼 테두리 제거 */
            padding: 2px;                 /* 버튼 내부 여백 줄이기 (아이콘 주변 공간) */
            margin: 0;                    /* 버튼 외부 여백 제거 */
            cursor: pointer;              /* 마우스 오버 시 커서 변경 */
            display: inline-flex;         /* SVG 아이콘을 버튼 내에서 정렬하기 용이하도록 설정 */
            align-items: center;          /* 수직 중앙 정렬 */
            justify-content: center;      /* 수평 중앙 정렬 */
            line-height: 0;               /* 버튼 내부에 불필요한 추가 공간 제거 */
        }}

        .translate-icon-btn:hover {{
            background: transparent; /* Slightly lighter bronze on hover */
            transform: scale(1.1); /* Subtle scale instead of translateY */
            border-color: #a89b7a; /* Brighter brass on hover */
        }}

        .translate-icon-btn svg {{
            stroke: #e6d4a6; /* Aged gold for steampunk icon */
            width: 20px;
            height: 20px;
        }}


        .content {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        .chapter-content h2 {{
            color: #2c3e50;
            margin-bottom: 30px;
            text-align: center;
            font-size: 28px;
            border-bottom: 3px solid #007bff;
            padding-bottom: 10px;
        }}

        .sentence-pair {{
            margin-bottom: 25px;
        }}

        .english-text {{
            font-size: 18px;
            line-height: 1.8;
            margin-bottom: 10px;
            color: #2c3e50;
        }}

        .korean-text {{
            font-size: 16px;
            line-height: 1.7;
            color: #666;
            font-style: italic;
            background: #f8f9fa;
            padding: 10px 15px;
            border-left: 4px solid #007bff;
            border-radius: 0 5px 5px 0;
        }}

        /* 단어 링크 스타일 */
        .word-link {{
            color: #007bff;
            font-weight: 600;
            padding: 2px 4px;
            border-radius: 3px;
            background: rgba(0, 123, 255, 0.1);
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: underline;
        }}

        .word-link:hover {{
            background: rgba(0, 123, 255, 0.3);
            transform: scale(1.05);
        }}

        /* 한국어 대상 단어 스타일 */
        .word-target-kr {{
            color: #dc3545;
            font-weight: 600;
            padding: 2px 4px;
            border-radius: 3px;
            background: rgba(220, 53, 69, 0.1);
        }}

        /* 팝업 모달 스타일 */
        .popup-overlay {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 1000;
            animation: fadeIn 0.3s ease;
        }}

        .popup-overlay.show {{
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .popup-content {{
            background: white;
            max-width: 400px;
            width: 90%;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            animation: slideIn 0.3s ease;
            position: relative;
        }}

        .popup-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 25px 10px;
            border-bottom: 2px solid #f1f3f4;
        }}

        .popup-header h3 {{
            color: #007bff;
            font-size: 24px;
            margin: 0;
        }}

        .close-btn {{
            background: none;
            border: none;
            color: #999;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
            transition: color 0.3s ease;
            padding: 0;
            line-height: 1;
        }}

        .close-btn:hover {{
            color: #333;
        }}

        .popup-body {{
            padding: 20px 25px 25px;
        }}

        .popup-body p {{
            margin-bottom: 15px;
            font-size: 16px;
            line-height: 1.5;
        }}

        .popup-body p:last-child {{
            margin-bottom: 0;
        }}

        .popup-body strong {{
            color: #2c3e50;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}

        @keyframes slideIn {{
            from {{
                transform: translateY(-50px);
                opacity: 0;
            }}
            to {{
                transform: translateY(0);
                opacity: 1;
            }}
        }}

        /* 반응형 디자인 */
        @media (max-width: 768px) {{
            .chapter-link {{
                padding: 6px 8px;
                min-width: 25px; /* 모바일에서 더 작게 */
                font-size: 10px;
            }}
            .container {{
                padding: 10px;
            }}
            .content {{
                padding: 20px;
            }}
            .chapter-content h2 {{
                font-size: 24px;
            }}
            .english-text {{
                font-size: 16px;
            }}
            .korean-text {{
                font-size: 14px;
            }}
            .toggle-index-btn {{
                margin-left: 0;
                margin-top: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="content">
        <div class="header">
            <div class="navigation">
                <span class="nav-label">Chapters:</span>
                {number_navigation}
                <button class="toggle-index-btn" onclick="toggleIndex()">목차 보기</button>
                <button class="translate-icon-btn" onclick="toggleTranslation()" title="Toggle Translation">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10" stroke="lightskyblue"></circle> {{/* 하늘색 테두리 */}}
                        <path d="M2 12h20" stroke="dodgerblue"></path> {{/* 파란색 가로선 */}}
                        <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10" stroke="dodgerblue"></path> {{/* 파란색 세로 곡선 */}}
                        <path d="M12 2a15.3 15.3 0 0 0-4 10 15.3 15.3 0 0 0 4 10" stroke="dodgerblue"></path> {{/* 파란색 세로 곡선 */}}
                    </svg>
                </button>
            </div>

            <div id="indexNavigation" class="index-navigation">
                {index_navigation}
            </div>

            {chapters_html}
        </div>
    </div>

    <!-- 팝업 모달 -->
    <div id="wordPopupOverlay" class="popup-overlay">
        <div class="popup-content">
            <div class="popup-header">
                <h3 id="popupTerm">단어</h3>
                <button class="close-btn" onclick="closePopup()">&times;</button>
            </div>
            <div class="popup-body">
                <p id="popupMeaning"><strong>뜻:</strong> </p>
                <p id="popupSynonyms" style="display: none;"><strong>동의어:</strong> </p>
            </div>
        </div>
    </div>

    <script>
        // 단어 데이터
        const wordData = {word_data_js};

        let translationVisible = false;

        // 챕터 전환 함수
        function showChapter(chapterIndex) {{
            // 모든 챕터 숨기기
            const chapters = document.querySelectorAll('.chapter-content');
            chapters.forEach(chapter => {{
                chapter.style.display = 'none';
            }});

            // 모든 링크에서 active 클래스 제거
            const links = document.querySelectorAll('.chapter-link');
            links.forEach(link => {{
                link.classList.remove('active');
            }});

            // 선택된 챕터 보이기
            const selectedChapter = document.getElementById('chapter-' + chapterIndex);
            if (selectedChapter) {{
                selectedChapter.style.display = 'block';

                // 현재 번역 상태에 따라 한국어 문장 표시/숨김
                const koreanTexts = selectedChapter.querySelectorAll('.korean-text');
                koreanTexts.forEach(text => {{
                    text.style.display = translationVisible ? 'block' : 'none';
                }});
            }}

            // 선택된 링크에 active 클래스 추가
            if (links[chapterIndex]) {{
                links[chapterIndex].classList.add('active');
            }}

            // 목차가 열려있으면 닫기
            const indexNav = document.getElementById('indexNavigation');
            if (indexNav && indexNav.classList.contains('show')) {{
                toggleIndex();
            }}
        }}

        // 목차 토글 함수
        function toggleIndex() {{
            const indexNav = document.getElementById('indexNavigation');
            const toggleBtn = document.querySelector('.toggle-index-btn');

            if (indexNav.classList.contains('show')) {{
                indexNav.classList.remove('show');
                toggleBtn.textContent = '목차 보기';
            }} else {{
                indexNav.classList.add('show');
                toggleBtn.textContent = '목차 숨기기';
            }}
        }}

        // 번역 토글 함수

        function toggleTranslation() {{
            translationVisible = !translationVisible;
            const koreanTexts = document.querySelectorAll('.korean-text');

            koreanTexts.forEach(text => {{
                text.style.display = translationVisible ? 'block' : 'none';
            }});

            const toggleBtn = document.querySelector('.translate-icon-btn');
            toggleBtn.setAttribute('title', translationVisible ? 'Hide Translation' : 'Show Translation');
        }}

        // 단어 팝업 표시 함수
        function showWordPopup(wordId) {{
            console.log('단어 팝업 표시:', wordId);

            const wordInfo = wordData[wordId];
            if (!wordInfo) {{
                console.error('단어 정보를 찾을 수 없습니다:', wordId);
                alert('단어 정보를 찾을 수 없습니다: ' + wordId);
                return;
            }}

            // 팝업 요소들 가져오기
            const overlay = document.getElementById('wordPopupOverlay');
            const termElement = document.getElementById('popupTerm');
            const meaningElement = document.getElementById('popupMeaning');
            const synonymsElement = document.getElementById('popupSynonyms');

            if (!overlay || !termElement || !meaningElement || !synonymsElement) {{
                console.error('팝업 요소를 찾을 수 없습니다');
                return;
            }}

            // 팝업 내용 설정
            termElement.textContent = wordInfo.term;
            meaningElement.innerHTML = '<strong>뜻:</strong> ' + wordInfo.kor_meaning;

            if (wordInfo.synonyms && wordInfo.synonyms.trim()) {{
                synonymsElement.innerHTML = '<strong>동의어:</strong> ' + wordInfo.synonyms;
                synonymsElement.style.display = 'block';
            }} else {{
                synonymsElement.style.display = 'none';
            }}

            // 팝업 표시
            overlay.classList.add('show');
            document.body.style.overflow = 'hidden';

            console.log('팝업 표시 완료');
        }}

        // 팝업 닫기 함수
        function closePopup() {{
            const overlay = document.getElementById('wordPopupOverlay');
            if (overlay) {{
                overlay.classList.remove('show');
                document.body.style.overflow = 'auto';
            }}
        }}

        // 페이지 로드 시 초기화
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('페이지 로드됨');
            console.log('단어 데이터 개수:', Object.keys(wordData).length);

            // 첫 번째 챕터 표시
            showChapter(0);

            // 단어 클릭 이벤트 리스너 (이벤트 위임)
            document.body.addEventListener('click', function(e) {{
                if (e.target.classList.contains('word-link')) {{
                    const wordId = e.target.getAttribute('data-word-id');
                    if (wordId) {{
                        console.log('단어 클릭됨:', wordId);
                        e.preventDefault();
                        e.stopPropagation();
                        showWordPopup(wordId);
                    }}
                }}
            }});

            // 팝업 오버레이 클릭 시 닫기
            document.getElementById('wordPopupOverlay').addEventListener('click', function(e) {{
                if (e.target === this) {{
                    closePopup();
                }}
            }});

            // ESC 키로 팝업 닫기
            document.addEventListener('keydown', function(e) {{
                if (e.key === 'Escape') {{
                    closePopup();
                }}
            }});

            console.log('이벤트 리스너 설정 완료');

            // 단어 요소 개수 확인
            setTimeout(function() {{
                const wordElements = document.querySelectorAll('.word-link');
                console.log('발견된 단어 요소 수:', wordElements.length);
                if (wordElements.length > 0) {{
                    console.log('첫 번째 단어 요소:', wordElements[0].textContent, wordElements[0].getAttribute('data-word-id'));
                }}
            }}, 500);
        }});
    </script>
</body>
</html>'''

    return html_template


def main():
    # 명령줄 인자 처리
    parser = argparse.ArgumentParser(
        description='대화형 어휘 학습 HTML 뷰어를 생성합니다.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
예시 사용법:
  python story_viewer_generator.py ./word_table ./stories output_story.html
  python story_viewer_generator.py /path/to/word_table /path/to/stories my_story.html
        '''
    )

    parser.add_argument('word_table_folder',
                       help='word_table.json 파일이 위치한 폴더 경로')
    parser.add_argument('stories_folder',
                       help='stories.json 파일이 위치한 폴더 경로')
    parser.add_argument('output_html',
                       help='생성될 HTML 파일명 (예: output_story.html)')

    args = parser.parse_args()

    # 입력 파일 경로 구성
    word_table_path = os.path.join(args.word_table_folder, 'word_table.json')
    stories_path = os.path.join(args.stories_folder, 'stories.json')

    print(f"단어 테이블 파일 로딩: {word_table_path}")
    print(f"스토리 파일 로딩: {stories_path}")

    # JSON 파일들 로드
    word_table_data = load_json_file(word_table_path)
    stories_data = load_json_file(stories_path)

    # 데이터 구조 검증
    if 'words' not in word_table_data:
        print("오류: word_table.json에 'words' 키가 없습니다.")
        sys.exit(1)

    if 'stories' not in stories_data:
        print("오류: stories.json에 'stories' 키가 없습니다.")
        sys.exit(1)

    words = word_table_data['words']
    stories = stories_data['stories']

    print(f"로드된 단어 수: {len(words)}")
    print(f"로드된 챕터 수: {len(stories)}")

    # HTML 생성
    print("HTML 파일 생성 중...")
    html_content = generate_html(words, stories, args.output_html)
    
     # 출력 파일의 디렉토리 경로를 가져옵니다.
    output_dir = os.path.dirname(args.output_html)

    # 디렉토리 경로가 존재하고, 현재 디렉토리가 아닌 경우
    if output_dir:
        try:
            # 재귀적으로 폴더를 생성합니다. exist_ok=True는 폴더가 이미 있어도 오류를 발생시키지 않습니다.
            os.makedirs(output_dir, exist_ok=True)
            print(f"출력 폴더 확인/생성 완료: {output_dir}")
        except OSError as e:
            # 폴더 생성 중 오류 발생 시 프로그램 종료
            print(f"오류: 출력 폴더를 생성하는 데 실패했습니다: {e}")
            sys.exit(1)

    # HTML 파일 저장
    try:
        with open(args.output_html, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ HTML 파일이 성공적으로 생성되었습니다: {args.output_html}")
        print(f"파일 크기: {os.path.getsize(args.output_html)} bytes")
    except Exception as e:
        print(f"오류: HTML 파일 저장 실패: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
