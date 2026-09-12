// Mobile nav toggle
const navToggle = document.getElementById('navToggle');
const navList = document.getElementById('navList');
if (navToggle && navList) {
  navToggle.addEventListener('click', () => {
    const isOpen = navList.classList.toggle('open');
    navToggle.setAttribute('aria-expanded', String(isOpen));
  });
  navList.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', () => {
      navList.classList.remove('open');
      navToggle.setAttribute('aria-expanded', 'false');
    });
  });
}

document.getElementById('year').textContent = new Date().getFullYear();

// Publications, fed by data/publications.json (kept fresh by the
// scheduled GitHub Actions Google Scholar sync — see scripts/fetch_scholar.py)
async function loadPublications() {
  const listEl = document.getElementById('publicationsList');
  try {
    const res = await fetch('data/publications.json', { cache: 'no-store' });
    if (!res.ok) throw new Error('Failed to load publications.json');
    const data = await res.json();

    renderStats(data);

    const papers = (data.publications || []).slice().sort((a, b) => (b.year || 0) - (a.year || 0));
    if (!papers.length) {
      listEl.innerHTML = '<p class="pub-error">No publications found yet.</p>';
      return;
    }

    listEl.innerHTML = papers.map(renderPublication).join('');
  } catch (err) {
    listEl.innerHTML = '<p class="pub-error">Could not load publications right now. Please check back later.</p>';
    console.error(err);
  }
}

function renderPublication(pub) {
  const title = pub.link
    ? `<a href="${escapeAttr(pub.link)}" target="_blank" rel="noopener">${escapeHtml(pub.title)}</a>`
    : escapeHtml(pub.title);
  return `
    <article class="pub-card">
      <div class="pub-main">
        <div class="pub-title">${title}</div>
        <div class="pub-authors">${escapeHtml(pub.authors || '')}</div>
        <div class="pub-venue">${escapeHtml(pub.venue || '')}</div>
      </div>
      <div class="pub-meta">
        <span class="pub-year">${pub.year || ''}</span>
        <span class="pub-cites">${pub.citations ? pub.citations + ' citations' : ''}</span>
      </div>
    </article>
  `;
}

function renderStats(data) {
  const totalPapers = (data.publications || []).length;
  const totalCitations = data.total_citations ??
    (data.publications || []).reduce((sum, p) => sum + (p.citations || 0), 0);

  document.getElementById('statPapers').textContent = totalPapers || '—';
  document.getElementById('statCitations').textContent = totalCitations || '—';
}

function escapeHtml(str) {
  return String(str).replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  }[c]));
}
function escapeAttr(str) { return escapeHtml(str); }

loadPublications();
