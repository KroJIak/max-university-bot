import { useEffect, useState } from 'react';

import styles from './ThemePage.module.scss';

type ThemeOption = 'dark' | 'light' | 'auto';

type ThemeSetting = {
  id: ThemeOption;
  title: string;
  description: string;
  icon: string;
};

const THEME_STORAGE_KEY = 'max-app-theme-setting';

function loadThemeSetting(): ThemeOption {
  if (typeof window === 'undefined') {
    return 'auto';
  }

  try {
    const stored = window.localStorage.getItem(THEME_STORAGE_KEY);
    if (stored === 'dark' || stored === 'light' || stored === 'auto') {
      return stored;
    }
  } catch (error) {
    console.warn('[ThemePage] Failed to load theme setting', error);
  }

  return 'auto';
}

function saveThemeSetting(theme: ThemeOption): void {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    window.localStorage.setItem(THEME_STORAGE_KEY, theme);
  } catch (error) {
    console.warn('[ThemePage] Failed to save theme setting', error);
  }
}

const themeOptions: ThemeSetting[] = [
  {
    id: 'dark',
    title: 'Тёмная тема',
    description: 'Всегда использовать тёмную тему интерфейса',
    icon: '🌙',
  },
  {
    id: 'light',
    title: 'Светлая тема',
    description: 'Всегда использовать светлую тему интерфейса',
    icon: '☀️',
  },
  {
    id: 'auto',
    title: 'Автоматическая',
    description: 'Следовать системным настройкам устройства',
    icon: '⚙️',
  },
];

export function ThemePage() {
  const [selectedTheme, setSelectedTheme] = useState<ThemeOption>(() => loadThemeSetting());

  useEffect(() => {
    saveThemeSetting(selectedTheme);
    // Здесь будет логика применения темы в будущем
    console.log('[ThemePage] Theme changed to:', selectedTheme);
  }, [selectedTheme]);

  const handleSelectTheme = (theme: ThemeOption) => {
    setSelectedTheme(theme);
  };

  return (
    <div className={styles.page}>
      <div className={styles.optionsList}>
        {themeOptions.map((option) => {
          const isSelected = selectedTheme === option.id;

          return (
            <button
              key={option.id}
              type="button"
              className={`${styles.optionItem} ${isSelected ? styles.optionItemSelected : ''}`}
              onClick={() => handleSelectTheme(option.id)}
            >
              <div className={styles.optionIcon} aria-hidden="true">
                {option.icon}
              </div>
              <div className={styles.optionContent}>
                <h3 className={styles.optionTitle}>{option.title}</h3>
                <p className={styles.optionDescription}>{option.description}</p>
              </div>
              {isSelected && (
                <div className={styles.optionCheckmark} aria-hidden="true">
                  ✓
                </div>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}

