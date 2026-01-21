function toggleTheme() {
    const html = document.documentElement;
    const isDark = html.classList.toggle('dark');


    if (localStorage.getItem('animations') !== 'true') {
        disableTransitionsTemporarily();
    }

    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    updateThemeIcon(isDark);
}

function loadTheme() {
    const savedTheme = localStorage.getItem('theme');
    const isDark = savedTheme === 'dark' || !savedTheme;

    if (localStorage.getItem('animations') !== 'true') {
        disableTransitionsTemporarily();
    }

    if (isDark) {
        document.documentElement.classList.add('dark');
    } else {
        document.documentElement.classList.remove('dark');
    }
    updateThemeIcon(isDark);
}

function updateThemeIcon(isDark) {
    document.querySelectorAll('#theme-icon')
        .forEach(el => (isDark ? el.className = 'fa-solid fa-moon' : el.className = 'fa-solid fa-sun text-yellow-500'));
}

function disableTransitionsTemporarily() {
  const style = document.createElement('style');
  style.id = 'disable-transitions';
  style.textContent = `
    * {
      transition: none !important;
    }
  `;
  document.head.appendChild(style);

  window.setTimeout(() => {
    document.getElementById('disable-transitions')?.remove();
  }, 1000)
}