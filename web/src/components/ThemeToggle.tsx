import { useEffect, useState } from 'react';
type Theme = 'light' | 'dark' | 'system';
export function ThemeToggle() {
  const read = (): Theme => { try { const value = localStorage.getItem('color-scheme'); return value === 'light' || value === 'dark' ? value : 'system'; } catch { return 'system'; } };
  const [theme, setTheme] = useState<Theme>(read);
  useEffect(() => { const sync = () => setTheme(read()); window.addEventListener('storage', sync); return () => window.removeEventListener('storage', sync); }, []);
  function change(value: Theme) {
    setTheme(value);
    document.querySelector('meta[name="color-scheme"]')?.setAttribute('content', value === 'system' ? 'light dark' : value);
    try { if (value === 'system') localStorage.removeItem('color-scheme'); else localStorage.setItem('color-scheme', value); } catch { /* Theme still applies when storage is blocked. */ }
  }
  return <label className="theme-label">Appearance<select value={theme} onChange={e => change(e.target.value as Theme)}><option value="system">System</option><option value="light">Light</option><option value="dark">Dark</option></select></label>;
}
