import { useEffect, useState } from 'react';

import styles from './NotificationsPage.module.scss';

type NotificationSetting = {
  id: string;
  title: string;
  description: string;
  enabled: boolean;
};

const NOTIFICATIONS_STORAGE_KEY = 'max-app-notifications-settings';

function loadNotificationSettings(): NotificationSetting[] {
  if (typeof window === 'undefined') {
    return getDefaultSettings();
  }

  try {
    const stored = window.localStorage.getItem(NOTIFICATIONS_STORAGE_KEY);
    if (stored) {
      const parsed = JSON.parse(stored) as NotificationSetting[];
      // Проверяем, что все настройки на месте
      const defaultSettings = getDefaultSettings();
      const settingsMap = new Map(parsed.map((s) => [s.id, s]));
      return defaultSettings.map((defaultSetting) => {
        const stored = settingsMap.get(defaultSetting.id);
        return stored ? { ...defaultSetting, enabled: stored.enabled } : defaultSetting;
      });
    }
  } catch (error) {
    console.warn('[NotificationsPage] Failed to load notification settings', error);
  }

  return getDefaultSettings();
}

function saveNotificationSettings(settings: NotificationSetting[]): void {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    window.localStorage.setItem(NOTIFICATIONS_STORAGE_KEY, JSON.stringify(settings));
  } catch (error) {
    console.warn('[NotificationsPage] Failed to save notification settings', error);
  }
}

function getDefaultSettings(): NotificationSetting[] {
  return [
    {
      id: 'lesson_soon',
      title: 'Уведомление что скоро пара',
      description: 'Получать уведомления перед началом занятий',
      enabled: true,
    },
    {
      id: 'schedule_change',
      title: 'Уведомление об изменении в расписании',
      description: 'Получать уведомления при изменении расписания',
      enabled: true,
    },
    {
      id: 'grade_added',
      title: 'Уведомление о выставлении оценки в зачётку',
      description: 'Получать уведомления при добавлении новых оценок',
      enabled: true,
    },
  ];
}

export function NotificationsPage() {
  const [settings, setSettings] = useState<NotificationSetting[]>(() => loadNotificationSettings());

  useEffect(() => {
    saveNotificationSettings(settings);
  }, [settings]);

  const handleToggle = (id: string) => {
    setSettings((prev) =>
      prev.map((setting) => (setting.id === id ? { ...setting, enabled: !setting.enabled } : setting))
    );
  };

  return (
    <div className={styles.page}>
      <div className={styles.settingsList}>
        {settings.map((setting) => (
          <div key={setting.id} className={styles.settingItem}>
            <div className={styles.settingContent}>
              <h3 className={styles.settingTitle}>{setting.title}</h3>
              <p className={styles.settingDescription}>{setting.description}</p>
            </div>
            <button
              type="button"
              className={`${styles.toggle} ${setting.enabled ? styles.toggleActive : ''}`}
              onClick={() => handleToggle(setting.id)}
              aria-label={setting.enabled ? 'Выключить' : 'Включить'}
              aria-pressed={setting.enabled}
            >
              <span className={styles.toggleThumb} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

