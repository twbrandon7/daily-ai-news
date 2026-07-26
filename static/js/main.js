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
  if (cards.length === 0) return;

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

  var detailCards = Array.prototype.slice.call(
    document.querySelectorAll('[data-article-detail-index]')
  );

  /* ── 2. Filter sidebar articles ──────────────────────── */
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

  /* ── 3. Activate card and switch detail view ─────────── */
  function activateCard(idx) {
    cards.forEach(function (card) {
      card.classList.remove('active-card-indicator');
      card.setAttribute('aria-selected', 'false');
    });

    var targetCard = document.querySelector('.sidebar-article-card[data-article-index="' + idx + '"]');
    if (targetCard) {
      targetCard.classList.add('active-card-indicator');
      targetCard.setAttribute('aria-selected', 'true');
    }

    detailCards.forEach(function (card) {
      var cardIdx = parseInt(card.getAttribute('data-article-detail-index'), 10);
      if (cardIdx === idx) {
        card.classList.add('is-visible');
      } else {
        card.classList.remove('is-visible');
      }
    });

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
        if (!isNaN(parsed) && parsed >= 0 && parsed < articles.length) {
          savedIdx = parsed;
        }
      }
    } catch (e) {}
    activateCard(savedIdx);
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
