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

  // ── localStorage key for article index ──
  var dateMatch  = window.location.pathname.match(/\/posts\/(\d{4}-\d{2}-\d{2})\//);
  var storageKey = 'articleIdx_' + (dateMatch ? dateMatch[1] : 'default');

  // ── Search / filter state ──
  var activeSearchQuery = '';
  var activeTagFilter   = '';

  // ── Additional DOM refs ──
  var searchInput = document.querySelector('.sidebar-search-input');
  var tagPills    = Array.prototype.slice.call(document.querySelectorAll('.tag-pill--filter'));
  var emptyState  = document.getElementById('sidebar-no-results');
  var resetBtn    = document.getElementById('sidebar-reset-search');

  /* ── 2. Helpers ──────────────────────────────────────── */
  function esc(str) {
    return String(str || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function buildStars(rating) {
    var r = parseInt(rating, 10) || 3;
    var html = '<div class="flex items-center gap-xs">';
    for (var i = 1; i <= 5; i++) {
      if (i <= r) {
        html += '<span class="material-symbols-outlined text-primary" style="font-variation-settings: \'FILL\' 1;">star</span>';
      } else {
        html += '<span class="material-symbols-outlined text-outline-variant">star</span>';
      }
    }
    html += '<span class="font-label-md text-label-md ml-xs text-on-surface">' + r.toFixed(1) + '</span>';
    return html + '</div>';
  }

  function buildInsightsList(items) {
    if (!Array.isArray(items) || items.length === 0) return '';
    return '<ul class="list-disc list-inside text-body-md space-y-1">' +
      items.map(function (item) {
        return '<li>' + esc(item) + '</li>';
      }).join('') +
    '</ul>';
  }

  /* ── 3. Filter sidebar articles ──────────────────────── */
  function filterArticles() {
    var query = activeSearchQuery.toLowerCase().trim();
    var tag   = activeTagFilter.toLowerCase().trim();
    var count = 0;

    cards.forEach(function (card) {
      var idx = parseInt(card.getAttribute('data-article-index'), 10);
      var art = articles[idx];
      if (!art) { card.style.display = 'none'; return; }

      var title   = String(art.title || '').toLowerCase();
      var tagList = Array.isArray(art.tags_action)
        ? art.tags_action.filter(function (t) { return typeof t === 'string'; })
        : [];
      var inTitle  = !query || title.indexOf(query) !== -1;
      var inTags   = !query || tagList.some(function (t) { return t.toLowerCase().indexOf(query) !== -1; });
      var tagMatch = !tag   || tagList.some(function (t) { return t.toLowerCase() === tag; });

      var show = (inTitle || inTags) && tagMatch;
      card.style.display = show ? '' : 'none';
      if (show) count++;
    });

    if (emptyState) emptyState.style.display = count === 0 ? '' : 'none';
  }

  /* ── 4. Render article to detail panel ───────────────── */
  function renderArticle(article) {
    var isTw = lang === 'zh-tw';

    var labelProblem  = isTw ? '痛點與背景 (Problem / Why)' : 'Problem / Why';
    var labelSolution = isTw ? '解法與核心機制 (Solution / How)' : 'Solution / How';
    var labelInsights = isTw ? '關鍵數據或權衡 (Insights & Trade-offs)' : 'Insights & Trade-offs';
    var labelPros     = isTw ? '優點 (Pros)' : 'Pros';
    var labelCons     = isTw ? '缺點 (Cons)' : 'Cons';
    var labelTags     = isTw ? '標籤與實用價值 (Tags & Action)' : 'Tags & Action';
    var labelLink     = isTw ? '原文連結' : 'Original Link';
    var labelElements = isTw ? '📋 技術摘要的 5 大核心要素' : '📋 5 Core Elements of Technical Summary';
    var labelReadTime = isTw ? '閱讀時間：約 4 分鐘' : 'Read time: ~4 mins';
    var labelTldr     = isTw ? '1. 一句話結論 (TL;DR)' : '1. TL;DR';

    var pros = (article.insights_tradeoffs || {}).pros || [];
    var cons = (article.insights_tradeoffs || {}).cons || [];

    var html = '';

    // Summary Header
    html += '<div class="p-lg border-b border-outline-variant bg-surface-bright">';
    html += '<div class="flex items-center gap-sm mb-md">';
    html += '<span class="bg-primary text-white text-[10px] font-bold px-2 py-0.5 rounded uppercase">Deep Dive</span>';
    html += '<span class="text-outline text-label-sm">' + esc(labelReadTime) + '</span>';
    html += '</div>';
    html += '<h1 class="font-headline-xl text-headline-xl mb-md">' + esc(article.title) + '</h1>';
    html += '<div class="flex items-center gap-md">';
    html += buildStars(article.rating);
    html += '<div class="h-4 w-px bg-outline-variant"></div>';
    html += '<span class="font-label-md text-label-md text-on-surface-variant">';
    html += isTw ? '發布日期：2024年10月' : 'Published: Oct 2024';
    html += '</span>';
    html += '</div>';
    html += '</div>';

    // 5 Core Elements Detail
    html += '<div class="p-lg space-y-lg">';
    html += '<div class="flex items-center gap-sm text-primary">';
    html += '<span class="material-symbols-outlined">analytics</span>';
    html += '<h3 class="font-headline-md text-headline-md font-bold">' + esc(labelElements) + '</h3>';
    html += '</div>';

    // 1. TL;DR
    html += '<div class="p-md rounded-lg bg-surface-container-low border-l-4 border-primary">';
    html += '<div class="font-label-md text-label-md text-primary mb-xs">' + esc(labelTldr) + '</div>';
    html += '<p class="font-body-lg text-body-lg font-semibold">' + esc(article.tldr) + '</p>';
    html += '</div>';

    // 2. Problem & 3. Solution
    html += '<div class="grid grid-cols-1 md:grid-cols-2 gap-lg">';
    html += '<div class="space-y-sm">';
    html += '<div class="font-label-md text-label-md text-outline">2. ' + esc(labelProblem) + '</div>';
    html += '<div class="technical-card p-md rounded-lg border-dashed">';
    html += '<p class="font-body-md text-body-md text-on-surface-variant">' + esc(article.problem_why) + '</p>';
    html += '</div>';
    html += '</div>';
    html += '<div class="space-y-sm">';
    html += '<div class="font-label-md text-label-md text-outline">3. ' + esc(labelSolution) + '</div>';
    html += '<div class="technical-card p-md rounded-lg border-dashed">';
    html += '<p class="font-body-md text-body-md text-on-surface-variant">' + esc(article.solution_how) + '</p>';
    html += '</div>';
    html += '</div>';
    html += '</div>';

    // 4. Insights & Trade-offs
    html += '<div class="space-y-sm">';
    html += '<div class="font-label-md text-label-md text-outline">4. ' + esc(labelInsights) + '</div>';
    html += '<div class="grid grid-cols-1 md:grid-cols-2 gap-md">';
    html += '<div class="p-md rounded-lg bg-green-50/50 border border-green-100">';
    html += '<div class="flex items-center gap-xs text-green-700 font-bold mb-xs text-label-md">';
    html += '<span class="material-symbols-outlined text-[16px]">add_circle</span> ' + esc(labelPros);
    html += '</div>';
    html += '<div class="text-green-800">' + buildInsightsList(pros) + '</div>';
    html += '</div>';
    html += '<div class="p-md rounded-lg bg-red-50/50 border border-red-100">';
    html += '<div class="flex items-center gap-xs text-red-700 font-bold mb-xs text-label-md">';
    html += '<span class="material-symbols-outlined text-[16px]">remove_circle</span> ' + esc(labelCons);
    html += '</div>';
    html += '<div class="text-red-800">' + buildInsightsList(cons) + '</div>';
    html += '</div>';
    html += '</div>';
    html += '</div>';

    // 5. Tags & Action
    html += '<div class="pt-md border-t border-outline-variant flex flex-col md:flex-row justify-between items-start md:items-center gap-md">';
    html += '<div class="space-y-sm">';
    html += '<div class="font-label-md text-label-md text-outline">5. ' + esc(labelTags) + '</div>';
    html += '<div class="flex flex-wrap gap-sm">';
    if (Array.isArray(article.tags_action)) {
      article.tags_action.forEach(function (tag) {
        html += '<span class="px-3 py-1 rounded-full bg-surface-container-high text-primary font-bold text-label-sm border border-outline-variant">#' + esc(tag) + '</span>';
      });
    }
    html += '</div>';
    html += '</div>';

    if (article.url && /^https?:\/\//i.test(article.url)) {
      html += '<div class="flex gap-sm">';
      html += '<a href="' + esc(article.url) + '" target="_blank" rel="noopener noreferrer" class="px-lg py-2 bg-primary text-white font-bold rounded-lg hover:bg-surface-tint transition-colors flex items-center gap-sm">';
      html += '<span class="material-symbols-outlined text-[18px]">share</span>' + esc(labelLink);
      html += '</a>';
      html += '</div>';
    }
    html += '</div>';

    html += '</div>';

    detailPanel.innerHTML = html;
  }

  /* ── 5. Activate card and render ─────────────────────── */
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
    try { localStorage.setItem(storageKey, idx); } catch (e) {}
  }

  /* ── 6. Attach event listeners ───────────────────────── */
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

  /* ── 7. Restore saved article on language switch ─────── */
  (function () {
    var savedIdx = 0;
    try {
      var saved = localStorage.getItem(storageKey);
      if (saved !== null) {
        var parsed = parseInt(saved, 10);
        if (!isNaN(parsed) && parsed > 0 && parsed < articles.length) {
          savedIdx = parsed;
        }
      }
    } catch (e) {}
    if (savedIdx > 0) activateCard(savedIdx);
  }());

  /* ── 8. Search input ─────────────────────────────────── */
  if (searchInput) {
    searchInput.addEventListener('input', function () {
      activeSearchQuery = searchInput.value;
      filterArticles();
    });
  }

  /* ── 9. Tag pill filter ──────────────────────────────── */
  tagPills.forEach(function (pill) {
    pill.style.cursor = 'pointer';
    function toggleTag() {
      var tag = (pill.getAttribute('data-filter-tag') || '').toLowerCase();
      if (!tag) {
        activeTagFilter = '';
        tagPills.forEach(function (p) {
          var isAll = !(p.getAttribute('data-filter-tag') || '');
          p.classList.toggle('tag-pill--filter-active', isAll);
          p.classList.toggle('bg-primary', isAll);
          p.classList.toggle('text-white', isAll);
          p.classList.toggle('bg-surface-container-high', !isAll);
          p.classList.toggle('text-on-surface-variant', !isAll);
          p.setAttribute('aria-pressed', isAll ? 'true' : 'false');
        });
      } else if (activeTagFilter === tag) {
        activeTagFilter = '';
        tagPills.forEach(function (p) {
          var isAll = !(p.getAttribute('data-filter-tag') || '');
          p.classList.toggle('tag-pill--filter-active', isAll);
          p.classList.toggle('bg-primary', isAll);
          p.classList.toggle('text-white', isAll);
          p.classList.toggle('bg-surface-container-high', !isAll);
          p.classList.toggle('text-on-surface-variant', !isAll);
          p.setAttribute('aria-pressed', isAll ? 'true' : 'false');
        });
      } else {
        activeTagFilter = tag;
        tagPills.forEach(function (p) {
          var pTag = (p.getAttribute('data-filter-tag') || '').toLowerCase();
          var active = pTag === tag;
          p.classList.toggle('tag-pill--filter-active', active);
          p.classList.toggle('bg-primary', active);
          p.classList.toggle('text-white', active);
          p.classList.toggle('bg-surface-container-high', !active);
          p.classList.toggle('text-on-surface-variant', !active);
          p.setAttribute('aria-pressed', active ? 'true' : 'false');
        });
      }
      filterArticles();
    }
    pill.addEventListener('click', toggleTag);
    pill.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggleTag(); }
    });
  });

  /* ── 10. Reset search / filter ───────────────────────── */
  if (resetBtn) {
    resetBtn.addEventListener('click', function () {
      activeSearchQuery = '';
      activeTagFilter   = '';
      if (searchInput) searchInput.value = '';
      tagPills.forEach(function (p) {
        var isAll = !(p.getAttribute('data-filter-tag') || '');
        p.classList.toggle('tag-pill--filter-active', isAll);
        p.classList.toggle('bg-primary', isAll);
        p.classList.toggle('text-white', isAll);
        p.classList.toggle('bg-surface-container-high', !isAll);
        p.classList.toggle('text-on-surface-variant', !isAll);
        p.setAttribute('aria-pressed', isAll ? 'true' : 'false');
      });
      filterArticles();
    });
  }

}());
