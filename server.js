// server.js

const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3000;

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// --- 헬퍼 함수들 (이전과 동일) ---
function loadJsonFile(filePath) {
    try {
        const fullPath = path.resolve(__dirname, filePath);
        if (!fs.existsSync(fullPath)) {
            console.error(`!!! 오류: 파일이 존재하지 않습니다 - ${fullPath}`);
            return null;
        }
        let content = fs.readFileSync(fullPath, 'utf-8');
        content = content.replace(/\u00A0/g, ' ');
        return JSON.parse(content);
    } catch (error) {
        console.error(`!!! 파일 처리 오류 (${filePath}):`, error);
        return null;
    }
}

function processWordTags(text, isEnglish = true) {
    if (isEnglish) {
        const pattern = /<word\s+id=['"]([^'"]+)['"]\s+class=['"]word-eng-link['"]>([^<]+)<\/word>/g;
        return text.replace(pattern, '<span class="word-link" data-word-id="$1">$2</span>');
    } else {
        const pattern = /<word\s+id=['"]([^'"]+)['"]\s+class=['"]word-target-kr['"]>([^<]+)<\/word>/g;
        return text.replace(pattern, '<span class="word-target-kr">$2</span>');
    }
}

function generateWordDataJs(wordsData) {
    const wordDict = {};
    wordsData.forEach(word => {
        wordDict[word.id] = {
            term: word.term,
            kor_meaning: word.kor_meaning,
            synonyms: (word.synonyms || []).join(', ')
        };
    });
    return JSON.stringify(wordDict, null, 4);
}

function generateChaptersHtml(storiesData) {
    let chaptersHtml = "", numberNavigation = "", indexNavigation = "";
    storiesData.forEach((chapter, idx) => {
        const chapterTitle = chapter.chapter_title || `Chapter ${idx + 1}`;
        const activeClass = (idx === 0) ? "active" : "";
        numberNavigation += `<a href="javascript:void(0)" class="chapter-link ${activeClass}" onclick="showChapter(${idx})">${idx + 1}</a>`;
        indexNavigation += `<div class="index-item" onclick="showChapter(${idx})"><span class="index-number">${idx + 1}.</span><span class="index-title">${chapterTitle}</span></div>`;
        
        let sentencesHtml = "";
        (chapter.story_sentences || []).forEach(pair => {
            const englishSentence = processWordTags(pair.english || '', true);
            const koreanSentence = processWordTags(pair.korean || '', false);
            sentencesHtml += `<div class="sentence-pair"><p class="english-text">${englishSentence}</p><p class="korean-text" style="display: none;">${koreanSentence}</p></div>`;
        });

        const visibleStyle = (idx === 0) ? "" : "style='display: none;'";
        chaptersHtml += `<div id="chapter-${idx}" class="chapter-content" ${visibleStyle}><h2>${chapterTitle}</h2><div class="story-content">${sentencesHtml}</div></div>`;
    });
    return { numberNavigation, indexNavigation, chaptersHtml };
}

// --- 메인 라우트 ---
app.get('/', (req, res) => {
    console.log("--- 요청 처리 시작 ---");

    // 1. 설정 파일('active_data.json')을 읽습니다.
    const config = loadJsonFile('active_data.json');
    if (!config || !config.active_directory) {
        console.error("!!! 오류: active_data.json 파일 또는 'active_directory' 키를 찾을 수 없습니다.");
        return res.status(500).send("<h1>오류: `active_data.json` 파일에 `active_directory` 설정이 없습니다.</h1>");
    }
    
    const activeDirectory = config.active_directory;
    console.log(`[정보] 활성 데이터 디렉토리: ${activeDirectory}`);

    // 2. 설정된 디렉토리 경로와 파일명을 조합하여 최종 파일 경로를 생성합니다.
    const wordTablePath = path.join(activeDirectory, 'word_table.json');
    const storiesPath = path.join(activeDirectory, 'stories.json');
    
    // 3. 조합된 경로로 실제 데이터 파일들을 읽습니다.
    const wordData = loadJsonFile(wordTablePath);
    const storyData = loadJsonFile(storiesPath);

    if (!wordData || !storyData) {
        return res.status(500).send(`<h1>오류: 데이터 파일을 읽을 수 없습니다.</h1><p>경로: '${activeDirectory}' 내에 'word_table.json'과 'stories.json' 파일이 있는지 확인하세요.</p>`);
    }

    // 4. 각 파일에서 실제 데이터 배열을 추출합니다.
    const words = wordData.words || [];
    const stories = storyData.stories || [];

    console.log(`[성공] 단어 ${words.length}개 로드.`);
    console.log(`[성공] 스토리 ${stories.length}개 로드.`);
    
    // 5. 데이터를 가공하여 HTML 렌더링
    const wordDataJs = generateWordDataJs(words);
    const { numberNavigation, indexNavigation, chaptersHtml } = generateChaptersHtml(stories);
    
    console.log("--- 렌더링 완료 ---");

    res.render('viewer', {
        number_navigation: numberNavigation,
        index_navigation: indexNavigation,
        chapters_html: chaptersHtml,
        word_data_js: wordDataJs,
		all_words_json: JSON.stringify(words) 
    });
});

app.listen(PORT, () => {
    console.log(`서버가 http://localhost:${PORT} 에서 실행 중입니다.`);
});
