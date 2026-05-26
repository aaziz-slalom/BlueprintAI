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
    // 1. Select the avatar container by escaping the special characters in the Tailwind classes
    const avatar = document.querySelector(
      '.relative.flex.shrink-0.overflow-hidden.rounded-full.h-5.w-5.mt-\\[3px\\]',
    );

    if (avatar) {
      // 2. Remove the old size and alignment classes
      avatar.classList.remove('h-5', 'w-5', 'mt-[3px]');

      // 3. Add your new larger size classes (h-10 and w-10 are 40px)
      // We also remove or adjust the top margin so it aligns nicely with the text
      avatar.classList.add('h-10', 'w-10', 'mt-0');

      console.log('Avatar resized successfully!');
    }
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
