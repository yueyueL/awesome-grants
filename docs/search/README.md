---
layout: default
title: Search Grants
nav_order: 10
permalink: /docs/search
---

# Search Grants

Search and filter every grant in this list — both the curated dataset and the automatically collected live opportunities — without leaving this page.

<!--
  NOTE: The JSON files under assets/data/ (grants.json, grants_live_master.json)
  are build copies of the canonical files in /data. The /data directory is
  excluded from the Jekyll build, so published copies are served from
  /assets/data/ instead. These copies are refreshed by the scheduled
  data-refresh workflow whenever the source data is regenerated.
-->

<style>
  #grant-search {
    margin-top: 1rem;
  }
  #grant-search .gs-controls {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    align-items: center;
    margin-bottom: 1rem;
  }
  #grant-search input[type="text"],
  #grant-search select {
    padding: 0.4rem 0.6rem;
    border: 1px solid rgba(128, 128, 128, 0.45);
    border-radius: 4px;
    background: transparent;
    color: inherit;
    font: inherit;
    font-size: 0.9rem;
  }
  #grant-search input[type="text"] {
    flex: 1 1 220px;
    min-width: 180px;
  }
  #grant-search select {
    max-width: 100%;
  }
  #grant-search select option {
    color: initial;
  }
  #grant-search .gs-checkbox {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    font-size: 0.9rem;
    white-space: nowrap;
    cursor: pointer;
  }
  #grant-search .gs-count {
    font-size: 0.85rem;
    opacity: 0.75;
    margin-bottom: 0.5rem;
  }
  #grant-search .gs-table-wrap {
    overflow-x: auto;
  }
  #grant-search table.gs-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.85rem;
  }
  #grant-search table.gs-table th,
  #grant-search table.gs-table td {
    text-align: left;
    padding: 0.45rem 0.6rem;
    border-bottom: 1px solid rgba(128, 128, 128, 0.3);
    vertical-align: top;
  }
  #grant-search table.gs-table th {
    border-bottom-width: 2px;
  }
  #grant-search .gs-badge {
    display: inline-block;
    padding: 0.05rem 0.45rem;
    border-radius: 9px;
    font-size: 0.7rem;
    background: rgba(128, 128, 128, 0.18);
    border: 1px solid rgba(128, 128, 128, 0.3);
    white-space: nowrap;
  }
  #grant-search .gs-expired {
    opacity: 0.55;
  }
  #grant-search .gs-expired-label {
    font-size: 0.7rem;
    opacity: 0.8;
  }
  #grant-search button.gs-showall {
    margin-top: 0.75rem;
    padding: 0.4rem 0.9rem;
    border: 1px solid rgba(128, 128, 128, 0.45);
    border-radius: 4px;
    background: rgba(128, 128, 128, 0.12);
    color: inherit;
    font: inherit;
    font-size: 0.85rem;
    cursor: pointer;
  }
  #grant-search button.gs-showall:hover {
    background: rgba(128, 128, 128, 0.25);
  }
  #grant-search .gs-footer {
    margin-top: 1rem;
    font-size: 0.8rem;
    opacity: 0.7;
  }
  #grant-search .gs-error {
    padding: 0.6rem;
    border: 1px solid rgba(200, 80, 80, 0.6);
    border-radius: 4px;
  }
</style>

<div id="grant-search">
  <div class="gs-controls">
    <input type="text" id="gs-query" placeholder="Search name, organization, description&hellip;" aria-label="Search grants" />
    <select id="gs-source" aria-label="Filter by data source">
      <option value="">All sources</option>
      <option value="Curated">Curated</option>
      <option value="Live">Live</option>
    </select>
    <select id="gs-audience" aria-label="Filter by audience">
      <option value="">All audiences</option>
    </select>
    <label class="gs-checkbox">
      <input type="checkbox" id="gs-hide-expired" checked />
      Hide expired deadlines
    </label>
  </div>
  <div class="gs-count" id="gs-count">Loading grant data&hellip;</div>
  <div class="gs-table-wrap">
    <table class="gs-table" id="gs-table" style="display:none">
      <thead>
        <tr>
          <th>Grant</th>
          <th>Organization</th>
          <th>Amount</th>
          <th>Deadline</th>
          <th>Source</th>
        </tr>
      </thead>
      <tbody id="gs-results"></tbody>
    </table>
  </div>
  <button type="button" class="gs-showall" id="gs-showall" style="display:none">Show all results</button>
  <div class="gs-footer" id="gs-footer"></div>
</div>

<script>
(function () {
  'use strict';

  var CURATED_URL = "{{ '/assets/data/grants.json' | relative_url }}";
  var LIVE_URL = "{{ '/assets/data/grants_live_master.json' | relative_url }}";
  var RENDER_CAP = 100;

  var els = {
    query: document.getElementById('gs-query'),
    source: document.getElementById('gs-source'),
    audience: document.getElementById('gs-audience'),
    hideExpired: document.getElementById('gs-hide-expired'),
    count: document.getElementById('gs-count'),
    table: document.getElementById('gs-table'),
    results: document.getElementById('gs-results'),
    showAll: document.getElementById('gs-showall'),
    footer: document.getElementById('gs-footer')
  };

  var allGrants = [];
  var showAllRows = false;

  function normalizeUrl(url) {
    if (!url) return '';
    return String(url)
      .trim()
      .toLowerCase()
      .replace(/^https?:\/\//, '')
      .replace(/^www\./, '')
      .replace(/\/+$/, '');
  }

  // Parse MM/DD/YYYY. Anything else (free text like "October (annually)",
  // "Rolling", or an empty string) returns null and is treated as NOT expired.
  function parseDeadline(s) {
    if (!s) return null;
    var m = /^(\d{1,2})\/(\d{1,2})\/(\d{4})$/.exec(String(s).trim());
    if (!m) return null;
    var month = parseInt(m[1], 10);
    var day = parseInt(m[2], 10);
    var year = parseInt(m[3], 10);
    if (month < 1 || month > 12 || day < 1 || day > 31) return null;
    var d = new Date(year, month - 1, day, 23, 59, 59);
    return isNaN(d.getTime()) ? null : d;
  }

  function isExpired(grant) {
    var d = parseDeadline(grant.deadline);
    if (!d) return false;
    return d.getTime() < Date.now();
  }

  function toRecord(raw, sourceTag) {
    return {
      name: raw.name || '',
      organization: raw.organization || '',
      url: raw.url || '',
      amount: raw.amount || '',
      deadline: raw.deadline || '',
      description: raw.description || '',
      audience: Array.isArray(raw.audience) ? raw.audience : [],
      sourceTag: sourceTag,
      haystack: ((raw.name || '') + ' ' + (raw.organization || '') + ' ' +
                 (raw.description || '')).toLowerCase()
    };
  }

  function mergeDatasets(curated, live) {
    var merged = [];
    var seen = Object.create(null);
    // Curated first: richer records win on duplicate URLs.
    curated.forEach(function (g) {
      var key = normalizeUrl(g.url) || ('curated:' + g.name);
      if (seen[key]) return;
      seen[key] = true;
      merged.push(toRecord(g, 'Curated'));
    });
    live.forEach(function (g) {
      var key = normalizeUrl(g.url) || ('live:' + g.name);
      if (seen[key]) return;
      seen[key] = true;
      merged.push(toRecord(g, 'Live'));
    });
    return merged;
  }

  function populateAudiences(grants) {
    var audiences = Object.create(null);
    grants.forEach(function (g) {
      g.audience.forEach(function (a) { audiences[a] = true; });
    });
    Object.keys(audiences).sort().forEach(function (a) {
      var opt = document.createElement('option');
      opt.value = a;
      opt.textContent = a;
      els.audience.appendChild(opt);
    });
  }

  function currentMatches() {
    var q = els.query.value.trim().toLowerCase();
    var source = els.source.value;
    var audience = els.audience.value;
    var hideExpired = els.hideExpired.checked;
    return allGrants.filter(function (g) {
      if (q && g.haystack.indexOf(q) === -1) return false;
      if (source && g.sourceTag !== source) return false;
      if (audience && g.audience.length && g.audience.indexOf(audience) === -1) return false;
      if (hideExpired && isExpired(g)) return false;
      return true;
    });
  }

  function makeCell(text) {
    var td = document.createElement('td');
    td.textContent = text || '—';
    return td;
  }

  function render() {
    var matches = currentMatches();
    els.results.textContent = '';
    var limit = showAllRows ? matches.length : Math.min(matches.length, RENDER_CAP);

    for (var i = 0; i < limit; i++) {
      var g = matches[i];
      var tr = document.createElement('tr');
      var expired = isExpired(g);
      if (expired) tr.className = 'gs-expired';

      var nameTd = document.createElement('td');
      if (g.url) {
        var a = document.createElement('a');
        a.href = g.url;
        a.target = '_blank';
        a.rel = 'noopener';
        a.textContent = g.name;
        a.title = g.description;
        nameTd.appendChild(a);
      } else {
        nameTd.textContent = g.name;
      }
      tr.appendChild(nameTd);
      tr.appendChild(makeCell(g.organization));
      tr.appendChild(makeCell(g.amount));

      var deadlineTd = makeCell(g.deadline);
      if (expired) {
        deadlineTd.appendChild(document.createTextNode(' '));
        var lbl = document.createElement('span');
        lbl.className = 'gs-expired-label';
        lbl.textContent = '(expired)';
        deadlineTd.appendChild(lbl);
      }
      tr.appendChild(deadlineTd);

      var srcTd = document.createElement('td');
      var badge = document.createElement('span');
      badge.className = 'gs-badge';
      badge.textContent = g.sourceTag;
      srcTd.appendChild(badge);
      tr.appendChild(srcTd);

      els.results.appendChild(tr);
    }

    els.table.style.display = matches.length ? '' : 'none';
    els.count.textContent = matches.length === 0
      ? 'No grants match your filters.'
      : (limit < matches.length
          ? 'Showing ' + limit + ' of ' + matches.length + ' matching grants (of ' + allGrants.length + ' total).'
          : matches.length + ' matching grant' + (matches.length === 1 ? '' : 's') + ' (of ' + allGrants.length + ' total).');
    els.showAll.style.display = limit < matches.length ? '' : 'none';
  }

  function onFilterChange() {
    showAllRows = false;
    render();
  }

  function fetchJson(url) {
    return fetch(url).then(function (resp) {
      if (!resp.ok) throw new Error('HTTP ' + resp.status + ' for ' + url);
      return resp.json();
    });
  }

  Promise.all([fetchJson(CURATED_URL), fetchJson(LIVE_URL)])
    .then(function (data) {
      var curated = (data[0] && data[0].grants) || [];
      var liveData = data[1] || {};
      var live = liveData.grants || [];

      allGrants = mergeDatasets(curated, live);
      populateAudiences(allGrants);

      var info = liveData.collection_info || {};
      if (info.scraped_at) {
        var datePart = String(info.scraped_at).split('T')[0];
        els.footer.textContent = 'Live data last collected: ' + datePart;
      }

      els.query.addEventListener('input', onFilterChange);
      els.source.addEventListener('change', onFilterChange);
      els.audience.addEventListener('change', onFilterChange);
      els.hideExpired.addEventListener('change', onFilterChange);
      els.showAll.addEventListener('click', function () {
        showAllRows = true;
        render();
      });

      render();
    })
    .catch(function (err) {
      els.count.className = 'gs-error';
      els.count.textContent = 'Could not load grant data (' + err.message +
        '). Please refresh the page or browse the category pages instead.';
    });
})();
</script>
