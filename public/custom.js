(function () {
  const GENIE_LOGO = '/public/genie-logo.svg';

  function setOrCreateIcon(rel, href) {
    let link = document.querySelector("link[rel='" + rel + "']");
    if (!link) {
      link = document.createElement('link');
      link.setAttribute('rel', rel);
      document.head.appendChild(link);
    }
    link.setAttribute('href', href);
  }

  function replaceBrandLogos() {
    const logoImgs = Array.from(document.querySelectorAll('img'));
    for (const img of logoImgs) {
      const src = (img.getAttribute('src') || '').toLowerCase();
      const alt = (img.getAttribute('alt') || '').toLowerCase();
      const isChainlitLogo =
        src.includes('logo_dark.svg') ||
        src.includes('logo_light.svg') ||
        src.includes('favicon.svg') ||
        alt === 'logo';

      if (isChainlitLogo && !src.includes('genie-logo.svg')) {
        img.setAttribute('src', GENIE_LOGO);
        img.setAttribute('alt', 'Genie');
      }
    }

    setOrCreateIcon('icon', GENIE_LOGO);
    setOrCreateIcon('shortcut icon', GENIE_LOGO);
    setOrCreateIcon('apple-touch-icon', GENIE_LOGO);
  }

  function createCancelButton() {
    const path = window.location.pathname || '';
    const isEnvPage = path === '/env' || path.endsWith('/env');
    if (!isEnvPage) return;

    const saveBtn = Array.from(document.querySelectorAll('button')).find(
      (btn) => (btn.textContent || '').trim().toLowerCase() === 'save',
    );
    if (!saveBtn) return;

    if (document.getElementById('bp-token-cancel-btn')) return;

    const cancelBtn = document.createElement('button');
    cancelBtn.id = 'bp-token-cancel-btn';
    cancelBtn.type = 'button';
    cancelBtn.textContent = 'Cancel';
    cancelBtn.className = saveBtn.className;
    cancelBtn.style.marginRight = '10px';

    cancelBtn.addEventListener('click', function () {
      window.location.href = '/';
    });

    saveBtn.parentElement &&
      saveBtn.parentElement.insertBefore(cancelBtn, saveBtn);
  }

  const observer = new MutationObserver(function () {
    replaceBrandLogos();
    createCancelButton();
  });

  observer.observe(document.documentElement, {
    childList: true,
    subtree: true,
  });

  replaceBrandLogos();
  createCancelButton();
})();
