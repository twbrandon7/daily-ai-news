(function () {
  'use strict';

  /* ── 1. Bootstrap guard ──────────────────────────────── */
  var dataEl = document.getElementById('articles-data');
  if (!dataEl) return;

  var articles;
  try { articles = JSON.parse(dataEl.textContent); } catch (e) { return; }
  if (!articles || articles.length === 0) return;

  var cards = Array.prototype.slice.call(
    document.querySelectorAll('.sidebar-article-card[data-article-index]')
  );
  var detailPanel = document.querySelector('.detail-panel');
  if (!detailPanel || cards.length === 0) return;

  var lang = document.documentElement.lang; // "en" or "zh-tw"

  /* ── 2. Helpers ──────────────────────────────────────── */
  function esc(str) {
    return String(str || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  var STAR_FILLED = '<svg class="rating-star rating-star--filled" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2l2.4 7.4H22l-6.2 4.5 2.4 7.4L12 17l-6.2 4.3 2.4-7.4L2 9.4h7.6z"/></svg>';
  var STAR_EMPTY  = '<svg class="rating-star rating-star--empty"  viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M22 9.74l-7.19-.62L12 2.5 9.19 9.13 2 9.74l5.46 4.73-1.64 7.03L12 17.77l6.18 3.73-1.63-7.03L22 9.74zM12 15.9l-3.76 2.27 1-4.28-3.32-2.88 4.38-.38L12 6.8l1.71 4.64 4.38.38-3.32 2.88 1 4.28L12 15.9z"/></svg>';
  var EXTERNAL_ICON = '<svg class="source-link-icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M19 19H5V5h7V3H5a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7h-2v7zM14 3v2h3.59l-9.83 9.83 1.41 1.41L19 6.41V10h2V3h-7z"/></svg>';

  function buildStars(rating) {
    var r = parseInt(rating, 10) || 3;
    var label = lang === 'zh-tw'
      ? '5 顆星中的 ' + r + ' 顆'
      : r + ' out of 5 stars';
    var html = '<div class="rating-stars" aria-label="' + esc(label) + '">';
    for (var i = 1; i <= 5; i++) {
      html += i <= r ? STAR_FILLED : STAR_EMPTY;
    }
    return html + '</div>';
  }

  function buildTagPills(tags, cssClass, style) {
    if (!Array.isArray(tags) || tags.length === 0) return '';
    return tags.map(function (t) {
      return '<span class="tag-pill ' + cssClass + '"' + (style ? ' style="' + style + '"' : '') + '>' + esc(t) + '</span>';
    }).join('');
  }

  function buildInsightsList(items) {
    if (!Array.isArray(items) || items.length === 0) return '';
    return '<ul class="insights-list">' +
      items.map(function (item) {
        return '<li class="insights-item">' + esc(item) + '</li>';
      }).join('') +
    '</ul>';
  }

  /* ── 3. Render article to detail panel ───────────────── */
  function renderArticle(article) {
    var isTw = lang === 'zh-tw';

    // Labels
    var labelProblem   = isTw ? '問題 / 背景' : 'Problem / Why';
    var labelSolution  = isTw ? '解法 / 方法' : 'Solution / How';
    var labelInsights  = isTw ? '洞察與取捨'  : 'Insights & Trade-offs';
    var labelPros      = isTw ? '✓ 優點'      : '✓ Strengths';
    var labelCons      = isTw ? '⚠ 取捨'      : '⚠ Trade-offs';
    var labelTags      = isTw ? '標籤與行動'  : 'Tags & Action';
    var labelLink      = isTw ? '原文連結'    : 'Original Link';
    var srcAriaLabel   = isTw
      ? '原文連結：' + (article.title || '')
      : 'Original Link: ' + (article.title || '');

    var pros = (article.insights_tradeoffs || {}).pros || [];
    var cons = (article.insights_tradeoffs || {}).cons || [];

    var html = '';

    // Article header
    html += '<header class="article-panel-header">';
    html += '<h1 class="article-panel-title text-headline-lg">' + esc(article.title) + '</h1>';
    html += buildStars(article.rating);
    html += '</header>';

    // TL;DR
    html += '<div class="tldr-box">';
    html += '<span class="tldr-label">TL;DR</span>';
    html += '<p class="tldr-text">' + esc(article.tldr) + '</p>';
    html += '</div>';

    // Problem / Why
    html += '<div class="summary-section">';
    html += '<span class="summary-section-label">' + esc(labelProblem) + '</span>';
    html += '<p class="summary-section-body">' + esc(article.problem_why) + '</p>';
    html += '</div>';

    // Solution / How
    html += '<div class="summary-section">';
    html += '<span class="summary-section-label">' + esc(labelSolution) + '</span>';
    html += '<p class="summary-section-body">' + esc(article.solution_how) + '</p>';
    html += '</div>';

    // Insights & Trade-offs
    html += '<div class="insights-section">';
    html += '<span class="insights-section-label">' + esc(labelInsights) + '</span>';
    html += '<div class="insights-grid">';
    html += '<div class="insights-col insights-col--pros">';
    html += '<span class="insights-col-header">' + esc(labelPros) + '</span>';
    html += buildInsightsList(pros);
    html += '</div>';
    html += '<div class="insights-col insights-col--cons">';
    html += '<span class="insights-col-header">' + esc(labelCons) + '</span>';
    html += buildInsightsList(cons);
    html += '</div>';
    html += '</div></div>';

    // Tags & Action
    html += '<div class="tags-action-section">';
    html += '<span class="tags-action-label">' + esc(labelTags) + '</span>';
    html += '<div class="tags-action-list">';
    html += buildTagPills(article.tags_action, 'tag-pill--primary', '');
    html += '</div></div>';

    // Source link (only if url is a safe http/https URL)
    if (article.url && /^https?:\/\//i.test(article.url)) {
      html += '<div class="source-link-row">';
      html += '<a class="source-link" href="' + esc(article.url) + '" target="_blank" rel="noopener noreferrer" aria-label="' + esc(srcAriaLabel) + '">';
      html += EXTERNAL_ICON;
      html += esc(labelLink);
      html += '</a></div>';
    }

    detailPanel.innerHTML = html;
  }

  /* ── 4. Activate card and render ─────────────────────── */
  function activateCard(idx) {
    cards.forEach(function (card) {
      card.classList.remove('active-card-indicator');
      card.setAttribute('aria-selected', 'false');
    });
    var target = document.querySelector('[data-article-index="' + idx + '"]');
    if (target) {
      target.classList.add('active-card-indicator');
      target.setAttribute('aria-selected', 'true');
    }
    if (articles[idx]) renderArticle(articles[idx]);
  }

  /* ── 5. Attach event listeners ───────────────────────── */
  cards.forEach(function (card) {
    card.style.cursor = 'pointer';
    card.addEventListener('click', function () {
      activateCard(parseInt(card.getAttribute('data-article-index'), 10));
    });
    card.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        activateCard(parseInt(card.getAttribute('data-article-index'), 10));
      }
    });
  });

}());
