<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><%= page_title %></title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif; line-height: 1.6; color: #333; background-color: #f8f9fa; }
        body.no-scroll { overflow: hidden; }
        .chapter-content h2:focus { outline: 2px solid #007bff; box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.25); }
        .container { max-width: 1000px; margin: 0 auto; padding: 20px; }
        .header { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .content { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .navigation-controls { display: flex; flex-direction: column; gap: 15px; margin-bottom: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px; }
        .nav-button-group { display: flex; align-items: center; gap: 10px; }
        .chapter-links-container { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; }
        .nav-label { font-weight: 600; color: #495057; font-size: 14px; margin-right: 9px; }
        .toggle-btn { background: #6c757d; color: white; border: none; padding: 8px 16px; border-radius: 20px; font-size: 12px; cursor: pointer; transition: all 0.3s ease; white-space: nowrap; }
        .toggle-btn:hover { background: #5a6268; }
        .toggle-btn.active-btn { background-color: #007bff; color: white; }
        .chapter-link { display: inline-block; padding: 5px; text-decoration: none; color: #007bff; border: none; border-bottom: 1px solid #007bff; font-weight: 500; font-size: 10px; transition: all 0.3s ease; min-width: 25px; text-align: center; }
        .chapter-link:hover, .chapter-link.active { background: #007bff; color: white; border-bottom-color: white; transform: scale(1.1); }
        .chapter-content h2 { color: #2c3e50; margin-bottom: 30px; text-align: center; font-size: 28px; border-bottom: 3px solid #007bff; padding-bottom: 10px; }
        .paragraph-group { margin-bottom: 25px; }
        .paragraph-group:last-child { margin-bottom: 0; }
        
        /* ★★★ 레이아웃 문제 해결 1: 문장과 버튼을 감싸는 컨테이너 ★★★ */
        .sentence-container { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
        /* ★★★ 레이아웃 문제 해결 2: p 태그에서 flex 속성 제거 ★★★ */
        .english-text { font-size: 18px; line-height: 1.5; color: #2c3e50; flex-grow: 1; }

        .word-link { display: inline; color: #007bff; font-weight: 600; padding: 2px 4px; border-radius: 3px; background: rgba(0, 123, 255, 0.1); cursor: pointer; transition: all 0.3s ease; text-decoration: underline; }
        .word-link:hover { background: rgba(0, 123, 255, 0.3); transform: scale(1.05); }
        .word-target-kr { display: inline; color: #dc3545; font-weight: 600; padding: 2px 4px; border-radius: 3px; background: rgba(220, 53, 69, 0.1); }
        .translate-sentence-btn { background: #f1f3f4; border: 1px solid #dee2e6; width: 24px; height: 24px; border-radius: 50%; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0; transition: all 0.2s ease; }
        .translate-sentence-btn:hover { background-color: #e9ecef; border-color: #adb5bd; }
        .translate-sentence-btn svg { width: 14px; height: 14px; stroke: #495057; pointer-events: none; }
        .bottom-sheet-overlay, .popup-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.4); display: flex; opacity: 0; visibility: hidden; transition: opacity 0.3s ease, visibility 0.3s ease; }
        .popup-overlay { z-index: 2000; align-items: center; justify-content: center; }
        .bottom-sheet-overlay { z-index: 1000; align-items: flex-end; }
        .bottom-sheet-overlay.show, .popup-overlay.show { opacity: 1; visibility: visible; }
        .bottom-sheet-panel { background-color: white; width: 100%; max-width: 1000px; height: 65vh; border-radius: 16px 16px 0 0; box-shadow: 0 -4px 20px rgba(0,0,0,0.15); transform: translateY(100%); transition: transform 0.4s cubic-bezier(0.25, 0.8, 0.25, 1); display: flex; flex-direction: column; }
        .bottom-sheet-overlay.show .bottom-sheet-panel { transform: translateY(0); }
        .bottom-sheet-header { padding: 10px 20px; border-bottom: 1px solid #e9ecef; display: flex; justify-content: space-between; align-items: center; flex-shrink: 0; }
        .bottom-sheet-title { font-size: 16px; font-weight: 600; }
        .bottom-sheet-content { padding: 0 20px 20px 20px; overflow-y: auto; }
        .word-table { width: 100%; border-collapse: collapse; font-size: 14px; }
        .word-table th { position: sticky; top: 0; background-color: white; z-index: 1; border-bottom: 2px solid #dee2e6; padding: 10px; text-align: left; font-weight: 600; }
        .word-table td { padding: 10px; border-bottom: 1px solid #dee2e6; text-align: left; }
        .word-table tbody tr:nth-child(even) { background-color: #f8f9fa; }
        .index-item { display: flex; align-items: center; padding: 12px 0; border-bottom: 1px solid #f1f3f4; cursor: pointer; transition: all 0.2s ease; }
        .index-item:hover { background: #f8f9fa; }
        .index-item:last-child { border-bottom: none; }
        .index-number { font-weight: 600; color: #007bff; margin-right: 12px; min-width: 25px; }
        .index-title { color: #495057; font-size: 14px; }
        .popup-content { background: white; max-width: 400px; width: 90%; border-radius: 15px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3); animation: slideIn 0.3s ease; position: relative; }
        .popup-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 25px 10px; border-bottom: 2px solid #f1f3f4; }
        .popup-header h3 { color: #007bff; font-size: 24px; margin: 0; }
        .close-btn { background: none; border: none; color: #999; font-size: 28px; font-weight: bold; cursor: pointer; transition: color 0.3s ease; padding: 0; line-height: 1; }
        .close-btn:hover { color: #333; }
        .popup-body { padding: 20px 25px; }
        .popup-body p { margin: 0; font-size: 16px; line-height: 1.5; }
        .popup-body p:last-child { margin-bottom: 0; }
        .popup-body strong { color: #2c3e50; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes slideIn { from { transform: translateY(-50px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
    </style>
</head>
<body>
    <div class="content">
        <div class="header">
            <div class="navigation-controls">
                <div class="nav-button-group">
                    <button id="index-toggle-btn" class="toggle-btn" onclick="toggleIndex()">목차 보기</button>
                    <button id="word-list-toggle-btn" class="toggle-btn" onclick="toggleWordList()">단어 목록 보기</button>
                </div>
                <div class="chapter-links-container">
                    <span class="nav-label">Chapters:</span>
                    <%- number_navigation %>
                </div>
            </div>
            <%- chapters_html %>
        </div>
    </div>
    <div id="indexNavigationTemplate" style="display: none;"><%- index_navigation %></div>
    <div id="wordPopupOverlay" class="popup-overlay"><div class="popup-content"><div class="popup-header"><h3 id="popupTerm">단어</h3><button class="close-btn" onclick="closePopup()">&times;</button></div><div class="popup-body"><p id="popupMeaning"><strong>뜻:</strong> </p><p id="popupSynonyms" style="display: none;"><strong>동의어:</strong> </p></div></div></div>
    <div id="sentencePopupOverlay" class="popup-overlay"><div class="popup-content"><div class="popup-body"><p id="sentencePopupText" style="margin: 0;"></p></div></div></div>
    <div id="bottomSheet" class="bottom-sheet-overlay"><div class="bottom-sheet-panel"><div class="bottom-sheet-header"><h3 id="bottomSheetTitle" class="bottom-sheet-title"></h3><button class="close-btn" onclick="closeSheet()">&times;</button></div><div id="bottomSheetContent" class="bottom-sheet-content"></div></div></div>

    <script>
        const wordData = <%- word_data_js %>;
        const wordsByChapter = <%- words_by_chapter_json %>;
        const contentHash = "<%- content_hash %>";
        let currentChapterIndex = 0;

        const bottomSheet = document.getElementById('bottomSheet');
        const wordPopup = document.getElementById('wordPopupOverlay');
        const sentencePopup = document.getElementById('sentencePopupOverlay');
        
        function closeAllPopups() {
            wordPopup.classList.remove('show');
            sentencePopup.classList.remove('show');
            closeSheet();
            document.body.classList.remove('no-scroll');
        }

        function openSheet(type) {
            const indexBtn = document.getElementById('index-toggle-btn');
            const wordListBtn = document.getElementById('word-list-toggle-btn');
            const bottomSheetTitle = document.getElementById('bottomSheetTitle');
            const bottomSheetContent = document.getElementById('bottomSheetContent');
            
            if (bottomSheet.classList.contains('show') && currentSheet === type) {
                return closeSheet();
            }

            if (type === 'index') {
                bottomSheetTitle.textContent = '목차';
                bottomSheetContent.innerHTML = document.getElementById('indexNavigationTemplate').innerHTML;
                indexBtn.classList.add('active-btn');
                wordListBtn.classList.remove('active-btn');
            } else if (type === 'word') {
                const wordsToShow = wordsByChapter[currentChapterIndex] || [];
                bottomSheetTitle.textContent = `Chapter ${currentChapterIndex + 1} 단어 목록`;
                bottomSheetContent.innerHTML = buildWordTableHtml(wordsToShow);
                wordListBtn.classList.add('active-btn');
                indexBtn.classList.remove('active-btn');
            }
            currentSheet = type;
            bottomSheet.classList.add('show');
            document.body.classList.add('no-scroll');
        }

        function closeSheet() {
            if (!bottomSheet) return;
            bottomSheet.classList.remove('show');
            document.getElementById('index-toggle-btn').classList.remove('active-btn');
            document.getElementById('word-list-toggle-btn').classList.remove('active-btn');
            currentSheet = null;
            if (!wordPopup.classList.contains('show') && !sentencePopup.classList.contains('show')) {
                 document.body.classList.remove('no-scroll');
            }
        }
        
        function showWordPopup(wordId) {
            const wordInfo = wordData[wordId];
            if (!wordInfo) return;
            wordPopup.querySelector('#popupTerm').textContent = wordInfo.term;
            wordPopup.querySelector('#popupMeaning').innerHTML = '<strong>뜻:</strong> ' + wordInfo.kor_meaning;
            const synonymsEl = wordPopup.querySelector('#popupSynonyms');
            if (wordInfo.synonyms && wordInfo.synonyms.trim()) {
                synonymsEl.innerHTML = '<strong>동의어:</strong> ' + wordInfo.synonyms;
                synonymsEl.style.display = 'block';
            } else {
                synonymsEl.style.display = 'none';
            }
            wordPopup.classList.add('show');
            document.body.classList.add('no-scroll');
        }
        
        function closePopup() { // 단어 팝업 닫기 전용
            if (!wordPopup) return;
            wordPopup.classList.remove('show');
            if (!bottomSheet.classList.contains('show') && !sentencePopup.classList.contains('show')) {
                document.body.classList.remove('no-scroll');
            }
        }
        
        function showSentencePopup(translation) {
            if (!sentencePopup) return;
            const popupTextEl = sentencePopup.querySelector('#sentencePopupText');
            popupTextEl.innerHTML = translation.replace(/&#34;/g, '"');
            sentencePopup.classList.add('show');
            document.body.classList.add('no-scroll');
        }

        function closeSentencePopup() {
            if (!sentencePopup) return;
            sentencePopup.classList.remove('show');
            if (!bottomSheet.classList.contains('show') && !wordPopup.classList.contains('show')) {
                document.body.classList.remove('no-scroll');
            }
        }
        
        function toggleIndex(){ openSheet('index'); }
        function toggleWordList(){ openSheet('word'); }

        function showChapter(index) {
            currentChapterIndex = index;
            closeSheet();
            document.querySelectorAll('.chapter-content').forEach(c => c.style.display = 'none');
            document.querySelectorAll('.chapter-link').forEach(l => l.classList.remove('active'));
            const chapterEl = document.getElementById('chapter-' + index);
            if(chapterEl) {
                chapterEl.style.display = 'block';
                const titleEl = chapterEl.querySelector('h2');
                if(titleEl) {
                    titleEl.setAttribute('tabindex', '-1');
                    titleEl.focus();
                }
            }
            const activeLink = document.querySelector(`.chapter-link[href="#chapter-${index}-${contentHash}"]`);
            if(activeLink) activeLink.classList.add('active');
        }

        function handleNavigation() {
            const hash = window.location.hash;
            let chapterIndex = 0;
            if (hash && hash.startsWith('#chapter-')) {
                const parts = hash.substring(1).split('-');
                if (parts.length >= 2) {
                    const indexFromHash = parseInt(parts[1], 10);
                    if (!isNaN(indexFromHash)) chapterIndex = indexFromHash;
                }
            }
            showChapter(chapterIndex);
        }

        function buildWordTableHtml(words) {
            if (!words || words.length === 0) return '<p style="padding: 20px; text-align: center;">이 챕터에 해당하는 단어가 없습니다.</p>';
            const config = { term: 'term', kor_meaning: '뜻', synonyms: 'synonyms' };
            const headers = Object.keys(config);
            let table = '<table class="word-table"><thead><tr>';
            Object.values(config).forEach(h => { table += `<th>${h}</th>`; });
            table += '</tr></thead><tbody>';
            words.forEach(word => {
                table += '<tr>';
                headers.forEach(key => {
                    let cellData = Array.isArray(word[key]) ? word[key].join(', ') : word[key];
                    table += `<td>${cellData || ''}</td>`;
                });
                table += '</tr>';
            });
            return table + '</tbody></table>';
        }

        document.addEventListener('DOMContentLoaded', function() {
            handleNavigation();

            document.body.addEventListener('click', function(e) {
                const target = e.target.closest('button, .index-item, .word-link');
                if (!target) return;
                
                if (target.matches('.word-link')) {
                    e.preventDefault();
                    showWordPopup(target.dataset.wordId);
                } else if (target.matches('.translate-sentence-btn')) {
                    e.preventDefault();
                    showSentencePopup(target.dataset.translation);
                } else if (target.matches('.index-item')) {
                    e.preventDefault();
                    window.location.hash = target.dataset.href;
                } else if (target.matches('.close-btn')) {
                     if (target.closest('.popup-overlay')) closePopup();
                     if (target.closest('.bottom-sheet-overlay')) closeSheet();
                }
            });
            
            wordPopup.addEventListener('click', e => { if(e.target === e.currentTarget) closePopup(); });
            sentencePopup.addEventListener('click', e => { if(e.target === e.currentTarget) closeSentencePopup(); });
            bottomSheet.addEventListener('click', e => { if(e.target === e.currentTarget) closeSheet(); });
            
            document.addEventListener('keydown', e => { if (e.key === 'Escape') { closePopup(); closeSheet(); closeSentencePopup(); }});
        });

        window.addEventListener('hashchange', handleNavigation, false);
    </script>
</body>
</html>