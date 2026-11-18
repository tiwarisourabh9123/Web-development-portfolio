/* Samriddhi Swasthya Seva – frontend logic (talks to the Flask API with fetch) */
'use strict';

const $ = (sel, root = document) => root.querySelector(sel);
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) =>
  ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

/* ---- toast ---- */
function toast(msg, isError = false) {
  let t = $('#toast');
  if (!t) { t = document.createElement('div'); t.id = 'toast'; document.body.appendChild(t); }
  t.textContent = msg;
  t.className = 'show' + (isError ? ' error' : '');
  clearTimeout(toast._t);
  toast._t = setTimeout(() => (t.className = ''), 3200);
}

/* ---- API helper: returns {ok, status, data} ---- */
async function api(path, method = 'GET', body) {
  try {
    const res = await fetch('/api' + path, {
      method,
      headers: body ? { 'Content-Type': 'application/json' } : {},
      body: body ? JSON.stringify(body) : undefined,
    });
    const data = await res.json().catch(() => ({}));
    return { ok: res.ok, status: res.status, data };
  } catch {
    return { ok: false, status: 0, data: { error: 'Cannot reach the server. Is Flask running?' } };
  }
}

const formData = (form) => Object.fromEntries(new FormData(form).entries());

/* ---- header button: Login/Register <-> Dashboard ---- */
async function setupAuthButton() {
  const btn = $('[data-auth-btn]');
  if (!btn) return;
  const { ok } = await api('/me');
  if (ok) { btn.textContent = 'Dashboard'; btn.href = 'dashboard.html'; }
  else { btn.textContent = 'Login / Register'; btn.href = 'login.html'; }
}

/* ---- pages ---- */
const pages = {
  home() {
    const form = $('#response-form');
    form?.addEventListener('submit', async (e) => {
      e.preventDefault();
      const r = await api('/contact', 'POST', formData(form));
      toast(r.data.message || r.data.error, !r.ok);
      if (r.ok) form.reset();
    });
  },

  contact() { pages.home(); },

  register() {
    const form = $('#register-form');
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const r = await api('/register', 'POST', formData(form));
      if (r.ok) { toast(r.data.message); setTimeout(() => (location.href = 'dashboard.html'), 900); }
      else toast(r.data.error, true);
    });
  },

  login() {
    const form = $('#login-form');
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const d = formData(form);
      d.remember_me = form.elements.remember_me.checked;
      const r = await api('/login', 'POST', d);
      if (r.ok) location.href = 'dashboard.html';
      else toast(r.data.error, true);
    });
  },

  async donors() {
    const form = $('#search-form');
    const grid = $('#donor-grid');
    const count = $('#donor-count');
    const params = new URLSearchParams(location.search);
    for (const [k, v] of params) if (form.elements[k]) form.elements[k].value = v;

    async function load() {
      const q = new URLSearchParams(formData(form));
      [...q.keys()].forEach((k) => !q.get(k) && q.delete(k));
      const r = await api('/donors?' + q);
      if (!r.ok) { toast(r.data.error, true); return; }
      count.textContent = `${r.data.length} donor${r.data.length === 1 ? '' : 's'} found`;
      grid.innerHTML = r.data.length ? r.data.map((d) => `
        <article class="donor-card">
          <span class="blood-badge">${esc(d.blood_group)}</span>
          <h3>${esc(d.name)}</h3>
          <p>📍 ${esc(d.area)}, ${esc(d.district)}, ${esc(d.state)}</p>
          <p>☎ <a class="link" href="tel:${esc(d.phone)}">${esc(d.phone)}</a></p>
        </article>`).join('') : '<p class="muted">No donors match your search yet.</p>';
    }
    form.addEventListener('submit', (e) => { e.preventDefault(); load(); });
    load();
  },

  async dashboard() {
    const profile = $('#profile-form');
    let donations = [];

    const me = await api('/me');
    if (!me.ok) { location.href = 'login.html'; return; }

    function fillProfile(u) {
      for (const el of profile.elements) {
        if (!el.name || !(el.name in u)) continue;
        if (el.type === 'checkbox') el.checked = !!u[el.name]; else el.value = u[el.name] ?? '';
      }
      $('#hello').textContent = `Welcome, ${u.name.split(' ')[0]}`;
      $('#stat-donations').textContent = u.donations_count;
      $('#stat-group').textContent = u.blood_group;
      $('#stat-since').textContent = (u.created_at || '').slice(0, 10);
    }
    fillProfile(me.data);

    /* Update profile */
    profile.addEventListener('submit', async (e) => {
      e.preventDefault();
      const d = formData(profile);
      delete d.email;
      d.is_available = profile.elements.is_available.checked;
      const r = await api('/me', 'PUT', d);
      toast(r.data.message || r.data.error, !r.ok);
      if (r.ok) fillProfile(r.data.user);
    });

    /* Change password */
    const pw = $('#password-form');
    pw.addEventListener('submit', async (e) => {
      e.preventDefault();
      const r = await api('/me/password', 'PUT', formData(pw));
      toast(r.data.message || r.data.error, !r.ok);
      if (r.ok) pw.reset();
    });

    /* Donations CRUD */
    const body = $('#donation-rows');
    const dForm = $('#donation-form');
    const dId = dForm.elements.id;
    dForm.elements.donated_on.max = new Date().toISOString().slice(0, 10);

    function renderDonations() {
      body.innerHTML = donations.length ? donations.map((d) => `
        <tr>
          <td>${esc(d.donated_on)}</td><td>${esc(d.location)}</td><td>${esc(d.units)}</td><td>${esc(d.notes)}</td>
          <td class="row-actions">
            <button class="btn btn-sm btn-outline" data-edit="${d.id}" type="button">Edit</button>
            <button class="btn btn-sm btn-danger" data-del="${d.id}" type="button">Delete</button>
          </td>
        </tr>`).join('') : '<tr><td colspan="5" class="muted">No donations recorded yet.</td></tr>';
      $('#stat-donations').textContent = donations.length;
    }
    async function loadDonations() {
      const r = await api('/donations');
      if (r.ok) { donations = r.data; renderDonations(); }
    }
    function resetDonationForm() { dForm.reset(); dId.value = ''; $('#donation-submit').textContent = 'Add donation'; $('#donation-cancel').hidden = true; }

    dForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const d = formData(dForm);
      const id = d.id; delete d.id;
      const r = id ? await api('/donations/' + id, 'PUT', d) : await api('/donations', 'POST', d);
      toast(r.data.message || r.data.error, !r.ok);
      if (r.ok) { resetDonationForm(); loadDonations(); }
    });
    $('#donation-cancel').addEventListener('click', resetDonationForm);
    body.addEventListener('click', async (e) => {
      const edit = e.target.dataset.edit, del = e.target.dataset.del;
      if (edit) {
        const d = donations.find((x) => String(x.id) === edit);
        for (const k of ['donated_on', 'location', 'units', 'notes']) dForm.elements[k].value = d[k];
        dId.value = d.id; $('#donation-submit').textContent = 'Save changes'; $('#donation-cancel').hidden = false;
        dForm.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
      if (del && confirm('Delete this donation record?')) {
        const r = await api('/donations/' + del, 'DELETE');
        toast(r.data.message || r.data.error, !r.ok);
        if (r.ok) loadDonations();
      }
    });
    loadDonations();

    /* Logout + delete account */
    $('#logout-btn').addEventListener('click', async () => { await api('/logout', 'POST'); location.href = 'index.html'; });
    $('#delete-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      if (!confirm('This permanently deletes your account and donation records. Continue?')) return;
      const r = await api('/me', 'DELETE', formData(e.target));
      if (r.ok) { toast(r.data.message); setTimeout(() => (location.href = 'index.html'), 1200); }
      else toast(r.data.error, true);
    });
  },
};

document.addEventListener('DOMContentLoaded', () => {
  setupAuthButton();
  const run = pages[document.body.dataset.page];
  if (run) run();
});
