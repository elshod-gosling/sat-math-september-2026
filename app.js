// Application State
let currentExamKey = 'v1';
let currentModuleIndex = 0; // 0 for Module 1, 1 for Module 2
let currentQuestionIndex = 0; // 0 to 21
let userAnswers = {}; // key: "v1_m1_q1" -> value
let markedForReview = {}; // key: "v1_m1_q1" -> boolean
let struckOptions = {}; // key: "v1_m1_q1_A" -> boolean
let strikethroughMode = false;
let testMode = 'timed'; // 'timed' or 'untimed'
let feedbackMode = 'exam'; // 'exam' or 'study'
let elapsedSeconds = 0;
let timerSeconds = 2100; // 35 minutes
let timerInterval = null;
let timerHidden = false;
let desmosCalc = null;
let isDocked = false;
let instantFeedbackRevealed = {}; // key: q.id -> boolean

function initKaTeX() {
  if (window.renderMathInElement) {
    renderMathInElement(document.body, {
      delimiters: [
        {left: '$$', right: '$$', display: true},
        {left: '$', right: '$', display: false},
        {left: '\\(', right: '\\)', display: false},
        {left: '\\[', right: '\\]', display: true}
      ],
      throwOnError: false
    });
  }
}

// Initialize on page load
window.addEventListener('DOMContentLoaded', () => {
  initDesmosCalculator();
  showLandingPage();
  initKaTeX();
});

function showLandingPage() {
  const landing = document.getElementById('landing-page');
  const exam = document.getElementById('exam-view');
  if (landing) landing.style.display = 'flex';
  if (exam) exam.style.display = 'none';
  if (timerInterval) clearInterval(timerInterval);
  const win = document.getElementById('desmos-floating-window');
  if (win) win.style.display = 'none';
  const btn = document.getElementById('btn-calculator');
  if (btn) btn.classList.remove('active');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function returnToHome() {
  const answeredCount = Object.keys(userAnswers).length;
  if (answeredCount > 0) {
    if (!confirm('Return to home screen? Your current test will be paused.')) {
      return;
    }
  }
  showLandingPage();
}

function setTestMode(mode) {
  testMode = mode;
  const btnTimed = document.getElementById('btn-mode-timed');
  const btnUntimed = document.getElementById('btn-mode-untimed');
  if (btnTimed) btnTimed.classList.toggle('active', mode === 'timed');
  if (btnUntimed) btnUntimed.classList.toggle('active', mode === 'untimed');
}

function setFeedbackMode(mode) {
  feedbackMode = mode;
  const btnExam = document.getElementById('btn-fb-exam');
  const btnStudy = document.getElementById('btn-fb-study');
  if (btnExam) btnExam.classList.toggle('active', mode === 'exam');
  if (btnStudy) btnStudy.classList.toggle('active', mode === 'study');
}

function launchExam(examKey, modIndex = 0) {
  currentExamKey = examKey;
  const landing = document.getElementById('landing-page');
  const exam = document.getElementById('exam-view');
  if (landing) landing.style.display = 'none';
  if (exam) exam.style.display = 'flex';
  document.getElementById('exam-select').value = examKey;
  userAnswers = {};
  markedForReview = {};
  struckOptions = {};
  instantFeedbackRevealed = {};
  startModule(modIndex);
}


function initDesmosCalculator() {
  const target = document.getElementById('desmos-calculator-target');
  try {
    if (window.Desmos && Desmos.GraphingCalculator) {
      desmosCalc = Desmos.GraphingCalculator(target, {
        keypad: true,
        graphpaper: true,
        expressions: true,
        settingsMenu: true,
        zoomButtons: true,
        border: false
      });
    } else {
      target.innerHTML = '<iframe src="https://www.desmos.com/calculator" style="width:100%; height:100%; border:none;"></iframe>';
    }
  } catch (e) {
    console.warn('Desmos init error, fallback to iframe:', e);
    target.innerHTML = '<iframe src="https://www.desmos.com/calculator" style="width:100%; height:100%; border:none;"></iframe>';
  }
  setupDesmosDrag();
}

function setupDesmosDrag() {
  const win = document.getElementById('desmos-floating-window');
  const bar = document.getElementById('desmos-drag-bar');
  let isDragging = false, startX, startY, initLeft, initTop;

  bar.addEventListener('mousedown', (e) => {
    if (e.target.classList.contains('desmos-ctrl-btn')) return;
    isDragging = true;
    startX = e.clientX;
    startY = e.clientY;
    const rect = win.getBoundingClientRect();
    initLeft = rect.left;
    initTop = rect.top;
    e.preventDefault();
  });

  window.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    const dx = e.clientX - startX;
    const dy = e.clientY - startY;
    win.style.left = Math.max(10, Math.min(window.innerWidth - win.offsetWidth - 10, initLeft + dx)) + 'px';
    win.style.top = Math.max(54, Math.min(window.innerHeight - win.offsetHeight - 10, initTop + dy)) + 'px';
    win.style.right = 'auto';
  });

  window.addEventListener('mouseup', () => { isDragging = false; });
}

function toggleCalculator() {
  const win = document.getElementById('desmos-floating-window');
  const dock = document.getElementById('dock-pane');
  const btn = document.getElementById('btn-calculator');

  if (isDocked) {
    dock.style.display = 'none';
    isDocked = false;
    btn.classList.remove('active');
    return;
  }

  if (win.style.display === 'flex') {
    win.style.display = 'none';
    btn.classList.remove('active');
  } else {
    win.style.display = 'flex';
    btn.classList.add('active');
    if (desmosCalc && desmosCalc.resize) desmosCalc.resize();
  }
}

function dockCalculator() {
  const win = document.getElementById('desmos-floating-window');
  const dock = document.getElementById('dock-pane');
  const dockTarget = document.getElementById('desmos-docked-target');
  const calcTarget = document.getElementById('desmos-calculator-target');

  win.style.display = 'none';
  dock.style.display = 'flex';
  dockTarget.appendChild(calcTarget);
  isDocked = true;
  if (desmosCalc && desmosCalc.resize) desmosCalc.resize();
}

function undockCalculator() {
  const win = document.getElementById('desmos-floating-window');
  const dock = document.getElementById('dock-pane');
  const calcTarget = document.getElementById('desmos-calculator-target');

  dock.style.display = 'none';
  win.appendChild(calcTarget);
  win.style.display = 'flex';
  isDocked = false;
  if (desmosCalc && desmosCalc.resize) desmosCalc.resize();
}

// Exam Lifecycle
function startExam(examKey) {
  currentExamKey = examKey;
  currentModuleIndex = 0;
  currentQuestionIndex = 0;
  userAnswers = {};
  markedForReview = {};
  struckOptions = {};
  document.getElementById('exam-select').value = examKey;
  startModule(0);
}

function switchExam(examKey) {
  if (confirm('Switch to ' + (examKey === 'v1' ? 'Exam V1' : 'Exam V2') + '? Progress will reset.')) {
    startExam(examKey);
  } else {
    document.getElementById('exam-select').value = currentExamKey;
  }
}

function startModule(modIndex) {
  currentModuleIndex = modIndex;
  currentQuestionIndex = 0;
  const mod = EXAM_DATABASE[currentExamKey].modules[modIndex];
  timerSeconds = mod.time || 2100;
  startTimer();
  document.getElementById('header-module-badge').innerText = 'Module ' + (modIndex + 1);
  renderQuestion();
}

function startTimer() {
  if (timerInterval) clearInterval(timerInterval);
  if (testMode === 'timed') {
    updateTimerDisplay();
    timerInterval = setInterval(() => {
      if (timerSeconds > 0) {
        timerSeconds--;
        updateTimerDisplay();
      } else {
        clearInterval(timerInterval);
        alert('Time is up for this module! Directing to module review.');
        showModuleReview();
      }
    }, 1000);
  } else {
    elapsedSeconds = 0;
    updateTimerDisplay();
    timerInterval = setInterval(() => {
      elapsedSeconds++;
      updateTimerDisplay();
    }, 1000);
  }
}

function updateTimerDisplay() {
  const display = document.getElementById('timer-display');
  if (testMode === 'timed') {
    const mins = Math.floor(timerSeconds / 60);
    const secs = timerSeconds % 60;
    const formatted = String(mins).padStart(2, '0') + ':' + String(secs).padStart(2, '0');
    display.innerText = timerHidden ? '--:--' : formatted;

    if (timerSeconds <= 300) {
      display.classList.add('timer-warning');
      if (timerHidden) toggleTimerVisibility();
    } else {
      display.classList.remove('timer-warning');
    }
  } else {
    const mins = Math.floor(elapsedSeconds / 60);
    const secs = elapsedSeconds % 60;
    const formatted = String(mins).padStart(2, '0') + ':' + String(secs).padStart(2, '0');
    display.innerText = timerHidden ? '--:--' : formatted + ' (Untimed)';
    display.classList.remove('timer-warning');
  }
}

function toggleTimerVisibility() {
  timerHidden = !timerHidden;
  document.getElementById('btn-timer-toggle').innerText = timerHidden ? 'Show' : 'Hide';
  updateTimerDisplay();
}

// Render Question
function renderQuestion() {
  const mod = EXAM_DATABASE[currentExamKey].modules[currentModuleIndex];
  const q = mod.questions[currentQuestionIndex];
  const scrollArea = document.getElementById('content-scroll-area');
  const isMarked = !!markedForReview[q.id];

  document.getElementById('main-footer').style.display = 'flex';
  document.getElementById('btn-back').disabled = (currentQuestionIndex === 0);
  document.getElementById('nav-toggle-text').innerText = 'Question ' + (currentQuestionIndex + 1) + ' of ' + mod.questions.length;
  document.getElementById('btn-next').innerText = (currentQuestionIndex === mod.questions.length - 1) ? 'Review Module' : 'Next';

  let html = '<div class="question-card">';
  html += '<div class="question-top-bar">';
  html += '  <div class="q-number-badge">Question ' + q.num + '</div>';
  html += '  <div class="q-actions-bar">';
  html += '    <button class="btn-mark-review ' + (isMarked ? 'marked' : '') + '" onclick="toggleMarkForReview(\'' + q.id + '\')">';
  html += '      <svg viewBox="0 0 24 24"><polygon points="6 2 18 2 18 22 12 18 6 22"></polygon></svg>';
  html += '      Mark for Review';
  html += '    </button>';
  if (q.type === 'mc') {
    html += '    <button class="btn-strikethrough-toggle ' + (strikethroughMode ? 'active' : '') + '" onclick="toggleStrikethroughMode()">ABC <s>S</s></button>';
  }
  html += '  </div>';
  html += '</div>';

  html += '<div class="question-stem">';
  if (q.figure) {
    html += '<div class="figure-container"><img src="' + q.figure + '" alt="Figure"></div>';
  }
  html += q.stem;
  html += '</div>';

  if (q.type === 'mc') {
    html += '<div class="options-group ' + (strikethroughMode ? 'strikethrough-mode' : '') + '">';
    q.options.forEach(opt => {
      const isSelected = (userAnswers[q.id] === opt.key);
      const isStruck = !!struckOptions[q.id + '_' + opt.key];
      html += '<div class="option-item ' + (isSelected ? 'selected' : '') + ' ' + (isStruck ? 'struck' : '') + '" onclick="selectOption(\'' + q.id + '\', \'' + opt.key + '\')">';
      html += '  <div class="option-left">';
      html += '    <div class="option-bubble">' + opt.key + '</div>';
      html += '    <div class="option-text">' + opt.text + '</div>';
      html += '  </div>';
      html += '  <button class="btn-strike-option" title="Strikethrough" onclick="toggleOptionStrike(event, \'' + q.id + '\', \'' + opt.key + '\')">✕</button>';
      html += '</div>';
    });
    html += '</div>';
  } else {
    const currentVal = userAnswers[q.id] || '';
    html += '<div class="gridin-container">';
    html += '  <div class="gridin-header">';
    html += '    <span>Student-Produced Response:</span>';
    html += '    <span class="gridin-help-link" onclick="openModal(\'spr-modal\')">How to enter your answer</span>';
    html += '  </div>';
    html += '  <div class="gridin-input-wrapper">';
    html += '    <input type="text" class="gridin-input" id="gridin-input-' + q.id + '" value="' + currentVal + '" placeholder="Enter answer" oninput="handleGridInChange(\'' + q.id + '\', this.value)">';
    html += '    <div class="gridin-preview" id="gridin-preview-' + q.id + '"></div>';
    html += '    <button class="btn-gridin-clear" onclick="clearGridIn(\'' + q.id + '\')">Clear</button>';
    html += '  </div>';
    html += '</div>';
  }

  // Study Mode Instant Feedback
  if (feedbackMode === 'study') {
    const hasAns = (userAnswers[q.id] !== undefined && userAnswers[q.id] !== '');
    if (hasAns) {
      if (instantFeedbackRevealed[q.id]) {
        const uAns = (userAnswers[q.id] || '').trim();
        const cAns = q.answer.trim();
        const isCorr = (q.type === 'mc') ? (uAns.toUpperCase() === cAns.toUpperCase()) : evaluateGridInMatch(uAns, cAns);
        
        html += '<div class="instant-feedback-box ' + (isCorr ? 'correct' : 'incorrect') + '">';
        html += '  <div style="font-weight:700; margin-bottom:6px;">' + (isCorr ? '✓ Correct!' : '✕ Incorrect') + ' (Correct Answer: ' + cAns + ')</div>';
        html += '  <div style="font-size:0.92rem; line-height:1.5;"><strong>Solution:</strong> ' + q.explanation + '</div>';
        if (q.desmos_tip) {
          html += '  <div class="desmos-tip-box" style="margin-top:8px;"><strong>⚡ Desmos Tip:</strong> ' + q.desmos_tip + '</div>';
        }
        html += '</div>';
      } else {
        html += '<button class="btn-check-answer" onclick="revealInstantFeedback(\'' + q.id + '\')">✓ Check Answer & Solution</button>';
      }
    }
  }

  html += '</div>';
  scrollArea.innerHTML = html;

  initKaTeX();
  updateNavDrawer();
  if (q.type === 'grid') {
    const inp = document.getElementById('gridin-input-' + q.id);
    if (inp) updateGridInPreview(q.id, inp.value);
  }
}

function revealInstantFeedback(qId) {
  instantFeedbackRevealed[qId] = true;
  renderQuestion();
}

// User Actions
function selectOption(qId, optKey) {
  if (struckOptions[qId + '_' + optKey]) return;
  instantFeedbackRevealed[qId] = false;
  if (userAnswers[qId] === optKey) {
    delete userAnswers[qId];
  } else {
    userAnswers[qId] = optKey;
  }
  renderQuestion();
}

function toggleOptionStrike(e, qId, optKey) {
  e.stopPropagation();
  const k = qId + '_' + optKey;
  struckOptions[k] = !struckOptions[k];
  if (struckOptions[k] && userAnswers[qId] === optKey) {
    delete userAnswers[qId];
  }
  renderQuestion();
}

function toggleStrikethroughMode() {
  strikethroughMode = !strikethroughMode;
  renderQuestion();
}

function handleGridInChange(qId, val) {
  userAnswers[qId] = val.trim();
  instantFeedbackRevealed[qId] = false;
  updateGridInPreview(qId, val);
  updateNavDrawer();
}

function clearGridIn(qId) {
  delete userAnswers[qId];
  instantFeedbackRevealed[qId] = false;
  const inp = document.getElementById('gridin-input-' + qId);
  if (inp) {
    inp.value = '';
    updateGridInPreview(qId, '');
  }
  updateNavDrawer();
}

function updateGridInPreview(qId, val) {
  const prev = document.getElementById('gridin-preview-' + qId);
  if (!prev) return;
  if (val.includes('/')) {
    const parts = val.split('/');
    if (parts.length === 2 && parts[0] && parts[1]) {
      prev.innerHTML = '$\\frac{' + parts[0] + '}{' + parts[1] + '}$';
      initKaTeX();
      return;
    }
  }
  prev.innerText = val;
}

function toggleMarkForReview(qId) {
  markedForReview[qId] = !markedForReview[qId];
  renderQuestion();
}

// Navigation
function navigateBack() {
  if (currentQuestionIndex > 0) {
    currentQuestionIndex--;
    renderQuestion();
  }
}

function navigateNext() {
  const mod = EXAM_DATABASE[currentExamKey].modules[currentModuleIndex];
  if (currentQuestionIndex < mod.questions.length - 1) {
    currentQuestionIndex++;
    renderQuestion();
  } else {
    showModuleReview();
  }
}

function jumpToQuestion(idx) {
  currentQuestionIndex = idx;
  closeNavDrawer();
  renderQuestion();
}

function toggleNavDrawer() {
  document.getElementById('nav-drawer').classList.toggle('open');
}

function closeNavDrawer() {
  document.getElementById('nav-drawer').classList.remove('open');
}

function updateNavDrawer() {
  const mod = EXAM_DATABASE[currentExamKey].modules[currentModuleIndex];
  const grid = document.getElementById('nav-grid-tiles');
  let html = '';
  mod.questions.forEach((q, idx) => {
    const isAns = (userAnswers[q.id] !== undefined && userAnswers[q.id] !== '');
    const isCurr = (idx === currentQuestionIndex);
    const isMrk = !!markedForReview[q.id];
    let cls = 'nav-tile';
    if (isAns) cls += ' answered';
    if (isCurr) cls += ' current';
    if (isMrk) cls += ' marked';
    html += '<div class="' + cls + '" onclick="jumpToQuestion(' + idx + ')">' + q.num + '</div>';
  });
  grid.innerHTML = html;
}

// Module Review Screen
function showModuleReview() {
  closeNavDrawer();
  document.getElementById('main-footer').style.display = 'none';
  const mod = EXAM_DATABASE[currentExamKey].modules[currentModuleIndex];
  const scrollArea = document.getElementById('content-scroll-area');

  let unansweredCount = 0;
  let reviewCardsHtml = '';
  mod.questions.forEach((q, idx) => {
    const isAns = (userAnswers[q.id] !== undefined && userAnswers[q.id] !== '');
    const isMrk = !!markedForReview[q.id];
    if (!isAns) unansweredCount++;

    reviewCardsHtml += '<div class="review-tile ' + (isAns ? 'answered' : 'unanswered') + '" onclick="jumpToQuestion(' + idx + ')">';
    reviewCardsHtml += '  <div><strong>Question ' + q.num + '</strong></div>';
    reviewCardsHtml += '  <div style="font-size:0.8rem; color:' + (isAns ? '#12b76a' : '#f04438') + ';">';
    reviewCardsHtml += (isAns ? 'Answered' : 'Unanswered') + (isMrk ? ' 🚩' : '');
    reviewCardsHtml += '  </div>';
    reviewCardsHtml += '</div>';
  });

  let html = '<div class="screen-container">';
  html += '<div class="screen-header">';
  html += '  <h2>Review: Section 2, Module ' + (currentModuleIndex + 1) + '</h2>';
  html += '  <p>Check your answers before submitting this module. Once submitted, you cannot return to Module ' + (currentModuleIndex + 1) + '.</p>';
  if (unansweredCount > 0) {
    html += '<div style="background:#fee4e2; border:1px solid #fecdca; color:#b42318; border-radius:6px; padding:12px; margin-top:12px;">';
    html += '  ⚠️ You have <strong>' + unansweredCount + '</strong> unanswered question' + (unansweredCount > 1 ? 's' : '') + '.';
    html += '</div>';
  }
  html += '</div>';

  html += '<div class="review-grid">' + reviewCardsHtml + '</div>';

  html += '<div style="display:flex; justify-content:space-between; align-items:center; margin-top:20px;">';
  html += '  <button class="btn-nav" style="background:#667085;" onclick="jumpToQuestion(0)">Return to Questions</button>';
  if (currentModuleIndex === 0) {
    html += '  <button class="btn-nav" onclick="finishModule1()">Submit Module 1 & Next</button>';
  } else {
    html += '  <button class="btn-nav" style="background:#12b76a;" onclick="submitEntireExam()">Submit Final Exam & View Score</button>';
  }
  html += '</div>';
  html += '</div>';

  scrollArea.innerHTML = html;
}

function finishModule1() {
  if (confirm('Are you sure you want to submit Module 1? You cannot change Module 1 answers after this.')) {
    clearInterval(timerInterval);
    showBreakScreen();
  }
}

// 10-Minute Break Screen
function showBreakScreen() {
  let breakSeconds = 600;
  const scrollArea = document.getElementById('content-scroll-area');

  function updateBreakDisplay() {
    const m = Math.floor(breakSeconds / 60);
    const s = breakSeconds % 60;
    const el = document.getElementById('break-timer');
    if (el) el.innerText = String(m).padStart(2, '0') + ':' + String(s).padStart(2, '0');
  }

  let html = '<div class="screen-container" style="text-align:center; max-width:600px;">';
  html += '  <div class="screen-header">';
  html += '    <h2>Take a 10-Minute Break</h2>';
  html += '    <p>You have finished Module 1. You may take a 10-minute break before starting Module 2.</p>';
  html += '  </div>';
  html += '  <div style="font-size:3.5rem; font-weight:800; font-family:monospace; color:var(--bb-blue); margin: 20px 0;" id="break-timer">10:00</div>';
  html += '  <p style="color:#667085; font-size:0.9rem;">You can resume testing at any time by clicking below.</p>';
  html += '  <div style="margin-top:24px;">';
  html += '    <button class="btn-nav" style="margin: 0 auto; padding:12px 36px; font-size:1.1rem;" onclick="startModule(1)">Resume Testing Now (Module 2)</button>';
  html += '  </div>';
  html += '</div>';

  scrollArea.innerHTML = html;

  const breakInterval = setInterval(() => {
    if (breakSeconds > 0) {
      breakSeconds--;
      updateBreakDisplay();
    } else {
      clearInterval(breakInterval);
      startModule(1);
    }
  }, 1000);
}

// Final Exam Submission & Score Engine
function submitEntireExam() {
  if (confirm('Submit complete test and calculate official score?')) {
    clearInterval(timerInterval);
    showScoreReport();
  }
}

function showScoreReport() {
  document.getElementById('main-footer').style.display = 'none';
  const scrollArea = document.getElementById('content-scroll-area');
  const exam = EXAM_DATABASE[currentExamKey];
  const m1 = exam.modules[0].questions;
  const m2 = exam.modules[1].questions;

  let m1Correct = 0, m2Correct = 0;
  let questionResults = [];

  [m1, m2].forEach((modQList, modIdx) => {
    modQList.forEach(q => {
      const userAns = (userAnswers[q.id] || '').trim();
      const correctAns = q.answer.trim();
      let isCorrect = false;

      if (q.type === 'mc') {
        isCorrect = (userAns.toUpperCase() === correctAns.toUpperCase());
      } else {
        isCorrect = evaluateGridInMatch(userAns, correctAns);
      }

      if (isCorrect) {
        if (modIdx === 0) m1Correct++;
        else m2Correct++;
      }

      questionResults.push({
        q: q,
        modNum: modIdx + 1,
        userAns: userAns,
        correctAns: correctAns,
        isCorrect: isCorrect,
        isOmitted: (userAns === '')
      });
    });
  });

  const totalCorrect = m1Correct + m2Correct;
  const scaledScore = exam.score_table ? exam.score_table[totalCorrect] : (200 + totalCorrect * 13.6);

  let html = '<div class="screen-container">';
  html += '<div class="score-summary-card">';
  html += '  <div>';
  html += '    <h3 style="font-size:1.2rem; opacity:0.9; margin-bottom:6px;">Your Math Score: ' + exam.title + '</h3>';
  html += '    <div style="display:flex; align-items:baseline; gap:8px;">';
  html += '      <span class="score-big">' + scaledScore + '</span>';
  html += '      <span class="score-scale">/ 800</span>';
  html += '    </div>';
  html += '    <div class="score-breakdown-row">';
  html += '      <div class="score-badge">Total Correct: ' + totalCorrect + ' / 44</div>';
  html += '      <div class="score-badge">Module 1: ' + m1Correct + ' / 22</div>';
  html += '      <div class="score-badge">Module 2: ' + m2Correct + ' / 22</div>';
  html += '    </div>';
  html += '  </div>';
  html += '  <div style="display:flex; flex-direction:column; gap:10px;">';
  html += '    <button class="btn-nav" style="background:#ffffff; color:#003366;" onclick="startExam(currentExamKey)">Retake Test</button>';
  html += '    <button class="btn-nav" style="background:#1e293b; color:#ffffff; border:1px solid #475569;" onclick="showLandingPage()">Choose Another Exam</button>';
  html += '  </div>';
  html += '</div>';

  html += '<div style="margin-top:24px;">';
  html += '  <h3 style="font-size:1.3rem; margin-bottom:16px; color:#1d2939;">Question-by-Question Review & Explanations</h3>';

  questionResults.forEach((res) => {
    const q = res.q;
    let cardCls = res.isCorrect ? 'correct' : (res.isOmitted ? 'omitted' : 'incorrect');
    let tagCls = cardCls;
    let tagText = res.isCorrect ? 'Correct' : (res.isOmitted ? 'Omitted' : 'Incorrect');

    html += '<div class="analysis-card ' + cardCls + '">';
    html += '  <div class="analysis-header">';
    html += '    <div><strong>Module ' + res.modNum + ', Question ' + q.num + '</strong> (' + (q.type === 'mc' ? 'Multiple Choice' : 'Grid-in') + ')</div>';
    html += '    <span class="status-tag ' + tagCls + '">' + tagText + '</span>';
    html += '  </div>';

    if (q.figure) {
      html += '<div class="figure-container"><img src="' + q.figure + '" style="max-height:200px;" alt="Figure"></div>';
    }

    html += '  <div style="font-size:0.95rem; line-height:1.5; margin-bottom:12px;">' + q.stem + '</div>';

    html += '  <div style="font-size:0.9rem; margin-bottom:10px;">';
    html += '    <strong>Your Answer:</strong> <span style="color:' + (res.isCorrect ? '#12b76a' : '#d92d20') + '; font-weight:600;">' + (res.userAns || 'None') + '</span> &nbsp;|&nbsp; ';
    html += '    <strong>Correct Answer:</strong> <span style="color:#12b76a; font-weight:700;">' + res.correctAns + '</span>';
    html += '  </div>';

    html += '  <div style="font-size:0.92rem; color:#344054; line-height:1.5; background:#f9fafb; padding:12px; border-radius:6px; border:1px solid #eaecf0;">';
    html += '    <strong>Step-by-Step Solution:</strong><br>' + q.explanation;
    html += '  </div>';

    if (q.desmos_tip) {
      html += '  <div class="desmos-tip-box">';
      html += '    <strong>⚡ Desmos Calculator Tip:</strong> ' + q.desmos_tip;
      html += '  </div>';
    }

    html += '</div>';
  });

  html += '</div>';
  html += '</div>';

  scrollArea.innerHTML = html;
  initKaTeX();
}

function evaluateGridInMatch(userStr, correctStr) {
  if (!userStr) return false;
  if (userStr.toLowerCase() === correctStr.toLowerCase()) return true;

  try {
    const parseNum = (s) => {
      if (s.includes('/')) {
        const p = s.split('/');
        return parseFloat(p[0]) / parseFloat(p[1]);
      }
      return parseFloat(s);
    };
    const uVal = parseNum(userStr);
    const cVal = parseNum(correctStr);
    if (!isNaN(uVal) && !isNaN(cVal)) {
      return Math.abs(uVal - cVal) < 0.005;
    }
  } catch (e) {}
  return false;
}

// Modals
function openModal(id) {
  const modal = document.getElementById(id);
  if (modal) modal.classList.add('open');
  initKaTeX();
}

function closeModal(id) {
  const modal = document.getElementById(id);
  if (modal) modal.classList.remove('open');
}

function toggleFullScreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen().catch(() => {});
  } else {
    if (document.exitFullscreen) document.exitFullscreen();
  }
}
