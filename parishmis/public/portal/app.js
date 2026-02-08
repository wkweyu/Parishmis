(function () {
  const selectors = {
    greeting: '[data-greeting]',
    syncLabel: '[data-sync-label]',
    parishChip: '[data-parish-chip]',
    sccChip: '[data-scc-chip]',
    contributionTotal: '[data-contribution-total]',
    contributionsList: '[data-recent-contributions]',
    sacramentsList: '[data-recent-sacraments]',
    announcementsList: '[data-recent-announcements]',
    activitiesList: '[data-upcoming-activities]',
    familyBody: '[data-family-body]'
  };

  const state = {
    bootstrap: null,
    collectionTypes: [],
    activeSheet: null,
    profile: null
  };

  const fmtDateTime = (value) => {
    if (!value) return '—';
    try {
      return new Intl.DateTimeFormat('en-KE', {
        dateStyle: 'medium',
        timeStyle: 'short'
      }).format(new Date(value));
    } catch (error) {
      return value;
    }
  };

  const fmtDate = (value) => {
    if (!value) return '—';
    try {
      return new Intl.DateTimeFormat('en-KE', { dateStyle: 'medium' }).format(new Date(value));
    } catch (error) {
      return value;
    }
  };

  const fmtCurrency = (value) => {
    const amount = Number(value || 0);
    return new Intl.NumberFormat('en-KE', { style: 'currency', currency: 'KES', maximumFractionDigits: 0 }).format(amount);
  };

  const plainText = (value) => {
    if (!value) return '';
    const element = document.createElement('div');
    element.innerHTML = value;
    return element.textContent || element.innerText || '';
  };

  const setText = (selector, text) => {
    const el = document.querySelector(selector);
    if (el) el.textContent = text;
  };

  async function fetchJSON(method, options = {}) {
    const response = await fetch(`/api/method/${method}`, {
      method: options.method || 'GET',
      headers: Object.assign({
        'Content-Type': 'application/json',
        'X-Frappe-CSRF-Token': window.portalBootstrap?.csrfToken
      }, options.headers || {}),
      body: options.body ? JSON.stringify(options.body) : undefined,
      credentials: 'include'
    });

    const data = await response.json();
    if (!response.ok || data.exc) {
      throw new Error(data.exc || data._server_messages || 'Unexpected server response');
    }
    return data.message || data;
  }

  function renderProfile(payload) {
    const info = payload?.parishioner || {};
    state.profile = payload;
    setText(selectors.greeting, `Hello ${info.first_name || info.full_name || 'friend'}`);
    setText(selectors.parishChip, info.parish_name || info.parish || '—');
    setText(selectors.sccChip, info.scc_name || info.scc || '—');
    renderFamily(payload);
  }

  function renderFamily(payload) {
    const body = document.querySelector(selectors.familyBody);
    if (!body) return;
    const info = payload?.parishioner || {};
    const family = payload?.family;
    const memberships = payload?.scc_memberships || [];
    const membershipMarkup = memberships.length
      ? `<ul class="space-y-2">
          ${memberships
            .map(
              (item) => `
                <li class="rounded-2xl border border-slate-200 px-3 py-2">
                  <div class="flex items-center justify-between">
                    <div>
                      <p class="font-semibold">${item.scc_name || item.scc}</p>
                      <p class="text-xs text-slate-500">${item.role || 'Member'}</p>
                    </div>
                    <p class="text-xs text-slate-400">Since ${fmtDate(item.join_date)}</p>
                  </div>
                </li>`
            )
            .join('')}
        </ul>`
      : '<p class="text-slate-500">No SCC membership recorded.</p>';

    body.innerHTML = `
      <div>
        <p class="text-xs uppercase tracking-[0.3em] text-slate-500">Phone</p>
        <p class="text-base font-semibold">${info.phone_number || '—'}</p>
      </div>
      <div>
        <p class="text-xs uppercase tracking-[0.3em] text-slate-500">Email</p>
        <p class="text-base font-semibold">${info.email || '—'}</p>
      </div>
      <div>
        <p class="text-xs uppercase tracking-[0.3em] text-slate-500">Address</p>
        <p class="text-base font-semibold">${info.address || family?.address || '—'}</p>
      </div>
      <div>
        <p class="text-xs uppercase tracking-[0.3em] text-slate-500">Family</p>
        <p class="text-base font-semibold">${family?.family_name || info.family_name || info.family || '—'}</p>
        ${family?.phone_number ? `<p class="text-sm text-slate-500">${family.phone_number}</p>` : ''}
      </div>
      <div>
        <p class="text-xs uppercase tracking-[0.3em] text-slate-500">SCC Memberships</p>
        ${membershipMarkup}
      </div>
    `;
  }

  function renderContributions(payload) {
    const container = document.querySelector(selectors.contributionsList);
    if (!container) return;
    const rows = payload?.entries?.slice(0, 3) || [];
    setText(selectors.contributionTotal, fmtCurrency(payload?.summary?.total_amount));
    if (!rows.length) {
      container.innerHTML = '<p class="text-sm text-slate-400">No contributions recorded.</p>';
      return;
    }
    container.innerHTML = rows
      .map(
        (row) => `
          <div class="flex items-center justify-between rounded-2xl bg-slate-900/40 px-4 py-3">
            <div>
              <p class="text-sm font-semibold">${row.collection_type}</p>
              <p class="text-xs text-slate-400">${fmtDate(row.date)} · ${row.payment_method}</p>
            </div>
            <p class="text-base font-display">${fmtCurrency(row.amount)}</p>
          </div>`
      )
      .join('');
  }

  function renderSacraments(records) {
    const container = document.querySelector(selectors.sacramentsList);
    if (!container) return;
    if (!records?.length) {
      container.innerHTML = '<p class="text-sm text-slate-400">No sacrament records yet.</p>';
      return;
    }
    container.innerHTML = records.slice(0, 3)
      .map(
        (row) => `
          <div class="rounded-2xl bg-slate-900/40 px-4 py-3">
            <p class="text-sm font-semibold">${row.sacrament_type}</p>
            <p class="text-xs text-slate-400">${fmtDate(row.sacrament_date)} · ${row.church || ''}</p>
            <p class="text-xs text-slate-500">Presider: ${row.priest || '—'}</p>
          </div>`
      )
      .join('');
  }

  function renderAnnouncements(list) {
    const container = document.querySelector(selectors.announcementsList);
    if (!container) return;
    if (!list?.length) {
      container.innerHTML = '<p class="text-sm text-slate-400">No announcements right now.</p>';
      return;
    }
    container.innerHTML = list.slice(0, 3)
      .map((item) => {
        const summary = plainText(item.body || '').trim();
        const preview = summary.length > 110 ? `${summary.slice(0, 110)}…` : summary;
        return `
          <article class="rounded-2xl border border-white/10 bg-white/5 p-4">
            <p class="text-xs uppercase tracking-[0.3em] text-amber-200">${fmtDate(item.published_on)}</p>
            <h3 class="mt-1 text-base font-semibold">${item.title}</h3>
            <p class="text-sm text-slate-200">${preview || 'Tap to learn more from the parish office.'}</p>
            ${item.link_url ? `<a class="mt-2 inline-flex text-sm font-semibold text-amber-300" href="${item.link_url}">Open link →</a>` : ''}
          </article>`;
      })
      .join('');
  }

  function renderActivities(list) {
    const container = document.querySelector(selectors.activitiesList);
    if (!container) return;
    if (!list?.length) {
      container.innerHTML = '<p class="text-sm text-slate-400">No activities scheduled.</p>';
      return;
    }
    container.innerHTML = list.slice(0, 3)
      .map(
        (item) => `
          <article class="rounded-2xl bg-slate-900/40 px-4 py-3">
            <div class="flex items-center justify-between text-xs text-amber-200">
              <span>${item.category}</span>
              <span>${fmtDateTime(item.start_datetime)}</span>
            </div>
            <h3 class="mt-1 text-base font-semibold">${item.title}</h3>
            <p class="text-sm text-slate-300">${item.location || ''}</p>
            <p class="text-xs text-slate-400">${item.description || ''}</p>
          </article>`
      )
      .join('');
  }

  async function loadBootstrap() {
    try {
      document.body.classList.add('cursor-wait');
      const data = await fetchJSON('parishmis.api.portal.get_portal_bootstrap');
      state.bootstrap = data;
      renderProfile(data.profile);
      renderContributions(data.contributions);
      renderSacraments(data.sacraments?.records);
      renderAnnouncements(data.announcements);
      renderActivities(data.activities);
      const syncLabel = document.querySelector(selectors.syncLabel);
      if (syncLabel) {
        syncLabel.textContent = `Synced ${fmtDateTime(new Date())}`;
      }
    } catch (error) {
      console.error(error);
      alert('Unable to load portal data. Please refresh.');
    } finally {
      document.body.classList.remove('cursor-wait');
    }
  }

  async function loadCollectionTypes() {
    try {
      const select = document.querySelector('select[name="collection_type"]');
      if (!select) return;
      const types = await fetchJSON('parishmis.api.portal.get_collection_types');
      state.collectionTypes = types;
      select.innerHTML = types
        .map((row) => `<option value="${row.name}">${row.collection_type}</option>`)
        .join('');
    } catch (error) {
      console.error(error);
    }
  }

  function bindRefresh() {
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', (event) => {
        event.preventDefault();
        loadBootstrap();
      });
    }
  }

  function scrollToTarget(target) {
    if (!target) return;
    const el = document.querySelector(target);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  function toggleSheet(name, show) {
    const sheet = document.querySelector(`[data-sheet="${name}"]`);
    if (!sheet) return;
    if (show) {
      sheet.classList.remove('hidden');
      sheet.classList.add('flex');
      state.activeSheet = name;
    } else {
      sheet.classList.remove('flex');
      sheet.classList.add('hidden');
      if (state.activeSheet === name) {
        state.activeSheet = null;
      }
    }
  }

  function bindActions() {
    document.querySelectorAll('[data-action]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const action = btn.getAttribute('data-action');
        if (action === 'give') return toggleSheet('give', true);
        if (action === 'family') return toggleSheet('family', true);
        if (action === 'nav') return scrollToTarget(btn.getAttribute('data-target'));
      });
    });

    document.querySelectorAll('[data-sheet-close]').forEach((btn) => {
      btn.addEventListener('click', () => toggleSheet(btn.getAttribute('data-sheet-close'), false));
    });

    document.querySelectorAll('[data-sheet]').forEach((sheet) => {
      sheet.addEventListener('click', (event) => {
        if (event.target === sheet) toggleSheet(sheet.getAttribute('data-sheet'), false);
      });
    });

    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && state.activeSheet) {
        toggleSheet(state.activeSheet, false);
      }
    });
  }

  function bindGiveForm() {
    const form = document.getElementById('give-form');
    const feedback = document.getElementById('give-feedback');
    if (!form) return;
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      feedback.textContent = 'Sending STK push…';
      const formData = new FormData(form);
      try {
        const payload = await fetchJSON('parishmis.api.portal.start_mpesa_payment', {
          method: 'POST',
          body: {
            collection_type: formData.get('collection_type'),
            amount: Number(formData.get('amount')),
            remarks: formData.get('remarks')
          }
        });
        feedback.textContent = `Check your phone to complete payment. Ref ${payload.collection}.`;
        form.reset();
        toggleSheet('give', false);
        loadBootstrap();
      } catch (error) {
        console.error(error);
        feedback.textContent = error.message || 'Failed to initiate payment. Please try again.';
      }
    });
  }

  function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/assets/parishmis/portal/sw.js').catch((error) => {
        console.warn('SW registration failed', error);
      });
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    bindRefresh();
    bindActions();
    bindGiveForm();
    registerServiceWorker();
    loadBootstrap();
    loadCollectionTypes();
  });
})();
