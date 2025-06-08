# app.py

import os
import json
from flask import Flask, jsonify, abort

# Flask 앱 인스턴스 생성
app = Flask(__name__)

def load_json_file(file_path):
    """지정된 경로의 JSON 파일을 로드하는 헬퍼 함수"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # 파일이 없으면 404 에러 발생
        abort(404, description=f"Resource not found: {file_path}")
    except json.JSONDecodeError:
        # JSON 파싱 실패 시 500 에러 발생
        abort(500, description=f"Failed to decode JSON from {file_path}")

@app.route("/")
def get_active_data():
    """
    active_data.json을 읽어 활성화된 데이터셋의 내용을 반환합니다.
    """
    try:
        # 1. active_data.json 파일의 경로를 설정하고 파일을 로드합니다.
        #    os.path.dirname(__file__)는 현재 app.py 파일이 있는 디렉토리를 가리킵니다.
        base_dir = os.path.dirname(__file__)
        config_path = os.path.join(base_dir, 'active_data.json')
        config = load_json_file(config_path)
        
        # 2. 설정 파일에서 활성 데이터 디렉토리 경로를 가져옵니다.
        active_dir_path = config.get("active_directory")
        if not active_dir_path:
            abort(500, description="'active_directory' not found in active_data.json")

        # 3. word_table.json과 stories.json 파일의 전체 경로를 구성합니다.
        word_table_path = os.path.join(base_dir, active_dir_path, 'word_table.json')
        stories_path = os.path.join(base_dir, active_dir_path, 'stories.json')

        # 4. 두 JSON 파일을 로드합니다.
        word_data = load_json_file(word_table_path)
        story_data = load_json_file(stories_path)

        # 5. 두 파일의 내용을 합쳐서 하나의 JSON 객체로 반환합니다.
        combined_data = {
            "words_data": word_data,
            "stories_data": story_data
        }
        
        return jsonify(combined_data)

    except Exception as e:
        # 예상치 못한 에러 처리
        # abort 함수에서 발생한 HTTP 예외는 그대로 전달됩니다.
        if hasattr(e, 'code'):
            raise e
        # 그 외의 서버 내부 오류
        app.logger.error(f"An unexpected error occurred: {e}")
        abort(500, description=str(e))

# Gunicorn이 아닌, 'python app.py'로 직접 실행할 때를 위한 코드 블록
if __name__ == "__main__":
    # debug=True는 개발 중에만 사용해야 합니다.
    # Render와 같은 프로덕션 환경에서는 Gunicorn이 이 파일을 실행하므로 이 블록은 실행되지 않습니다.
    app.run(debug=True, port=5001)