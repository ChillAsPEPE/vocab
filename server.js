// server.js

const express = require('express');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const app = express();
const PORT = 3000;

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

function loadJsonFile(filePath) {
    try {
        const fullPath = path.resolve(__dirname, filePath);
        if (!fs.existsSync(fullPath)) {
            console.error(`!!! 오류: 파일이 존재하지 않습니다 - ${fullPath}`);
            return null;
        }
        const content = fs.readFileSync(fullPath, 'utf-8');
        return { content, data: JSON.parse(content.replace(/\u00A0/g, ' ')) };
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

function generateChaptersHtml(storiesData, contentHash) {
    let chaptersHtml = "", numberNavigation = "", indexNavigation = "";
    storiesData.forEach((chapter, idx) => {
        const chapterTitle = chapter.chapter_title || `Chapter ${idx + 1}`;
        const href = `#chapter-${idx}-${contentHash}`;
        
        numberNavigation += `<a href="${href}" class="chapter-link">${idx + 1}</a>`;
        indexNavigation += `<div class="index-item" data-href="${href}"><span class="index-number">${idx + 1}.</span><span class="index-title">${chapterTitle}</span></div>`;
        
        let sentencesHtml = "";
        (chapter.story_sentences || []).forEach(pair => {
            const englishSentence = processWordTags(pair.english || '', true);
            const koreanSentence = processWordTags(pair.korean || '', false);
            sentencesHtml += `<div class="sentence-pair"><p class="english-text">${englishSentence}</p><p class="korean-text" style="display: none;">${koreanSentence}</p></div>`;
        });
        chaptersHtml += `<div id="chapter-${idx}" class="chapter-content" style="display: none;"><h2>${chapterTitle}</h2><div class="story-content">${sentencesHtml}</div></div>`;
    });
    return { numberNavigation, indexNavigation, chaptersHtml };
}

app.get('/', (req, res) => {
    console.log("--- 요청 처리 시작 ---");

    const configResult = loadJsonFile('active_data.json');
    if (!configResult || !configResult.data.active_directory) {
        return res.status(500).send("<h1>오류: `active_data.json` 설정 파일이 없거나 'active_directory' 키가 없습니다.</h1>");
    }
    
    const activeDirectory = configResult.data.active_directory;
    const wordTablePath = path.join(activeDirectory, 'word_table.json');
    const storiesPath = path.join(activeDirectory, 'stories.json');
    
    const wordFile = loadJsonFile(wordTablePath);
    const storyFile = loadJsonFile(storiesPath);

    if (!wordFile || !storyFile) {
        return res.status(500).send(`<h1>오류: 데이터 파일을 읽을 수 없습니다.</h1><p>경로: '${activeDirectory}' 내에 'word_table.json'과 'stories.json' 파일이 있는지 확인하세요.</p>`);
    }

    const words = wordFile.data.words || [];
    const stories = storyFile.data.stories || [];
    
    const contentHash = crypto.createHash('md5').update(storyFile.content).digest('hex').substring(0, 8);
    console.log(`[정보] 생성된 콘텐츠 해시: ${contentHash}`);

    const wordDataJs = generateWordDataJs(words);
    const { numberNavigation, indexNavigation, chaptersHtml } = generateChaptersHtml(stories, contentHash);
    
    console.log("--- 렌더링 완료 ---");

    res.render('viewer', {
        number_navigation: numberNavigation,
        index_navigation: indexNavigation,
        chapters_html: chaptersHtml,
        word_data_js: wordDataJs,
        all_words_json: JSON.stringify(words),
        content_hash: contentHash
    });
});

app.listen(PORT, () => {
    console.log(`서버가 http://localhost:${PORT} 에서 실행 중입니다.`);
});