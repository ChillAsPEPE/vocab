const express = require('express');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const app = express();
const PORT = 3000;

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));
app.use(express.static('public'));
app.use('/data', express.static(path.join(__dirname, 'data')));

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
        if(word.id) wordDict[word.id] = { term: word.term, kor_meaning: word.kor_meaning, synonyms: (word.synonyms || []).join(', ') };
    });
    return JSON.stringify(wordDict, null, 4);
}

// 이 함수가 새로운 'paragraphs' 데이터 구조를 처리하도록 수정되었습니다.
function generateChaptersHtml(storiesData, contentHash) {
    let chaptersHtml = "", numberNavigation = "", indexNavigation = "";
    storiesData.forEach((chapter, idx) => {
        const chapterTitle = chapter.chapter_title || `Chapter ${idx + 1}`;
        const href = `#chapter-${idx}-${contentHash}`;
        
        numberNavigation += `<a href="${href}" class="chapter-link">${idx + 1}</a>`;
        indexNavigation += `<div class="index-item" data-href="${href}"><span class="index-number">${idx + 1}.</span><span class="index-title">${chapterTitle}</span></div>`;
        
        let storyContentHtml = "";
        (chapter.paragraphs || []).forEach(paragraph => {
            let paragraphSentences = '';
            (paragraph.sentences || []).forEach(pair => {
                const englishSentence = processWordTags(pair.english || '');
                const koreanSentence = processWordTags(pair.korean || '', false);
                const encodedKorean = koreanSentence.replace(/"/g, '&#34;');
                
                // 각 문장을 별도의 span으로 감싸고, 문장 단위의 번역 데이터를 속성으로 가집니다.
                paragraphSentences += `<span class="sentence-unit" data-translation="${encodedKorean}">${englishSentence}</span> `;
            });
            // 문단 내의 모든 문장들을 하나의 P 태그로 묶습니다.
            storyContentHtml += `<p class="english-paragraph">${paragraphSentences.trim()}</p>`;
        });

        // 챕터별로 컨텐츠를 생성합니다. (display:none 으로 초기에 숨김)
        chaptersHtml += `<div id="chapter-${idx}" class="chapter-content" style="display: none;"><h2>${chapterTitle}</h2><div class="story-content">${storyContentHtml}</div></div>`;
    });
    return { numberNavigation, indexNavigation, chaptersHtml };
}


app.get('/', (req, res) => {
    const dataPath = path.join(__dirname, 'data');
    let storyList = [];
    try {
        const sets = fs.readdirSync(dataPath, { withFileTypes: true }).filter(d => d.isDirectory() && d.name !== 'out').map(d => d.name);
        for (const set of sets) {
            const setPath = path.join(dataPath, set);
            const storiesPath = path.join(setPath, 'stories');
            if (fs.existsSync(storiesPath)) {
                const parts = fs.readdirSync(storiesPath, { withFileTypes: true }).filter(d => d.isDirectory()).map(d => d.name);
                for (const part of parts) {
                    const storyJsonPath = path.join(storiesPath, part, 'stories.json');
                    const storyFile = loadJsonFile(storyJsonPath);
                    if (storyFile && storyFile.data.part_title) {
                        let coverImagePath = '/images/default-cover.jpg';
                        const jpgCoverPath = path.join(storiesPath, part, 'cover.jpg');
                        const pngCoverPath = path.join(storiesPath, part, 'cover.png');
                        if (fs.existsSync(jpgCoverPath)) coverImagePath = `/data/${set}/stories/${part}/cover.jpg`;
                        else if (fs.existsSync(pngCoverPath)) coverImagePath = `/data/${set}/stories/${part}/cover.png`;
                        
                        const partNumber = part.replace('part', '');

                        storyList.push({
                            seriesTitle: set,
                            partTitle: storyFile.data.part_title,
                            partNumber: partNumber,
                            genre: storyFile.data.genre || '장르 미정',
                            url: `/view?set=${set}&part=${part}`,
                            coverImagePath: coverImagePath
                        });
                    }
                }
            }
        }
        res.render('index', { storyList });
    } catch (error) {
        console.error("!!! 스토리 목록 생성 중 오류:", error);
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
        chapters_html: chaptersHtml, // Edge 읽기 모드 대응 전의 방식으로, 모든 챕터 HTML을 한 번에 전달
        word_data_js: wordDataJs,
        words_by_chapter_json: JSON.stringify(wordsByChapter),
        content_hash: contentHash
    });
});

app.listen(PORT, () => console.log(`서버가 http://localhost:${PORT} 에서 실행 중입니다.`));