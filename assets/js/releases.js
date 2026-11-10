(() => {
  'use strict';
  const configElement = document.getElementById('release-live-config');
  const updated = document.getElementById('release-updated');
  const status = document.getElementById('release-refresh-status');
  if (!configElement || !updated || !status) return;
  const config = JSON.parse(configElement.textContent);
  const format = new Intl.NumberFormat('en-US');
  const dateFormat = new Intl.DateTimeFormat('en-GB', {day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit', timeZone: 'Europe/Paris'});
  const initialDate = new Date(updated.dateTime);
  if (!Number.isNaN(initialDate.getTime())) updated.textContent = dateFormat.format(initialDate);
  let running = false;

  async function readEndpoint(endpoint, signal) {
    const rows = [];
    const seen = new Set();
    let url = endpoint.url;
    while (url) {
      if (seen.has(url) || new URL(url).origin !== 'https://huggingface.co') throw new Error('Invalid pagination');
      seen.add(url);
      const response = await fetch(url, {signal, credentials: 'omit', cache: 'no-store'});
      if (!response.ok) throw new Error('Statistics are unavailable');
      const data = await response.json();
      if (!Array.isArray(data)) throw new Error('Unexpected response');
      rows.push(...data.map(item => ({...item, kind: endpoint.kind})));
      const next = (response.headers.get('Link') || '').match(/<([^>]+)>;\s*rel="next"/);
      url = next ? next[1] : null;
    }
    return rows;
  }

  async function refresh() {
    if (running) return;
    running = true;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 15000);
    try {
      const pages = await Promise.all(config.endpoints.map(endpoint => readEndpoint(endpoint, controller.signal)));
      const rows = new Map(pages.flat().map(item => [item.kind + ':' + item.id, item]));
      // Validate the whole selected inventory before replacing any saved values.
      config.resources.forEach(key => {
        const row = rows.get(key);
        if (!row || !Number.isInteger(row.downloads) || row.downloads < 0 || !Number.isInteger(row.downloadsAllTime) || row.downloadsAllTime < 0) throw new Error('Incomplete metrics');
      });
      const totals = {};
      Object.entries(config.aggregates).forEach(([id, keys]) => {
        totals[id] = keys.reduce((sum, key) => {
          const row = rows.get(key);
          sum.month += row.downloads;
          sum.allTime += row.downloadsAllTime;
          return sum;
        }, {month: 0, allTime: 0});
      });
      document.querySelectorAll('[data-aggregate-month]').forEach(element => element.textContent = format.format(totals[element.dataset.aggregateMonth].month));
      document.querySelectorAll('[data-aggregate-all-time]').forEach(element => {
        const count = totals[element.dataset.aggregateAllTime].allTime;
        element.textContent = format.format(count);
      });
      const now = new Date();
      updated.dateTime = now.toISOString();
      updated.textContent = dateFormat.format(now);
      status.textContent = 'Download statistics updated from Hugging Face.';
    } catch (_) {
      status.textContent = 'Showing the last saved statistics. Statistics will update automatically when available.';
    } finally {
      clearTimeout(timeout);
      running = false;
    }
  }

  refresh();
  setInterval(() => { if (document.visibilityState === 'visible') refresh(); }, 5 * 60 * 1000);
})();
