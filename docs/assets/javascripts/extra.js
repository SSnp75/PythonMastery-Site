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

/* ── Share this page: QR code + email + copy link ─────────── */
function initShare() {
  const section = document.querySelector('[data-pm-share]');
  if (!section) return;

  const url = window.location.href.split('#')[0];
  const title = document.title;

  // Show the plain URL
  const urlEl = section.querySelector('[data-pm-url]');
  if (urlEl) urlEl.textContent = url;

  // Email link (mailto opens the user's mail app pre-filled)
  const emailEl = section.querySelector('[data-pm-email]');
  if (emailEl) {
    const subject = encodeURIComponent(title);
    const body = encodeURIComponent(title + '\n\n' + url);
    emailEl.setAttribute('href', `mailto:?subject=${subject}&body=${body}`);
  }

  // Copy link button
  const copyBtn = section.querySelector('[data-pm-copy]');
  if (copyBtn && !copyBtn.dataset.bound) {
    copyBtn.dataset.bound = '1';
    copyBtn.addEventListener('click', function () {
      navigator.clipboard.writeText(url).then(() => {
        const original = copyBtn.textContent;
        copyBtn.textContent = '✓ Copied!';
        setTimeout(() => { copyBtn.textContent = original; }, 1500);
      });
    });
  }

  // QR code — render once the library is available
  const qrEl = section.querySelector('[data-pm-qr]');
  if (qrEl && !qrEl.dataset.rendered) {
    let tries = 0;
    const render = () => {
      if (typeof QRCode !== 'undefined') {
        qrEl.innerHTML = '';
        new QRCode(qrEl, { text: url, width: 160, height: 160,
                           colorDark: '#000000', colorLight: '#ffffff' });
        qrEl.dataset.rendered = '1';
      } else if (tries++ < 40) {
        setTimeout(render, 100);   // wait for the deferred CDN script
      }
    };
    render();
  }
}

// Run on first load and on Material's instant navigation.
if (typeof document$ !== 'undefined' && document$.subscribe) {
  document$.subscribe(function () { initShare(); });
} else {
  document.addEventListener('DOMContentLoaded', initShare);
}
