// generate_html.js

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const ejs = require('ejs'); // EJS를 직접 사용하기 위해 모듈 추가

// --- 헬퍼 함수들 (변경 없음) ---
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

/**
 * 메인 실행 함수
 */
async function main() {
    console.log("--- HTML 파일 생성 시작 ---");

    const configResult = loadJsonFile('active_data.json');
    if (!configResult || !configResult.data.active_directory || !configResult.data.active_output) {
        console.error("❌ 오류: active_data.json 파일 또는 'active_directory', 'active_output' 키를 찾을 수 없습니다.");
        return;
    }

    const activeDirectory = configResult.data.active_directory;
    const outputDirectory = path.resolve(__dirname, configResult.data.active_output);

    if (!fs.existsSync(outputDirectory)) {
        fs.mkdirSync(outputDirectory, { recursive: true });
        console.log(`[정보] 출력 폴더 생성: ${outputDirectory}`);
    }

    try {
        const setPath = path.join(__dirname, activeDirectory);
        const setName = path.basename(setPath);
        
        console.log(`[정보] 처리 대상 디렉토리: ${setPath}`);

        const storiesPath = path.join(setPath, 'stories');
        if (!fs.existsSync(storiesPath)) {
            console.error(`❌ 오류: stories 폴더를 찾을 수 없습니다: ${storiesPath}`);
            return;
        }
            
        const parts = fs.readdirSync(storiesPath, { withFileTypes: true }).filter(d => d.isDirectory()).map(d => d.name);

        for (const part of parts) {
            console.log(`\n[처리중] ${setName}/${part} ...`);
            const storyJsonPath = path.join(storiesPath, part, 'stories.json');
            const storyFile = loadJsonFile(storyJsonPath);
            if (!storyFile) continue;

            const stories = storyFile.data.stories || [];
            let allWords = [];
            let combinedWordContent = '';
            const wordsByChapter = {};

            for (const [idx, chapter] of stories.entries()) {
                if (chapter.ref_word_table) {
                    const wordTablePath = path.join(setPath, 'words_table', part, chapter.ref_word_table);
                    const wordFile = loadJsonFile(wordTablePath);
                    if (wordFile) {
                        const chapterWords = wordFile.data.words || [];
                        allWords.push(...chapterWords);
                        combinedWordContent += wordFile.content;
                        wordsByChapter[idx] = chapterWords;
                    }
                }
            }

            allWords = allWords.filter((word, index, self) => index === self.findIndex((w) => w.id === word.id));
            const contentHash = crypto.createHash('md5').update(combinedWordContent).digest('hex').substring(0, 8);
            
            const wordDataJs = generateWordDataJs(allWords);
            const { numberNavigation, indexNavigation, chaptersHtml } = generateChaptersHtml(stories, contentHash);
            
            const templateData = {
                page_title: `${storyFile.data.part_title || 'Untitled'} - ${setName}`,
                number_navigation: numberNavigation,
                index_navigation: indexNavigation,
                chapters_html: chaptersHtml,
                word_data_js: wordDataJs,
                words_by_chapter_json: JSON.stringify(wordsByChapter),
                content_hash: contentHash
            };

            // EJS를 사용하여 HTML 파일 생성
            const ejsTemplatePath = path.join(__dirname, 'views', 'viewer.ejs');
            const finalHtml = await ejs.renderFile(ejsTemplatePath, templateData);

            const partTitle = storyFile.data.part_title || 'Untitled';
            const sanitizedTitle = partTitle.replace(/\s+/g, '-').replace(/[^a-zA-Z0-9-]/g, '');
            const outputFilename = `${part}_${sanitizedTitle}.html`;
            const outputPath = path.join(outputDirectory, outputFilename);

            fs.writeFileSync(outputPath, finalHtml, 'utf-8');
            console.log(`✅ 성공: ${outputPath} 파일이 생성되었습니다.`);
        }
        
    } catch (error) {
        console.error("!!! 전체 프로세스 중 오류 발생:", error);
    }
    console.log("\n--- 모든 작업 완료 ---");
}

main();