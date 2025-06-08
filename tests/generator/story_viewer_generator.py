#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSS 전용 대화형 어휘 학습 HTML 뷰어 생성기
JavaScript 없이 CSS만으로 작동하는 단일 HTML 파일을 생성합니다.
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


def process_word_tags(text, words_data, is_english=True):
    """문장 내의 <word> 태그를 처리하여 적절한 HTML 태그로 변환합니다."""
    if is_english:
        # 영어 문장: 단어 정보를 포함한 hover 요소로 변환
        def replace_word(match):
            word_id = match.group(1)
            word_text = match.group(2)

            # word_id로 단어 정보 찾기
            word_info = None
            for word in words_data:
                if word['id'] == word_id:
                    word_info = word
                    break

            if word_info:
                meaning = word_info.get('kor_meaning', '')
                synonyms = word_info.get('synonyms', [])
                synonyms_text = f"동의어: {', '.join(synonyms)}" if synonyms else ""

                return f'''<span class="word-link">{word_text}
                    <span class="word-tooltip">
                        <strong>{word_info['term']}</strong><br>
                        뜻: {meaning}
                        {f"<br>{synonyms_text}" if synonyms_text else ""}
                    </span>
                </span>'''
            else:
                return word_text

        pattern = r'<word\s+id=[\'"]([^\'"]+)[\'"]\s+class=[\'"]word-eng-link[\'"]>([^<]+)</word>'
        return re.sub(pattern, replace_word, text)
    else:
        # 한국어 문장: <word id='...' class='word-target-kr'>단어</word> -> <span class='word-target-kr'>단어</span>
        pattern = r'<word\s+id=[\'"]([^\'"]+)[\'"]\s+class=[\'"]word-target-kr[\'"]>([^<]+)</word>'
        replacement = r'<span class="word-target-kr">\2</span>'
        return re.sub(pattern, replacement, text)


def generate_chapters_html(stories_data, words_data):
    """챕터 데이터로부터 HTML을 생성합니다."""
    chapters_html = ""
    navigation_html = ""

    # 번역 토글을 위한 체크박스
    translation_checkbox = '<input type="checkbox" id="translation-toggle" class="translation-toggle">'

    # 목차 토글을 위한 체크박스
    index_checkbox = '<input type="checkbox" id="index-toggle" class="index-toggle">'

    # 각 챕터를 위한 라디오 버튼 생성
    chapter_radios = ""
    for idx, _ in enumerate(stories_data):
        checked = 'checked' if idx == 0 else ''
        chapter_radios += f'<input type="radio" name="chapter" id="chapter-radio-{idx}" class="chapter-radio" {checked}>\n'

    # 네비게이션 생성
    navigation_html += '<div class="navigation">'
    navigation_html += '<span class="nav-label">Chapters:</span>'
    navigation_html += '<div class="chapter-links">'

    for idx, chapter in enumerate(stories_data):
        navigation_html += f'<label for="chapter-radio-{idx}" class="chapter-link">{idx + 1}</label>'

    navigation_html += '</div>'
    navigation_html += '<label for="index-toggle" class="toggle-index-btn">목차 보기</label>'
    navigation_html += '<label for="translation-toggle" class="translate-icon-btn" title="Toggle Translation">'
    navigation_html += '''
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10" stroke="lightskyblue"></circle>
            <path d="M2 12h20" stroke="dodgerblue"></path>
            <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10" stroke="dodgerblue"></path>
            <path d="M12 2a15.3 15.3 0 0 0-4 10 15.3 15.3 0 0 0 4 10" stroke="dodgerblue"></path>
        </svg>
    '''
    navigation_html += '</label>'
    navigation_html += '</div>'

    # 목차 생성
    index_html = '<div class="index-navigation">'
    for idx, chapter in enumerate(stories_data):
        chapter_title = chapter.get('chapter_title', f'Chapter {idx + 1}')
        index_html += f'''
            <label for="chapter-radio-{idx}" class="index-item">
                <span class="index-number">{idx + 1}.</span>
                <span class="index-title">{chapter_title}</span>
            </label>
        '''
    index_html += '</div>'

    # 챕터 콘텐츠 생성
    for idx, chapter in enumerate(stories_data):
        chapter_title = chapter.get('chapter_title', f'Chapter {idx + 1}')

        chapters_html += f'''
        <div class="chapter-content chapter-{idx}">
            <h2>{chapter_title}</h2>
            <div class="story-content">'''

        # 문장 쌍들 처리
        for sentence_pair in chapter.get('story_sentences', []):
            english_sentence = process_word_tags(sentence_pair.get('english', ''), words_data, is_english=True)
            korean_sentence = process_word_tags(sentence_pair.get('korean', ''), words_data, is_english=False)

            chapters_html += f'''
                <div class="sentence-pair">
                    <p class="english-text">{english_sentence}</p>
                    <p class="korean-text">{korean_sentence}</p>
                </div>'''

        chapters_html += '''
            </div>
        </div>'''

    return translation_checkbox, index_checkbox, chapter_radios, navigation_html, index_html, chapters_html


def generate_html(words_data, stories_data, output_filename):
    """완전한 HTML 문서를 생성합니다."""

    translation_checkbox, index_checkbox, chapter_radios, navigation_html, index_html, chapters_html = generate_chapters_html(stories_data, words_data)

    html_template = f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>대화형 어휘 학습 뷰어 (CSS Only)</title>
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

        /* 체크박스와 라디오 버튼 숨기기 */
        .translation-toggle,
        .index-toggle,
        .chapter-radio {{
            display: none;
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

        .chapter-links {{
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
        }}

        .chapter-link {{
            display: inline-block;
            padding: 8px 12px;
            text-decoration: none;
            color: #007bff;
            border: none;
            border-bottom: 1px solid #007bff;
            font-weight: 500;
            font-size: 10px;
            transition: all 0.3s ease;
            min-width: 35px;
            text-align: center;
            cursor: pointer;
        }}

        .chapter-link:hover {{
            background: #007bff;
            color: white;
            border-bottom-color: white;
            transform: scale(1.1);
        }}

        /* 모든 챕터 숨기기 */
        .chapter-content {{
            display: none;
        }}

        /* 라디오 버튼 기반 챕터 표시 */
        .chapter-radio:nth-of-type(1):checked ~ .content .chapter-0,
        .chapter-radio:nth-of-type(2):checked ~ .content .chapter-1,
        .chapter-radio:nth-of-type(3):checked ~ .content .chapter-2,
        .chapter-radio:nth-of-type(4):checked ~ .content .chapter-3,
        .chapter-radio:nth-of-type(5):checked ~ .content .chapter-4,
        .chapter-radio:nth-of-type(6):checked ~ .content .chapter-5,
        .chapter-radio:nth-of-type(7):checked ~ .content .chapter-6,
        .chapter-radio:nth-of-type(8):checked ~ .content .chapter-7,
        .chapter-radio:nth-of-type(9):checked ~ .content .chapter-8,
        .chapter-radio:nth-of-type(10):checked ~ .content .chapter-9,
        .chapter-radio:nth-of-type(11):checked ~ .content .chapter-10,
        .chapter-radio:nth-of-type(12):checked ~ .content .chapter-11,
        .chapter-radio:nth-of-type(13):checked ~ .content .chapter-12,
        .chapter-radio:nth-of-type(14):checked ~ .content .chapter-13,
        .chapter-radio:nth-of-type(15):checked ~ .content .chapter-14,
        .chapter-radio:nth-of-type(16):checked ~ .content .chapter-15,
        .chapter-radio:nth-of-type(17):checked ~ .content .chapter-16,
        .chapter-radio:nth-of-type(18):checked ~ .content .chapter-17,
        .chapter-radio:nth-of-type(19):checked ~ .content .chapter-18,
        .chapter-radio:nth-of-type(20):checked ~ .content .chapter-19 {{
            display: block;
        }}

        /* 활성 챕터 링크 스타일 */
        .chapter-radio:nth-of-type(1):checked ~ .header .chapter-links .chapter-link:nth-child(1),
        .chapter-radio:nth-of-type(2):checked ~ .header .chapter-links .chapter-link:nth-child(2),
        .chapter-radio:nth-of-type(3):checked ~ .header .chapter-links .chapter-link:nth-child(3),
        .chapter-radio:nth-of-type(4):checked ~ .header .chapter-links .chapter-link:nth-child(4),
        .chapter-radio:nth-of-type(5):checked ~ .header .chapter-links .chapter-link:nth-child(5),
        .chapter-radio:nth-of-type(6):checked ~ .header .chapter-links .chapter-link:nth-child(6),
        .chapter-radio:nth-of-type(7):checked ~ .header .chapter-links .chapter-link:nth-child(7),
        .chapter-radio:nth-of-type(8):checked ~ .header .chapter-links .chapter-link:nth-child(8),
        .chapter-radio:nth-of-type(9):checked ~ .header .chapter-links .chapter-link:nth-child(9),
        .chapter-radio:nth-of-type(10):checked ~ .header .chapter-links .chapter-link:nth-child(10),
        .chapter-radio:nth-of-type(11):checked ~ .header .chapter-links .chapter-link:nth-child(11),
        .chapter-radio:nth-of-type(12):checked ~ .header .chapter-links .chapter-link:nth-child(12),
        .chapter-radio:nth-of-type(13):checked ~ .header .chapter-links .chapter-link:nth-child(13),
        .chapter-radio:nth-of-type(14):checked ~ .header .chapter-links .chapter-link:nth-child(14),
        .chapter-radio:nth-of-type(15):checked ~ .header .chapter-links .chapter-link:nth-child(15),
        .chapter-radio:nth-of-type(16):checked ~ .header .chapter-links .chapter-link:nth-child(16),
        .chapter-radio:nth-of-type(17):checked ~ .header .chapter-links .chapter-link:nth-child(17),
        .chapter-radio:nth-of-type(18):checked ~ .header .chapter-links .chapter-link:nth-child(18),
        .chapter-radio:nth-of-type(19):checked ~ .header .chapter-links .chapter-link:nth-child(19),
        .chapter-radio:nth-of-type(20):checked ~ .header .chapter-links .chapter-link:nth-child(20) {{
            background: #007bff;
            color: white;
            border-bottom-color: white;
        }}

        .toggle-index-btn,
        .translate-icon-btn {{
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

        .translate-icon-btn {{
            background-color: transparent;
            padding: 2px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }}

        .toggle-index-btn:hover {{
            background: #5a6268;
        }}

        .translate-icon-btn:hover {{
            transform: scale(1.1);
        }}

        .translate-icon-btn svg {{
            stroke: #e6d4a6;
            width: 20px;
            height: 20px;
        }}

        /* 목차 토글 */
        .index-navigation {{
            display: none;
            margin-top: 15px;
            padding: 15px;
            background: white;
            border-radius: 8px;
            border: 1px solid #dee2e6;
        }}

        .index-toggle:checked ~ .header .index-navigation {{
            display: block;
        }}

        .index-toggle:checked ~ .header .toggle-index-btn {{
            background: #5a6268;
        }}

        .index-toggle:checked ~ .header .toggle-index-btn::after {{
            content: " 숨기기";
        }}

        .toggle-index-btn::after {{
            content: " 보기";
        }}

        .index-item {{
            display: flex;
            align-items: center;
            padding: 8px 12px;
            margin-bottom: 5px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            color: inherit;
            display: flex;
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
            display: none;
        }}

        /* 번역 토글 */
        .translation-toggle:checked ~ .content .korean-text {{
            display: block;
        }}

        /* 단어 링크 스타일 */
        .word-link {{
            position: relative;
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

        /* 툴팁 스타일 */
        .word-tooltip {{
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            background: #333;
            color: white;
            padding: 10px 15px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: normal;
            white-space: nowrap;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
            z-index: 100;
            text-decoration: none;
            min-width: 200px;
            text-align: left;
            line-height: 1.4;
        }}

        .word-tooltip::after {{
            content: "";
            position: absolute;
            top: 100%;
            left: 50%;
            transform: translateX(-50%);
            border: 6px solid transparent;
            border-top-color: #333;
        }}

        .word-link:hover .word-tooltip {{
            opacity: 1;
        }}

        /* 한국어 대상 단어 스타일 */
        .word-target-kr {{
            color: #dc3545;
            font-weight: 600;
            padding: 2px 4px;
            border-radius: 3px;
            background: rgba(220, 53, 69, 0.1);
        }}

        /* 반응형 디자인 */
        @media (max-width: 768px) {{
            .chapter-link {{
                padding: 6px 8px;
                min-width: 25px;
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
            .word-tooltip {{
                white-space: normal;
                max-width: 200px;
            }}
        }}
    </style>
</head>
<body>
    {translation_checkbox}
    {index_checkbox}
    {chapter_radios}

    <div class="header">
        {navigation_html}
        {index_html}
    </div>

    <div class="content">
        {chapters_html}
    </div>
</body>
</html>'''

    return html_template


def main():
    # 명령줄 인자 처리
    parser = argparse.ArgumentParser(
        description='CSS 전용 대화형 어휘 학습 HTML 뷰어를 생성합니다.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
예시 사용법:
  python css_story_viewer_generator.py ./word_table ./stories output_story.html
  python css_story_viewer_generator.py /path/to/word_table /path/to/stories my_story.html
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
