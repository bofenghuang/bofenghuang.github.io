(() => {
  const button = document.getElementById('theme-toggle');
  if (!button) return;
  const updateLabel = () => {
    const dark = document.documentElement.dataset.theme === 'dark';
    const label = dark ? 'Switch to light mode' : 'Switch to dark mode';
    button.setAttribute('aria-label', label);
    button.title = label;
  };
  updateLabel();
  new MutationObserver(updateLabel).observe(document.documentElement, {attributes: true, attributeFilter: ['data-theme']});
})();
