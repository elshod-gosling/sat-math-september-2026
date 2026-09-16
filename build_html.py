# -*- coding: utf-8 -*-
"""
Assembles the complete standalone SAT Math Bluebook application into a single HTML file:
SAT_Math_September_2026_Bluebook.html
"""

import json
import os

BASE_DIR = r"C:\Users\elsho\Documents\gemini\math\september 2026"

# 1. Load exam data
with open(os.path.join(BASE_DIR, "full_exam_data.json"), "r", encoding="utf-8") as f:
    exam_data = json.load(f)

# Ensure score_table is present both at root and within v1/v2
if "score_table" in exam_data:
    exam_data["v1"]["score_table"] = exam_data["score_table"]
    exam_data["v2"]["score_table"] = exam_data["score_table"]

exam_data_json_str = json.dumps(exam_data, ensure_ascii=False)

# 2. Load CSS
with open(os.path.join(BASE_DIR, "styles.css"), "r", encoding="utf-8") as f:
    styles_css = f.read()

# 3. Load and enhance JS
with open(os.path.join(BASE_DIR, "app.js"), "r", encoding="utf-8") as f:
    app_js = f.read()

# Make sure Desmos init has retry logic for async CDN loading
old_desmos_init = """function initDesmosCalculator() {
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
}"""

new_desmos_init = """function initDesmosCalculator(retryCount = 0) {
  const target = document.getElementById('desmos-calculator-target');
  if (!target) return;
  if (window.Desmos && Desmos.GraphingCalculator) {
    try {
      desmosCalc = Desmos.GraphingCalculator(target, {
        keypad: true,
        graphpaper: true,
        expressions: true,
        settingsMenu: true,
        zoomButtons: true,
        border: false
      });
      setupDesmosDrag();
      return;
    } catch (e) {
      console.warn('Desmos init error, fallback to iframe:', e);
    }
  } else if (retryCount < 12) {
    setTimeout(() => initDesmosCalculator(retryCount + 1), 250);
    return;
  }
  // Fallback to official Desmos web app iframe if CDN is unreachable
  target.innerHTML = '<iframe src="https://www.desmos.com/calculator" style="width:100%; height:100%; border:none;"></iframe>';
  setupDesmosDrag();
}"""

if old_desmos_init in app_js:
    app_js = app_js.replace(old_desmos_init, new_desmos_init)

# Ensure scaled score calculation is robust
old_score_calc = "const scaledScore = exam.score_table ? exam.score_table[totalCorrect] : (200 + totalCorrect * 13.6);"
new_score_calc = """const table = exam.score_table || EXAM_DATABASE.score_table;
  const scaledScore = table ? (table[totalCorrect] || table[String(totalCorrect)]) : Math.round(200 + totalCorrect * (600 / 44));"""

if old_score_calc in app_js:
    app_js = app_js.replace(old_score_calc, new_score_calc)

# Build HTML
html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Bluebook — Digital SAT Math Practice (September 2026)</title>
  
  <!-- KaTeX CSS & JS for authentic SAT Math typography -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"></script>

  <!-- Official Desmos API -->
  <script src="https://www.desmos.com/api/v1.9/calculator.js?apiKey=dcb31709b452b1cf9dc26972add0fda6"></script>

  <style>
{styles_css}
  </style>
</head>
<body>

  <!-- ========================================================
       LANDING PAGE (Welcome & Exam Choice)
       ======================================================== -->
  <div id="landing-page">
    <nav class="landing-nav">
      <div class="landing-brand">
        <div class="landing-logo">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="#38bdf8">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
          </svg>
          Bluebook<span>™</span> Practice
        </div>
        <span class="landing-brand-badge">Digital SAT Math</span>
      </div>
      <div class="landing-nav-actions">
        <button class="landing-btn-secondary" onclick="toggleCalculator()">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor">
            <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zM7 10h2v7H7zm4-3h2v10h-2zm4 6h2v4h-2z"/>
          </svg>
          Desmos Calculator
        </button>
        <button class="landing-btn-secondary" onclick="openModal('reference-modal')">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor">
            <path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>
          </svg>
          Reference Sheet
        </button>
        <button class="landing-btn-secondary" onclick="openModal('directions-modal')">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
          </svg>
          Directions
        </button>
        <button class="landing-btn-secondary" onclick="toggleFullScreen()">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor">
            <path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/>
          </svg>
          Fullscreen
        </button>
      </div>
    </nav>

    <div class="landing-body">
      <!-- Hero Header -->
      <div class="landing-hero">
        <div class="landing-pill">
          <span>⚡</span>
          <span>Official September 2026 Test Releases • SAT Zone Academy</span>
        </div>
        <h1 class="landing-title">
          Digital SAT® Math <span class="gradient-text">Practice Suite</span>
        </h1>
        <p class="landing-subtitle">
          Experience authentic College Board Bluebook testing conditions with full-featured Desmos graphing calculator, countdown modules, SPR grid-in answers, and official 200–800 scaled scoring.
        </p>
      </div>

      <!-- Config & Mode Selector -->
      <div class="config-bar">
        <div class="config-group">
          <span class="config-label">Timer Mode:</span>
          <div class="segment-control">
            <button id="btn-mode-timed" class="segment-btn active" onclick="setTestMode('timed')">⏱️ Official Timed (35 min / module)</button>
            <button id="btn-mode-untimed" class="segment-btn" onclick="setTestMode('untimed')">⏳ Untimed / Self-Paced</button>
          </div>
        </div>

        <div class="config-group">
          <span class="config-label">Practice Mode:</span>
          <div class="segment-control">
            <button id="btn-fb-exam" class="segment-btn active" onclick="setFeedbackMode('exam')">🔒 Test Simulation (Score at End)</button>
            <button id="btn-fb-study" class="segment-btn" onclick="setFeedbackMode('study')">💡 Study Mode (Instant Solutions)</button>
          </div>
        </div>
      </div>

      <!-- Exam Selection Cards -->
      <div class="exam-cards-grid">
        <!-- Exam V1 Card -->
        <div class="exam-card">
          <div class="exam-card-badge">Form 1 • September 2026</div>
          <div>
            <h2 class="exam-card-title">September 2026 Exam V1</h2>
            <p class="exam-card-desc">
              Full-length Math assessment covering Algebra, Advanced Math, Problem-Solving & Data Analysis, and Geometry & Trigonometry.
            </p>
          </div>

          <div class="exam-stats-row">
            <div class="stat-box">
              <div class="stat-val">44</div>
              <div class="stat-lbl">Questions</div>
            </div>
            <div class="stat-box">
              <div class="stat-val">70m</div>
              <div class="stat-lbl">Duration</div>
            </div>
            <div class="stat-box">
              <div class="stat-val">800</div>
              <div class="stat-lbl">Max Score</div>
            </div>
            <div class="stat-box">
              <div class="stat-val">2</div>
              <div class="stat-lbl">Modules</div>
            </div>
          </div>

          <div class="modules-list">
            <div class="module-row">
              <div class="module-row-info">
                <span class="module-row-title">Module 1</span>
                <span class="module-row-sub">22 Questions (17 Multiple Choice, 5 Grid-in)</span>
              </div>
              <span style="font-size:0.8rem; font-weight:700; color:#38bdf8;">35 Mins</span>
            </div>
            <div class="module-row">
              <div class="module-row-info">
                <span class="module-row-title">Module 2</span>
                <span class="module-row-sub">22 Questions (18 Multiple Choice, 4 Grid-in)</span>
              </div>
              <span style="font-size:0.8rem; font-weight:700; color:#38bdf8;">35 Mins</span>
            </div>
          </div>

          <div class="exam-actions">
            <button class="btn-start-full" onclick="launchExam('v1', 0)">
              <span>🚀 Start Full Exam V1 (Modules 1 & 2)</span>
            </button>
            <div class="module-buttons-row">
              <button class="btn-start-mod" onclick="launchExam('v1', 0)">Start Module 1 Only</button>
              <button class="btn-start-mod" onclick="launchExam('v1', 1)">Start Module 2 Only</button>
            </div>
          </div>
        </div>

        <!-- Exam V2 Card -->
        <div class="exam-card">
          <div class="exam-card-badge">Form 2 • September 2026</div>
          <div>
            <h2 class="exam-card-title">September 2026 Exam V2</h2>
            <p class="exam-card-desc">
              Comprehensive companion test featuring advanced quadratic models, coordinate geometry, parallel line transversals, and heavy SPR practice.
            </p>
          </div>

          <div class="exam-stats-row">
            <div class="stat-box">
              <div class="stat-val">44</div>
              <div class="stat-lbl">Questions</div>
            </div>
            <div class="stat-box">
              <div class="stat-val">70m</div>
              <div class="stat-lbl">Duration</div>
            </div>
            <div class="stat-box">
              <div class="stat-val">800</div>
              <div class="stat-lbl">Max Score</div>
            </div>
            <div class="stat-box">
              <div class="stat-val">2</div>
              <div class="stat-lbl">Modules</div>
            </div>
          </div>

          <div class="modules-list">
            <div class="module-row">
              <div class="module-row-info">
                <span class="module-row-title">Module 1</span>
                <span class="module-row-sub">22 Questions (17 Multiple Choice, 5 Grid-in)</span>
              </div>
              <span style="font-size:0.8rem; font-weight:700; color:#38bdf8;">35 Mins</span>
            </div>
            <div class="module-row">
              <div class="module-row-info">
                <span class="module-row-title">Module 2</span>
                <span class="module-row-sub">22 Questions (14 Multiple Choice, 8 Grid-in)</span>
              </div>
              <span style="font-size:0.8rem; font-weight:700; color:#38bdf8;">35 Mins</span>
            </div>
          </div>

          <div class="exam-actions">
            <button class="btn-start-full" onclick="launchExam('v2', 0)">
              <span>🚀 Start Full Exam V2 (Modules 1 & 2)</span>
            </button>
            <div class="module-buttons-row">
              <button class="btn-start-mod" onclick="launchExam('v2', 0)">Start Module 1 Only</button>
              <button class="btn-start-mod" onclick="launchExam('v2', 1)">Start Module 2 Only</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Highlights & Bluebook Features -->
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zM7 10h2v7H7zm4-3h2v10h-2zm4 6h2v4h-2z"/>
            </svg>
          </div>
          <div>
            <h4>Embedded Desmos Calculator</h4>
            <p>Freely draggable or dockable side-by-side with questions. Supports graphing, regression, and equations.</p>
          </div>
        </div>

        <div class="feature-card">
          <div class="feature-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2L1 21h22L12 2zm0 3.45l8.28 14.3H3.72L12 5.45zM11 10h2v4h-2zm0 6h2v2h-2z"/>
            </svg>
          </div>
          <div>
            <h4>Authentic Scoring Scale</h4>
            <p>Exact 44-question to 200–800 conversion scale taken directly from Page 37 of the official test releases.</p>
          </div>
        </div>

        <div class="feature-card">
          <div class="feature-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M3 13h2v-2H3v2zm0 4h2v-2H3v2zm0-8h2V7H3v2zm4 4h14v-2H7v2zm0 4h14v-2H7v2zM7 7v2h14V7H7z"/>
            </svg>
          </div>
          <div>
            <h4>Question Navigator & Tools</h4>
            <p>Tile drawer for instant question jumping, answer strikethrough, review bookmarking, and SPR fraction input.</p>
          </div>
        </div>

        <div class="feature-card">
          <div class="feature-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 3L1 9l4 2.18v6L12 21l7-3.82v-6l2-1.09V17h2V9L12 3zm6.82 6L12 12.72 5.18 9 12 5.28 18.82 9zM17 15.99l-5 2.73-5-2.73v-3.72L12 15l5-2.73v3.72z"/>
            </svg>
          </div>
          <div>
            <h4>Step-by-Step Solutions & Tips</h4>
            <p>Complete step-by-step explanations for all 88 questions with Desmos graphing calculator shortcut strategies.</p>
          </div>
        </div>
      </div>

      <!-- Footer Info -->
      <div style="text-align: center; color: #64748b; font-size: 0.8rem; margin-top: 10px; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 20px;">
        Digital SAT® is a trademark registered by the College Board, which is not affiliated with, and does not endorse, this practice simulation.
      </div>
    </div>
  </div>

  <!-- ========================================================
       ACTIVE EXAM VIEW (Bluebook Test Environment)
       ======================================================== -->
  <div id="exam-view">
    <!-- Top Bluebook Header -->
    <header class="bb-header">
      <div class="header-left">
        <button class="btn-header-home" onclick="returnToHome()" title="Return to Main Menu">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>
          Home
        </button>
        <span class="section-title">Section 2: Math</span>
        <span class="module-badge" id="header-module-badge">Module 1</span>
        <select id="exam-select" class="exam-selector" onchange="switchExam(this.value)" title="Choose SAT Exam Version">
          <option value="v1">September 2026 Exam V1</option>
          <option value="v2">September 2026 Exam V2</option>
        </select>
        <button class="btn-header-link" onclick="openModal('directions-modal')" title="View Section Directions">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>
          Directions
        </button>
      </div>

      <div class="header-center">
        <span class="timer-display" id="timer-display">35:00</span>
        <button class="btn-timer-toggle" id="btn-timer-toggle" onclick="toggleTimerVisibility()">Hide</button>
      </div>

      <div class="header-right">
        <button class="btn-header-tool" id="btn-calculator" onclick="toggleCalculator()" title="Toggle Desmos Calculator">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zM7 10h2v7H7zm4-3h2v10h-2zm4 6h2v4h-2z"/>
          </svg>
          Calculator
        </button>
        <button class="btn-header-tool" onclick="openModal('reference-modal')" title="Official SAT Math Reference Formulas">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>
          </svg>
          Reference
        </button>
        <button class="btn-header-tool" onclick="toggleFullScreen()" title="Toggle Fullscreen Mode">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/>
          </svg>
          Fullscreen
        </button>
      </div>
    </header>

    <!-- Main Container -->
    <div id="app-container">
      <div id="left-pane">
        <!-- Question Scroll Area -->
        <main class="question-scroll-area" id="content-scroll-area">
          <!-- Rendered dynamically by app.js -->
        </main>

        <!-- Bottom Nav Bar -->
        <footer class="bb-footer" id="main-footer">
          <div class="footer-left">
            <span style="font-weight: 600; color: #475467; font-size: 0.9rem;">Section 2: Math</span>
          </div>
          <div class="footer-center">
            <button class="btn-navigator-toggle" id="nav-drawer-toggle" onclick="toggleNavDrawer()">
              <span id="nav-toggle-text">Question 1 of 22</span>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M7 14l5-5 5 5z"/></svg>
            </button>
          </div>
          <div class="footer-right" style="display: flex; gap: 12px;">
            <button class="btn-nav" id="btn-back" onclick="navigateBack()" style="background: #f2f4f7; color: #344054; border: 1px solid #d0d5dd;">Back</button>
            <button class="btn-nav" id="btn-next" onclick="navigateNext()">Next</button>
          </div>
        </footer>

        <!-- Navigator Drawer Popup -->
        <div id="nav-drawer">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #eaecf0;">
            <span style="font-weight: 700; color: #1d2939; font-size: 0.95rem;">Question Navigator</span>
            <button style="background:none; border:none; font-size:1.2rem; cursor:pointer; color:#667085;" onclick="closeNavDrawer()">✕</button>
          </div>
          <div class="nav-grid" id="nav-grid-tiles"></div>
          <div class="nav-legend">
            <div class="legend-item"><span class="legend-dot curr"></span> Current</div>
            <div class="legend-item"><span class="legend-dot ans"></span> Answered</div>
            <div class="legend-item"><span class="legend-dot"></span> Unanswered</div>
            <div class="legend-item"><span class="legend-dot mrk"></span> Marked for Review</div>
          </div>
        </div>
      </div>

      <!-- Docked Calculator Pane -->
      <aside id="dock-pane">
        <div class="desmos-titlebar" style="cursor: default;">
          <div class="desmos-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zM7 10h2v7H7zm4-3h2v10h-2zm4 6h2v4h-2z"/>
            </svg>
            Desmos Graphing Calculator (Docked)
          </div>
          <div class="desmos-controls">
            <button class="desmos-ctrl-btn" onclick="undockCalculator()" title="Float / Undock Window">🗗 Float</button>
            <button class="desmos-ctrl-btn" onclick="toggleCalculator()" title="Close Calculator">✕</button>
          </div>
        </div>
        <div id="desmos-docked-target" style="flex:1; width:100%; height:calc(100% - 36px); overflow:hidden;"></div>
      </aside>
    </div>
  </div> <!-- /#exam-view -->

  <!-- Floating Desmos Window -->
  <div id="desmos-floating-window">
    <div class="desmos-titlebar" id="desmos-drag-bar">
      <div class="desmos-title">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
          <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zM7 10h2v7H7zm4-3h2v10h-2zm4 6h2v4h-2z"/>
        </svg>
        Desmos Graphing Calculator
      </div>
      <div class="desmos-controls">
        <button class="desmos-ctrl-btn" onclick="dockCalculator()" title="Dock to Side">⬌ Dock</button>
        <button class="desmos-ctrl-btn" onclick="toggleCalculator()" title="Close">✕</button>
      </div>
    </div>
    <div id="desmos-calculator-target"></div>
  </div>

  <!-- MODAL: Reference Sheet -->
  <div class="modal-overlay" id="reference-modal" onclick="if(event.target===this)closeModal('reference-modal')">
    <div class="modal-card">
      <div class="modal-header">
        <div class="modal-title">Official SAT Reference Sheet</div>
        <button class="btn-modal-close" onclick="closeModal('reference-modal')">&times;</button>
      </div>
      <div class="modal-body">
        <div class="ref-grid">
          <!-- Circle -->
          <div class="ref-box">
            <h4>Circle</h4>
            <svg viewBox="0 0 100 80">
              <circle cx="50" cy="40" r="32" stroke="#0077c8" stroke-width="2" fill="none"/>
              <line x1="50" y1="40" x2="82" y2="40" stroke="#0077c8" stroke-width="2"/>
              <circle cx="50" cy="40" r="3" fill="#0077c8"/>
              <text x="64" y="34" font-size="12" font-style="italic" fill="#333">r</text>
            </svg>
            <div>$A = \\pi r^2$</div>
            <div>$C = 2\\pi r$</div>
          </div>

          <!-- Rectangle -->
          <div class="ref-box">
            <h4>Rectangle</h4>
            <svg viewBox="0 0 120 80">
              <rect x="20" y="20" width="80" height="40" stroke="#0077c8" stroke-width="2" fill="none"/>
              <text x="56" y="15" font-size="12" font-style="italic" fill="#333">\\ell</text>
              <text x="105" y="44" font-size="12" font-style="italic" fill="#333">w</text>
            </svg>
            <div>$A = \\ell w$</div>
          </div>

          <!-- Triangle -->
          <div class="ref-box">
            <h4>Triangle</h4>
            <svg viewBox="0 0 120 80">
              <polygon points="20,60 100,60 60,15" stroke="#0077c8" stroke-width="2" fill="none"/>
              <line x1="60" y1="15" x2="60" y2="60" stroke="#f04438" stroke-dasharray="3,3" stroke-width="1.5"/>
              <text x="64" y="42" font-size="12" font-style="italic" fill="#f04438">h</text>
              <text x="56" y="74" font-size="12" font-style="italic" fill="#333">b</text>
            </svg>
            <div>$A = \\frac{{1}}{{2}} b h$</div>
          </div>

          <!-- Right Triangle / Pythagorean -->
          <div class="ref-box">
            <h4>Right Triangle</h4>
            <svg viewBox="0 0 120 80">
              <polygon points="30,65 95,65 30,15" stroke="#0077c8" stroke-width="2" fill="none"/>
              <rect x="30" y="55" width="10" height="10" stroke="#333" stroke-width="1" fill="none"/>
              <text x="18" y="44" font-size="12" font-style="italic" fill="#333">a</text>
              <text x="58" y="76" font-size="12" font-style="italic" fill="#333">b</text>
              <text x="68" y="36" font-size="12" font-style="italic" fill="#333">c</text>
            </svg>
            <div>$c^2 = a^2 + b^2$</div>
          </div>

          <!-- Special Right Triangle 30-60-90 -->
          <div class="ref-box">
            <h4>Special Right ($30^\\circ-60^\\circ-90^\\circ$)</h4>
            <svg viewBox="0 0 120 80">
              <polygon points="30,65 95,65 30,20" stroke="#0077c8" stroke-width="2" fill="none"/>
              <rect x="30" y="55" width="10" height="10" stroke="#333" stroke-width="1" fill="none"/>
              <text x="36" y="32" font-size="10" fill="#333">30°</text>
              <text x="75" y="60" font-size="10" fill="#333">60°</text>
              <text x="16" y="46" font-size="11" font-style="italic" fill="#333">x</text>
              <text x="50" y="76" font-size="11" font-style="italic" fill="#333">x\\sqrt{{3}}</text>
              <text x="68" y="40" font-size="11" font-style="italic" fill="#333">2x</text>
            </svg>
            <div>$x, x\\sqrt{{3}}, 2x$</div>
          </div>

          <!-- Special Right Triangle 45-45-90 -->
          <div class="ref-box">
            <h4>Special Right ($45^\\circ-45^\\circ-90^\\circ$)</h4>
            <svg viewBox="0 0 120 80">
              <polygon points="30,65 80,65 30,15" stroke="#0077c8" stroke-width="2" fill="none"/>
              <rect x="30" y="55" width="10" height="10" stroke="#333" stroke-width="1" fill="none"/>
              <text x="36" y="32" font-size="10" fill="#333">45°</text>
              <text x="64" y="60" font-size="10" fill="#333">45°</text>
              <text x="18" y="44" font-size="11" font-style="italic" fill="#333">s</text>
              <text x="52" y="76" font-size="11" font-style="italic" fill="#333">s</text>
              <text x="60" y="36" font-size="11" font-style="italic" fill="#333">s\\sqrt{{2}}</text>
            </svg>
            <div>$s, s, s\\sqrt{{2}}$</div>
          </div>

          <!-- Rectangular Prism -->
          <div class="ref-box">
            <h4>Rectangular Prism</h4>
            <svg viewBox="0 0 120 80">
              <rect x="25" y="30" width="50" height="35" stroke="#0077c8" stroke-width="1.5" fill="none"/>
              <polygon points="75,30 95,18 95,53 75,65" stroke="#0077c8" stroke-width="1.5" fill="none"/>
              <polygon points="25,30 45,18 95,18 75,30" stroke="#0077c8" stroke-width="1.5" fill="none"/>
              <text x="46" y="74" font-size="11" font-style="italic" fill="#333">\\ell</text>
              <text x="14" y="50" font-size="11" font-style="italic" fill="#333">h</text>
              <text x="88" y="44" font-size="11" font-style="italic" fill="#333">w</text>
            </svg>
            <div>$V = \\ell w h$</div>
          </div>

          <!-- Cylinder -->
          <div class="ref-box">
            <h4>Right Cylinder</h4>
            <svg viewBox="0 0 120 80">
              <ellipse cx="60" cy="20" rx="30" ry="8" stroke="#0077c8" stroke-width="1.5" fill="none"/>
              <ellipse cx="60" cy="60" rx="30" ry="8" stroke="#0077c8" stroke-width="1.5" fill="none"/>
              <line x1="30" y1="20" x2="30" y2="60" stroke="#0077c8" stroke-width="1.5"/>
              <line x1="90" y1="20" x2="90" y2="60" stroke="#0077c8" stroke-width="1.5"/>
              <line x1="60" y1="20" x2="90" y2="20" stroke="#0077c8" stroke-width="1.5"/>
              <text x="72" y="16" font-size="11" font-style="italic" fill="#333">r</text>
              <text x="96" y="44" font-size="11" font-style="italic" fill="#333">h</text>
            </svg>
            <div>$V = \\pi r^2 h$</div>
          </div>

          <!-- Sphere -->
          <div class="ref-box">
            <h4>Sphere</h4>
            <svg viewBox="0 0 120 80">
              <circle cx="60" cy="40" r="28" stroke="#0077c8" stroke-width="1.5" fill="none"/>
              <ellipse cx="60" cy="40" rx="28" ry="8" stroke="#0077c8" stroke-dasharray="3,3" stroke-width="1" fill="none"/>
              <line x1="60" y1="40" x2="88" y2="40" stroke="#0077c8" stroke-width="1.5"/>
              <text x="72" y="36" font-size="11" font-style="italic" fill="#333">r</text>
            </svg>
            <div>$V = \\frac{{4}}{{3}} \\pi r^3$</div>
          </div>

          <!-- Cone -->
          <div class="ref-box">
            <h4>Right Cone</h4>
            <svg viewBox="0 0 120 80">
              <ellipse cx="60" cy="62" rx="30" ry="7" stroke="#0077c8" stroke-width="1.5" fill="none"/>
              <line x1="30" y1="62" x2="60" y2="15" stroke="#0077c8" stroke-width="1.5"/>
              <line x1="90" y1="62" x2="60" y2="15" stroke="#0077c8" stroke-width="1.5"/>
              <line x1="60" y1="15" x2="60" y2="62" stroke="#f04438" stroke-dasharray="3,3" stroke-width="1.2"/>
              <line x1="60" y1="62" x2="90" y2="62" stroke="#0077c8" stroke-width="1.2"/>
              <text x="72" y="58" font-size="11" font-style="italic" fill="#333">r</text>
              <text x="64" y="38" font-size="11" font-style="italic" fill="#f04438">h</text>
            </svg>
            <div>$V = \\frac{{1}}{{3}} \\pi r^2 h$</div>
          </div>

          <!-- Pyramid -->
          <div class="ref-box">
            <h4>Right Pyramid</h4>
            <svg viewBox="0 0 120 80">
              <polygon points="30,60 80,65 100,52 60,15" stroke="#0077c8" stroke-width="1.5" fill="none"/>
              <line x1="30" y1="60" x2="60" y2="15" stroke="#0077c8" stroke-width="1.5"/>
              <line x1="80" y1="65" x2="60" y2="15" stroke="#0077c8" stroke-width="1.5"/>
              <line x1="60" y1="15" x2="60" y2="58" stroke="#f04438" stroke-dasharray="3,3" stroke-width="1.2"/>
              <text x="50" y="71" font-size="11" font-style="italic" fill="#333">\\ell</text>
              <text x="92" y="62" font-size="11" font-style="italic" fill="#333">w</text>
              <text x="64" y="38" font-size="11" font-style="italic" fill="#f04438">h</text>
            </svg>
            <div>$V = \\frac{{1}}{{3}} \\ell w h$</div>
          </div>
        </div>

        <div style="background: #f8f9fa; border: 1px solid #e4e7ec; border-radius: 8px; padding: 14px; margin-top: 14px; font-size: 0.9rem; line-height: 1.6;">
          <strong>Additional Circle & Angle Properties:</strong>
          <ul style="padding-left: 20px; margin-top: 6px;">
            <li>The number of degrees of arc in a circle is $360$.</li>
            <li>The number of radians of arc in a circle is $2\\pi$.</li>
            <li>The sum of the measures in degrees of the angles of a triangle is $180$.</li>
          </ul>
        </div>

        <div style="text-align: right; margin-top: 16px;">
          <button class="btn-nav" onclick="closeModal('reference-modal')">Close</button>
        </div>
      </div>
    </div>
  </div>

  <!-- MODAL: Student-Produced Response Help -->
  <div class="modal-overlay" id="spr-modal" onclick="if(event.target===this)closeModal('spr-modal')">
    <div class="modal-card">
      <div class="modal-header">
        <div class="modal-title">Student-Produced Response Instructions</div>
        <button class="btn-modal-close" onclick="closeModal('spr-modal')">&times;</button>
      </div>
      <div class="modal-body">
        <ul style="padding-left: 20px; margin-bottom: 16px; line-height: 1.8;">
          <li>For student-produced response questions, solve each problem and enter your answer in the box provided.</li>
          <li>If your answer is a fraction that doesn't fit in the provided space, enter the decimal equivalent.</li>
          <li>If your answer is a decimal that doesn't fit in the space, enter the rounded or truncated decimal to the maximum number of digits allowed.</li>
          <li>If a question has multiple correct answers, enter only one answer.</li>
          <li>You may enter negative numbers (using <code>-</code>) and fractions (using <code>/</code>).</li>
          <li>Do not enter symbols such as <code>$</code>, <code>%</code>, or commas.</li>
        </ul>
        <div style="text-align: right; margin-top: 16px;">
          <button class="btn-nav" onclick="closeModal('spr-modal')">Got It</button>
        </div>
      </div>
    </div>
  </div>

  <!-- MODAL: Math Section Directions -->
  <div class="modal-overlay" id="directions-modal" onclick="if(event.target===this)closeModal('directions-modal')">
    <div class="modal-card">
      <div class="modal-header">
        <div class="modal-title">Section 2: Math Directions</div>
        <button class="btn-modal-close" onclick="closeModal('directions-modal')">&times;</button>
      </div>
      <div class="modal-body">
        <ul style="padding-left: 20px; margin-bottom: 16px; line-height: 1.8;">
          <li>The questions in this section address a number of important math skills.</li>
          <li><strong>Use of a calculator is permitted for all questions.</strong> The official embedded Desmos graphing calculator is available in the top toolbar.</li>
          <li>Unless a question indicates otherwise, you may assume that:
            <ul>
              <li>All variables and expressions represent real numbers.</li>
              <li>Figures provided with questions are drawn to scale unless otherwise stated.</li>
              <li>All figures lie in a plane.</li>
              <li>The domain of a given function $f$ is the set of all real numbers $x$ for which $f(x)$ is a real number.</li>
            </ul>
          </li>
          <li>For multiple-choice questions, solve each problem and choose the best answer from the choices provided.</li>
          <li>For student-produced response questions, solve each problem and enter your answer into the box provided.</li>
        </ul>
        <div style="text-align: right; margin-top: 16px;">
          <button class="btn-nav" onclick="closeModal('directions-modal')">Close</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Application Data and Script Engine -->
  <script>
    const EXAM_DATABASE = {exam_data_json_str};
  </script>
  <script>
{app_js}
  </script>
</body>
</html>
"""

output_path = os.path.join(BASE_DIR, "SAT_Math_September_2026_Bluebook.html")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_template)

index_path = os.path.join(BASE_DIR, "index.html")
with open(index_path, "w", encoding="utf-8") as f:
    f.write(html_template)

file_size = os.path.getsize(output_path)
print(f"Successfully generated {output_path} and index.html ({file_size:,} bytes)")

# Verification checks
with open(output_path, "r", encoding="utf-8") as f:
    content = f.read()

assert "const EXAM_DATABASE =" in content, "Missing EXAM_DATABASE"
assert "desmos.com/api" in content, "Missing Desmos API script"
assert "katex.min.js" in content, "Missing KaTeX JS"
assert "katex.min.css" in content, "Missing KaTeX CSS"
assert "data:image/png;base64," in content, "Missing base64 figures"
assert content.count("data:image/png;base64,") == 6, f"Expected 6 figures, got {content.count('data:image/png;base64,')}"
assert "v1_m1_q1" in content, "Missing v1_m1_q1"
assert "v1_m2_q22" in content, "Missing v1_m2_q22"
assert "v2_m1_q1" in content, "Missing v2_m1_q1"
assert "v2_m2_q22" in content, "Missing v2_m2_q22"
assert 'id="landing-page"' in content, "Missing landing page"
assert 'id="exam-view"' in content, "Missing exam view"
assert 'id="btn-mode-timed"' in content, "Missing mode selector"
assert 'id="reference-modal"' in content, "Missing reference modal"
assert 'id="desmos-floating-window"' in content, "Missing desmos floating window"
assert 'id="dock-pane"' in content, "Missing dock pane"
assert 'id="nav-drawer"' in content, "Missing nav drawer"
assert 'id="timer-display"' in content, "Missing timer display"
assert 'id="exam-select"' in content, "Missing exam select"

print("All 19 verification checks PASSED successfully!")


