import { useState, type FC } from 'react';

import { ArrowRightIcon } from '@components/icons';
import { AboutModal } from './AboutModal';
import styles from './Profile.module.scss';

type SettingsGroupItem = {
  id: string;
  icon: string;
  title: string;
};

type SettingsGroup = {
  id: string;
  items: SettingsGroupItem[];
};

type ProfileSettingsSectionProps = {
  groups: SettingsGroup[];
  onOpenNotifications?: () => void;
  onOpenTheme?: () => void;
};

const IMPROVEMENTS_URL = 'https://forms.yandex.ru/u/69171d6b4936393c5d1b1b26/';
const SUPPORT_URL = 'https://max.ru/join/Alo8firoXl3kulwip0ULCQRb9ThCrOh6a-Ww3LPlexk';

export const ProfileSettingsSection: FC<ProfileSettingsSectionProps> = ({ groups, onOpenNotifications, onOpenTheme }) => {
  const [isAboutModalOpen, setIsAboutModalOpen] = useState(false);

  const handleItemClick = (itemId: string) => {
    if (itemId === 'about') {
      setIsAboutModalOpen(true);
      return;
    }
    if (itemId === 'theme') {
      onOpenTheme?.();
      return;
    }
    if (itemId === 'notifications') {
      onOpenNotifications?.();
      return;
    }
    if (itemId === 'improvements') {
      window.open(IMPROVEMENTS_URL, '_blank', 'noopener,noreferrer');
      return;
    }
    if (itemId === 'support') {
      window.open(SUPPORT_URL, '_blank', 'noopener,noreferrer');
      return;
    }
    // Другие элементы настройки могут обрабатываться здесь в будущем
  };

  return (
    <>
    <section className={styles.settings}>
      {groups.map((group) => (
        <article key={group.id} className={styles.settingsCard}>
          <div className={styles.settingsList}>
            {group.items.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  className={styles.settingsItem}
                  onClick={() => handleItemClick(item.id)}
                  data-profile-section={item.id}
                >
                <span className={styles.settingsIcon} aria-hidden="true">
                  {item.icon}
                </span>
                <span className={styles.settingsTitle}>{item.title}</span>
                <ArrowRightIcon className={styles.settingsArrow} />
              </button>
            ))}
          </div>
        </article>
      ))}
    </section>
      <AboutModal isOpen={isAboutModalOpen} onClose={() => setIsAboutModalOpen(false)} />
    </>
  );
};

