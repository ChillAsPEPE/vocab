const ejs = require('ejs');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const mkdirp = require('mkdirp');

// Output directory for static files
const OUTPUT_DIR = path.join(__dirname, 'out');

// Ensure output directory exists
mkdirp.sync(OUTPUT_DIR);

// Copy static assets (public folder and data folder for images)
function copyStaticAssets() {
  const publicSrc = path.join(__dirname, 'public');
  const publicDest = path.join(OUTPUT_DIR, 'public');
  const dataSrc = path.join(__dirname, 'data');
  const dataDest = path.join(OUTPUT_DIR, 'data');

  // Copy public folder
  if (fs.existsSync(publicSrc)) {
    mkdirp.sync(publicDest);
    fs.cpSync(publicSrc, publicDest, { recursive: true });
  }

  // Copy data folder (for cover images)
  if (fs.existsSync(dataSrc)) {
    mkdirp.sync(dataDest);
    fs.cpSync(dataSrc, dataDest, { recursive: true });
  }
}

// Load JSON file (from server.js)
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

// Process word tags (from server.js)
function processWordTags(text, isEnglish = true) {
  if (isEnglish) {
    const pattern = /<word\s+id=['"]([^'"]+)['"]\s+class=['"]word-eng-link['"]>([^<]+)<\/word>/g;
    return text.replace(pattern, '<span class="word-link" data-word-id="$1">$2</span>');
  } else {
    const pattern = /<word\s+id=['"]([^'"]+)['"]\s+class=['"]word-target-kr['"]>([^<]+)<\/word>/g;
    return text.replace(pattern, '<span class="word-target-kr">$2</span>');
  }
}

// Generate word data JS (from server.js)
function generateWordDataJs(wordsData) {
  const wordDict = {};
  wordsData.forEach(word => {
    if (word.id) wordDict[word.id] = { term: word.term, kor_meaning: word.kor_meaning, synonyms: (word.synonyms || []).join(', ') };
  });
  return JSON.stringify(wordDict, null, 4);
}

// Generate chapters HTML (from server.js)
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
        
        paragraphSentences += `<span class="sentence-unit" data-translation="${encodedKorean}">${englishSentence}</span> `;
      });
      storyContentHtml += `<p class="english-paragraph">${paragraphSentences.trim()}</p>`;
    });

    chaptersHtml += `<div id="chapter-${idx}" class="chapter-content" style="display: none;"><h2>${chapterTitle}</h2><div class="story-content">${storyContentHtml}</div></div>`;
  });
  return { numberNavigation, indexNavigation, chaptersHtml };
}

// Generate index.html
function generateIndexPage() {
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
              url: `/view/${set}/${part}.html`, // Static URL
              coverImagePath: coverImagePath
            });
          }
        }
      }
    }

    // Render index.ejs to HTML
    const indexTemplate = path.join(__dirname, 'views', 'index.ejs');
    ejs.renderFile(indexTemplate, { storyList }, (err, html) => {
      if (err) {
        console.error('!!! index.ejs 렌더링 오류:', err);
        return;
      }
      fs.writeFileSync(path.join(OUTPUT_DIR, 'index.html'), html);
      console.log('✅ index.html 생성 완료');
    });
  } catch (error) {
    console.error('!!! 스토리 목록 생성 중 오류:', error);
  }
}

// Generate viewer pages
function generateViewerPages() {
  const dataPath = path.join(__dirname, 'data');
  const sets = fs.readdirSync(dataPath, { withFileTypes: true }).filter(d => d.isDirectory() && d.name !== 'out').map(d => d.name);

  for (const set of sets) {
    const setPath = path.join(dataPath, set);
    const storiesPath = path.join(setPath, 'stories');
    if (fs.existsSync(storiesPath)) {
      const parts = fs.readdirSync(storiesPath, { withFileTypes: true }).filter(d => d.isDirectory()).map(d => d.name);
      for (const part of parts) {
        const storyJsonPath = path.join('data', set, 'stories', part, 'stories.json');
        const storyFile = loadJsonFile(storyJsonPath);
        if (!storyFile) {
          console.error(`!!! ${storyJsonPath} 파일을 찾을 수 없습니다.`);
          continue;
        }

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

        // Create output directory for viewer page
        const viewDir = path.join(OUTPUT_DIR, 'view', set);
        mkdirp.sync(viewDir);

        // Render viewer.ejs to HTML
        const viewerTemplate = path.join(__dirname, 'views', 'viewer.ejs');
        ejs.renderFile(viewerTemplate, {
          page_title: `${storyFile.data.part_title || 'Untitled'} - ${set}`,
          number_navigation: numberNavigation,
          index_navigation: indexNavigation,
          chapters_html: chaptersHtml,
          word_data_js: wordDataJs,
          words_by_chapter_json: JSON.stringify(wordsByChapter),
          content_hash: contentHash
        }, (err, html) => {
          if (err) {
            console.error(`!!! viewer.ejs 렌더링 오류 (${set}/${part}):`, err);
            return;
          }
          const outputFile = path.join(viewDir, `${part}.html`);
          fs.writeFileSync(outputFile, html);
          console.log(`✅ ${outputFile} 생성 완료`);
        });
      }
    }
  }
}

// Main function to generate static site
function generateStaticSite() {
  console.log('📦 정적 사이트 생성 시작...');
  copyStaticAssets();
  generateIndexPage();
  generateViewerPages();
  console.log('🎉 정적 사이트 생성 완료!');
}

// Run the generator
generateStaticSite();