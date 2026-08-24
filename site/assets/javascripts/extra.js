/* ============================================================
   Python Mastery — Custom JavaScript
   ============================================================ */

document.addEventListener('DOMContentLoaded', function () {

  /* ── Track Filter ──────────────────────────────────────── */
  initTrackFilter();

  /* ── Smooth scroll for anchor links ───────────────────── */
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  /* ── Active nav highlight ──────────────────────────────── */
  highlightActiveTrack();

  /* ── Progress bars animate on scroll ──────────────────── */
  animateProgressBars();

});

/* ─────────────────────────────────────────────────────────── */
function initTrackFilter() {
  const filterBtns = document.querySelectorAll('[data-track-filter]');
  if (!filterBtns.length) return;

  filterBtns.forEach(btn => {
    btn.addEventListener('click', function () {
      const track = this.dataset.trackFilter;

      // Toggle active button
      filterBtns.forEach(b => b.classList.remove('active'));
      this.classList.add('active');

      // Filter cards
      const cards = document.querySelectorAll('[data-track]');
      cards.forEach(card => {
        if (track === 'all' || card.dataset.track === track) {
          card.style.opacity = '1';
          card.style.transform = '';
          card.style.pointerEvents = '';
        } else {
          card.style.opacity = '0.35';
          card.style.transform = 'scale(0.97)';
          card.style.pointerEvents = 'none';
        }
      });
    });
  });
}

/* ─────────────────────────────────────────────────────────── */
function highlightActiveTrack() {
  const path = window.location.pathname;
  const trackMap = {
    '/core/':     'core',
    '/web/':      'web',
    '/data/':     'data',
    '/systems/':  'systems',
    '/security/': 'security',
    '/research/': 'research',
  };

  for (const [segment, track] of Object.entries(trackMap)) {
    if (path.includes(segment)) {
      document.querySelectorAll(`[data-track="${track}"]`).forEach(el => {
        el.classList.add('pm-track-active');
      });
      break;
    }
  }
}

/* ─────────────────────────────────────────────────────────── */
function animateProgressBars() {
  const bars = document.querySelectorAll('.pm-progress-bar-fill');
  if (!bars.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const bar = entry.target;
        const width = bar.dataset.width || '0%';
        setTimeout(() => { bar.style.width = width; }, 100);
        observer.unobserve(bar);
      }
    });
  }, { threshold: 0.3 });

  bars.forEach(bar => {
    const target = bar.dataset.width || '0%';
    bar.style.width = '0%';
    bar.dataset.width = target;
    observer.observe(bar);
  });
}

/* ── Copy code button enhancement ─────────────────────────── */
document.addEventListener('click', function (e) {
  if (e.target.closest('.md-clipboard')) {
    const btn = e.target.closest('.md-clipboard');
    const original = btn.innerHTML;
    btn.innerHTML = '✓';
    setTimeout(() => { btn.innerHTML = original; }, 1500);
  }
});
