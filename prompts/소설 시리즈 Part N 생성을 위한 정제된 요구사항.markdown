# 소설 시리즈 Part N 생성을 위한 API 요구사항 템플릿

## 1. 기본 설정 및 목표

- **입력 데이터:**
  - `<소설의 장르>`: SF, 100년 후의 미래 지구에서 벌어지는 AI 와 유전자 변형 신종 인간계, 그 중 하층민인 자연인 인간 간의 갈등과 음모가 펼쳐지는 스릴러
  - `<시리즈 들 중 현재 파트가 몇번째 시리즈인지>`: 총 N개의 파트 중 현재 M번째 파트.
  - `<이전 시리즈의 내용>`: 이전 파트의 내용. 첫 번째 파트인 경우 무시.
  - `<요구 단어 난이도 수준>`: `term` 외 단어의 난이도 수준 (예: 2500단어 수준).
  - `word_table_chapter_N.json` 파일 리스트 (예: `word_table_chapter_1.json`). 각 파일은 `words` 배열 포함, 단어 객체 필드:
    - `num`: 정수 (단어 식별자).
    - `id`: 문자열 (고유 식별자, 예: `_abreast`).
    - `term`: 문자열 (영어 단어, 예: `abreast`).
    - `synonyms`: 문자열 배열 (예: `["alongside", "in a row"]`).
    - `kor_meaning`: 문자열 (한국어 의미, 예: `나란히`, 품사 내포).

- **출력 목표:** Part 타이틀, 전체 텍스트, 장르, 챕터 객체를 포함하는 소설 JSON. 출력 형식:
```json
{
  "part_title": "문자열",
  "part_full_text": "문자열",
  "genre": "문자열",
  "stories": [
    {
      "chapter_title": "문자열",
      "chapter_num": 0,
      "ref_word_table": "문자열",
      "paragraphs": [
        {
          "sentences": [
            {
              "english": "문자열",
              "korean": "문자열"
            },
            ...
          ]
        },
        ...
      ]
    },
    ...
  ]
}
```

- **맥락:** `<이전 시리즈의 내용>`을 반영하여 이야기 구상. 첫 번째 파트인 경우 새로운 이야기 시작.
- **완성도:** 문장과 스토리의 완성도를 최우선으로 하여 자연스럽고 흥미로운 이야기를 구성. 입력된 모든 `term`은 단 하나도 빠뜨리지 않고 반드시 사용.

## 2. 챕터 JSON 생성 규칙

### 2.1. 단어 선정
- 해당 `word_table_chapter_N.json` 파일의 `words` 배열에 있는 **모든** `term`을 사용해 한 챕터 구성. 단 하나도 빠뜨리지 않음.
- `term`, `id`, `kor_meaning` 추출.

### 2.2. 이야기 및 문장 생성
- **장르:** `<소설의 장르>`에 맞는 이야기 구성.
- **시리즈 계획:** 모든 입력 파일 기반으로 Part M의 전체 흐름 구상. 각 챕터는 전체 이야기에 기여.
- **챕터 연속성:** 첫 챕터 제외, 각 챕터는 이전 챕터의 사건, 분위기, 클라이맥스를 자연스럽게 이어감.
- **영어 문장:**
  - 모든 `term`을 최소 1회 사용해 장르에 맞는 흥미롭고 일관된 이야기 구성.
  - `term` 외 단어는 `<요구 단어 난이도 수준>`에 맞춤. 
  - 한 문장은 0~2개의 `term`만 포함.
  - 단어 수준이 낮다고 해서 문장 자체의 질이 떨어져서는 절대로 안 됨. 
  - 문장은 문법적으로 완벽하고 자연스러워야 함.
- **문장 수:** `term` 수와 비슷한 수준 (예: 10개 `term` → 약 8~12문장).
- **스토리 완성도:** 흥미로운 줄거리, 일관된 캐릭터, 자연스러운 전개로 독자 몰입도 극대화.

### 2.3. `term` 사용 요구사항
- **의미 일치:**
  - `term`은 `synonyms`와 `kor_meaning`에 맞는 문맥에서 사용.
  - `term`을 `synonyms` 또는 `kor_meaning`(영어로 번역, 예: `나란히` → “side by side”)으로 대체해도 문장이 자연스럽고 정확.
- **품사 일치:**
  - `term`은 `kor_meaning`의 품사와 동일하게 사용 (예: `act`가 `행동`(명사)면 명사로).
- **예시:**
  - 입력: `{"term": "abreast", "id": "_abreast", "synonyms": ["alongside", "in a row"], "kor_meaning": "나란히"}` (부사).
  - 문장: `The robots moved <word id="_abreast" class="word-eng-link">abreast</word> in formation.`
  - 검증:
    - 동의어: `alongside` → `The robots moved alongside...` (자연스러움).
    - `kor_meaning`: `나란히` → `The robots moved side by side...` (자연스러움).
    - 품사: `abreast`는 부사, `나란히`(부사)와 일치.

### 2.4. 문장 객체 생성
- 이야기를 개별 문장으로 분리.
- 각 문장에 대해 JSON 객체:
  - `english`: 영어 문장, `term`은 `<word id='{id}' class='word-eng-link'>{term}</word>`로 태그.
  - `korean`: 한국어 번역, `kor_meaning`은 `<word id='{id}' class='word-target-kr'>{adjusted_kor_meaning}</word>`로 태그. `adjusted_kor_meaning`은 한국어 문법에 맞게 반드시 조정 (예: “행동” → “행동을”).
- 예시:
```json
{
  "english": "The leader performed an <word id='_act' class='word-eng-link'>act</word> of courage.",
  "korean": "리더는 용감한 <word id='_act' class='word-target-kr'>행동을</word> 했다."
}
```

### 2.5. 문단 구분
- 챕터는 여러 문단으로 구성 가능. 문단은 `paragraphs` 배열로 구분.
- 각 문단은 `sentences` 배열로 문장 객체 포함. 문단 구분은 이야기의 자연스러운 흐름 (예: 장면 전환, 주제 변경)에 따라 결정.
- 예시:
```json
{
  "paragraphs": [
    {
      "sentences": [
        {
          "english": "The robots moved <word id='_abreast' class='word-eng-link'>abreast</word> in formation.",
          "korean": "로봇들이 대형을 맞춰 <word id='_abreast' class='word-target-kr'>나란히</word> 이동했다."
        },
        ...
      ]
    },
    ...
  ]
}
```

### 2.6. 챕터 JSON 객체
- `chapter_title`: 챕터 내용을 반영한 창의적인 영어 제목.
- `chapter_num`: 정수, 첫 챕터는 0, 이후 1씩 증가.
- `ref_word_table`: 해당 챕터에 사용된 입력 파일명 (예: “word_table_chapter_1.json”).
- `paragraphs`: 2.5의 문단 배열, 이야기 순서대로.

### 2.7. Part 타이틀
- `part_title`: Part M을 대표하는 창의적인 영어 제목, 장르와 주제 반영.

### 2.8. Part 전체 텍스트
- `part_full_text`: 모든 챕터의 `paragraphs` 내 `sentences`의 `english` 문장을 순서대로 연결. 문장 사이 공백 1개, HTML 태그 유지. 한국어 번역 제외.

### 2.9. 오류 처리
- 입력 파일에 오류 (예: `kor_meaning` 누락) 시, 해당 단어의 대표 의미를 `kor_meaning`으로 대체 (예: `synonyms`의 첫 번째 값).

## 3. 출력
- `part_title`, `part_full_text`, `genre`, `stories` 배열 포함 JSON. 각 입력 파일에 해당하는 챕터 객체 포함.
- 예시 (1개 챕터, 2개 문단):
```json
{
  "part_title": "Eternal Quest",
  "part_full_text": "The robots moved <word id='_abreast' class='word-eng-link'>abreast</word> in formation. The leader showed no <word id='_affectation' class='word-eng-link'>affectation</word> in their command.",
  "genre": "SF",
  "stories": [
    {
      "chapter_title": "New Horizons",
      "chapter_num": 0,
      "ref_word_table": "word_table_chapter_1.json",
      "paragraphs": [
        {
          "sentences": [
            {
              "english": "The robots moved <word id='_abreast' class='word-eng-link'>abreast</word> in formation.",
              "korean": "로봇들이 대형을 맞춰 <word id='_abreast' class='word-target-kr'>나란히</word> 이동했다."
            }
          ]
        },
        {
          "sentences": [
            {
              "english": "The leader showed no <word id='_affectation' class='word-eng-link'>affectation</word> in their command.",
              "korean": "리더는 명령에서 <word id='_affectation' class='word-target-kr'>가식을</word> 보이지 않았다."
            }
          ]
        }
      ]
    }
  ]
}
```