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
            console.error(`❌ 파일 없음: ${fullPath}`);
            return null;
        }
        const content = fs.readFileSync(fullPath, 'utf-8');
        return { content, data: JSON.parse(content.replace(/\u00A0/g, ' ')) };
    } catch (error) {
        console.error(`❌ 파일 처리 오류 (${filePath}):`, error);
        return null;
    }
}

function processWordTags(text) {
    const pattern = /<word\s+id=['"]([^'"]+)['"]\s+class=['"]word-eng-link['"]>([^<]+)<\/word>/g;
    return text.replace(pattern, '<span class="word-link" data-word-id="$1">$2</span>');
}

function generateWordDataJs(wordsData) {
    const wordDict = {};
    wordsData.forEach(word => {
        if (word.id) {
            wordDict[word.id] = {
                term: word.term,
                kor_meaning: word.kor_meaning,
                synonyms: (word.synonyms || []).join(', ')
            };
        }
    });
    return JSON.stringify(wordDict, null, 4);
}

// ★★★ 이 함수가 올바른 HTML 구조를 생성하도록 수정되었습니다 ★★★
function generateChaptersHtml(storiesData, contentHash) {
    let chaptersHtml = "", numberNavigation = "", indexNavigation = "";
    storiesData.forEach((chapter, idx) => {
        const chapterTitle = chapter.chapter_title || `Chapter ${idx + 1}`;
        const href = `#chapter-${idx}-${contentHash}`;
        
        numberNavigation += `<a href="${href}" class="chapter-link">${idx + 1}</a>`;
        indexNavigation += `<div class="index-item" data-href="${href}"><span class="index-number">${idx + 1}.</span><span class="index-title">${chapterTitle}</span></div>`;
        
        let storyContentHtml = "";
        (chapter.paragraphs || []).forEach(paragraph => {
            storyContentHtml += `<div class="paragraph-group">`;
            (paragraph.sentences || []).forEach(pair => {
                const englishSentence = processWordTags(pair.english || '');
                const koreanSentence = pair.korean || '';
                const encodedKorean = koreanSentence.replace(/"/g, '&#34;');

                // 문장과 버튼을 별도의 div로 감싸서 flexbox 레이아웃을 올바르게 적용
                storyContentHtml += `<div class="sentence-container">
                    <p class="english-text">${englishSentence}</p>
                    <button class="translate-sentence-btn" data-translation="${encodedKorean}" title="이 문장 번역 보기">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6.9l-7.4 7.4-2.6-2.6L20 6.9z"></path><path d="M14 17.1L14 17.1z"></path><path d="M3 12.5L3 12.5z"></path><path d="M3 7l7.4 7.4-2.6 2.6L3 7z"></path><path d="M14 6.9L14 6.9z"></path></svg>
                    </button>
                </div>`;
            });
            storyContentHtml += `</div>`;
        });

        chaptersHtml += `<div id="chapter-${idx}" class="chapter-content" style="display: none;"><h2>${chapterTitle}</h2><div class="story-content">${storyContentHtml}</div></div>`;
    });
    return { numberNavigation, indexNavigation, chaptersHtml };
}

app.get('/', (req, res) => {
    const dataPath = path.join(__dirname, 'data');
    let storyList = [];
    try {
        const sets = fs.readdirSync(dataPath, { withFileTypes: true }).filter(d => d.isDirectory()).map(d => d.name);
        for (const set of sets) {
            const storiesPath = path.join(dataPath, set, 'stories');
            if (fs.existsSync(storiesPath)) {
                const parts = fs.readdirSync(storiesPath, { withFileTypes: true }).filter(d => d.isDirectory()).map(d => d.name);
                for (const part of parts) {
                    const storyJsonPath = path.join(storiesPath, part, 'stories.json');
                    const storyFile = loadJsonFile(storyJsonPath);
                    if (storyFile && storyFile.data.part_title) {
                        storyList.push({
                            title: `${set} - ${storyFile.data.part_title}`,
                            url: `/view?set=${set}&part=${part}`
                        });
                    }
                }
            }
        }
        res.render('index', { storyList });
    } catch (error) {
        res.status(500).send("<h1>스토리 목록을 만드는 중 오류가 발생했습니다.</h1>");
    }
});

app.get('/view', (req, res) => {
    const { set, part } = req.query;
    if (!set || !part) return res.status(400).send("<h1>오류: set과 part 파라미터가 필요합니다.</h1>");
    const storyJsonPath = path.join('data', set, 'stories', part, 'stories.json');
    const storyFile = loadJsonFile(storyJsonPath);
    if (!storyFile) return res.status(404).send(`<h1>오류: ${storyJsonPath} 파일을 찾을 수 없습니다.</h1>`);
    
    const stories = storyFile.data.stories || [];
    let allWords = [];
    let combinedWordContent = '';
    const wordsByChapter = {};

    stories.forEach((chapter, idx) => {
        if (chapter.ref_word_table) {
            const wordTablePath = path.join('data', set, 'words_table', part, chapter.ref_word_table);
            const wordFile = loadJsonFile(wordTablePath);
            if (wordFile) {
                const chapterWords = wordFile.data.words || [];
                allWords.push(...chapterWords);
                combinedWordContent += wordFile.content;
                wordsByChapter[idx] = chapterWords;
            }
        }
    });
    
    allWords = allWords.filter((word, index, self) => index === self.findIndex((w) => w.id === word.id));
    const contentHash = crypto.createHash('md5').update(combinedWordContent).digest('hex').substring(0, 8);
    const wordDataJs = generateWordDataJs(allWords);
    const { numberNavigation, indexNavigation, chaptersHtml } = generateChaptersHtml(stories, contentHash);

    res.render('viewer', {
        page_title: `${storyFile.data.part_title || 'Untitled'} - ${set}`,
        number_navigation: numberNavigation,
        index_navigation: indexNavigation,
        chapters_html: chaptersHtml,
        word_data_js: wordDataJs,
        words_by_chapter_json: JSON.stringify(wordsByChapter),
        content_hash: contentHash
    });
});

app.listen(PORT, () => console.log(`서버가 http://localhost:${PORT} 에서 실행 중입니다.`));