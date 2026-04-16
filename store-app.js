/* ===== 13th Chamber — App Logic ===== */

(function () {
  'use strict';

  // ===== PARTICLE BACKGROUND =====
  const canvas = document.getElementById('particles');
  const ctx = canvas.getContext('2d');
  let particles = [];
  let w, h;
  let animId;

  function resize() {
    w = canvas.width = window.innerWidth;
    h = canvas.height = window.innerHeight;
  }

  function isDark() {
    return document.documentElement.getAttribute('data-theme') === 'dark';
  }

  class Particle {
    constructor() {
      this.reset();
    }

    reset() {
      this.x = Math.random() * w;
      this.y = Math.random() * h;
      this.size = Math.random() * 1.5 + 0.5;
      this.speedX = (Math.random() - 0.5) * 0.3;
      this.speedY = (Math.random() - 0.5) * 0.3;
      this.opacity = Math.random() * 0.5 + 0.1;
      this.pulse = Math.random() * Math.PI * 2;
      this.pulseSpeed = Math.random() * 0.02 + 0.005;
    }

    update() {
      this.x += this.speedX;
      this.y += this.speedY;
      this.pulse += this.pulseSpeed;

      if (this.x < -10) this.x = w + 10;
      if (this.x > w + 10) this.x = -10;
      if (this.y < -10) this.y = h + 10;
      if (this.y > h + 10) this.y = -10;
    }

    draw() {
      const dark = isDark();
      const op = this.opacity * (0.7 + 0.3 * Math.sin(this.pulse));
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
      ctx.fillStyle = dark
        ? `rgba(0, 229, 255, ${op})`
        : `rgba(0, 151, 167, ${op * 0.6})`;
      ctx.fill();
    }
  }

  function initParticles() {
    const count = Math.min(Math.floor((w * h) / 12000), 120);
    particles = [];
    for (let i = 0; i < count; i++) {
      particles.push(new Particle());
    }
  }

  function drawConnections() {
    const dark = isDark();
    const maxDist = 120;
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < maxDist) {
          const op = (1 - dist / maxDist) * 0.15;
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = dark
            ? `rgba(0, 229, 255, ${op})`
            : `rgba(0, 151, 167, ${op * 0.5})`;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    }
  }

  function animate() {
    ctx.clearRect(0, 0, w, h);
    particles.forEach(p => {
      p.update();
      p.draw();
    });
    drawConnections();
    animId = requestAnimationFrame(animate);
  }

  resize();
  initParticles();
  animate();

  window.addEventListener('resize', () => {
    resize();
    initParticles();
  });


  // ===== THEME TOGGLE =====
  // Default to dark for the brand identity
  const html = document.documentElement;
  html.setAttribute('data-theme', 'dark');


  // ===== MOBILE MENU =====
  const mobileToggle = document.getElementById('mobileToggle');
  const mobileMenu = document.getElementById('mobileMenu');

  if (mobileToggle && mobileMenu) {
    mobileToggle.addEventListener('click', () => {
      const isOpen = mobileMenu.classList.toggle('is-open');
      mobileToggle.setAttribute('aria-expanded', isOpen);
    });

    mobileMenu.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        mobileMenu.classList.remove('is-open');
        mobileToggle.setAttribute('aria-expanded', 'false');
      });
    });
  }


  // ===== NUMBER COUNTER ANIMATION =====
  function animateCounters() {
    const counters = document.querySelectorAll('[data-count]');
    counters.forEach(el => {
      if (el.dataset.animated) return;
      const rect = el.getBoundingClientRect();
      if (rect.top < window.innerHeight && rect.bottom > 0) {
        el.dataset.animated = 'true';
        const target = parseInt(el.dataset.count, 10);
        const duration = 2000;
        const start = performance.now();

        function tick(now) {
          const elapsed = now - start;
          const progress = Math.min(elapsed / duration, 1);
          // Ease out cubic
          const eased = 1 - Math.pow(1 - progress, 3);
          el.textContent = Math.round(target * eased).toLocaleString();
          if (progress < 1) {
            requestAnimationFrame(tick);
          } else {
            el.textContent = target.toLocaleString();
          }
        }
        requestAnimationFrame(tick);
      }
    });
  }


  // ===== SCROLL ANIMATIONS =====
  function initScrollAnimations() {
    // Add fade-in class to elements
    const selectors = [
      '.product-card',
      '.about__text',
      '.founder-card',
      '.specs-table-wrap',
      '.specs-metrics',
      '.research-card',
      '.patent-notice'
    ];

    selectors.forEach(sel => {
      document.querySelectorAll(sel).forEach((el, i) => {
        el.classList.add('fade-in');
        el.style.transitionDelay = `${i * 80}ms`;
      });
    });

    function checkVisibility() {
      document.querySelectorAll('.fade-in').forEach(el => {
        const rect = el.getBoundingClientRect();
        if (rect.top < window.innerHeight - 60) {
          el.classList.add('is-visible');
        }
      });
      animateCounters();
    }

    window.addEventListener('scroll', checkVisibility, { passive: true });
    checkVisibility();
  }

  // Init after DOM paint
  requestAnimationFrame(initScrollAnimations);


  // ===== SMOOTH SCROLL =====
  document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', e => {
      const target = document.querySelector(link.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });


  // ===== NAV SCROLL EFFECT =====
  const nav = document.getElementById('nav');
  let lastScroll = 0;

  window.addEventListener('scroll', () => {
    const scrollY = window.scrollY;
    if (scrollY > 100) {
      nav.style.borderBottomColor = 'var(--color-border-bright)';
    } else {
      nav.style.borderBottomColor = 'var(--color-border)';
    }
    lastScroll = scrollY;
  }, { passive: true });

})();
