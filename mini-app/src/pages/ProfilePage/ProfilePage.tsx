import { ArrowRightIcon } from '../../components/icons';
import styles from './ProfilePage.module.scss';

type StatCard = {
  id: string;
  title: string;
  value: string;
  suffix: string;
  icon: string;
  hint?: string;
};

type SettingsGroup = {
  id: string;
  items: { id: string; icon: string; title: string }[];
};

const statCards: StatCard[] = [
  {
    id: 'gradebook',
    title: 'Зачётка',
    value: '3.90',
    suffix: 'ср. балл',
    icon: '🟦',
    hint: '— —',
  },
  {
    id: 'debts',
    title: 'Долги',
    value: '0',
    suffix: 'долгов',
    icon: '😎',
  },
];

const settingsGroups: SettingsGroup[] = [
  {
    id: 'preferences',
    items: [
      { id: 'cache', icon: '⚙️', title: 'Настройки и кэш' },
      { id: 'theme', icon: '🎨', title: 'Внешний вид' },
      { id: 'language', icon: '🌐', title: 'Язык интерфейса' },
      { id: 'notifications', icon: '🔔', title: 'Уведомления и звуки' },
      { id: 'security', icon: '🛡️', title: 'Безопасность' },
    ],
  },
  {
    id: 'support',
    items: [
      { id: 'about', icon: 'ℹ️', title: 'О приложении' },
      { id: 'support', icon: '🆘', title: 'Служба поддержки' },
      { id: 'community', icon: '🔗', title: 'Группа VK' },
      { id: 'improvements', icon: '⭐️', title: 'Предложить улучшение' },
    ],
  },
];

export function ProfilePage() {
  return (
    <div className={styles.page}>
      <section className={styles.card}>
        <div className={styles.avatar} />
        <div className={styles.info}>
          <span className={styles.name}>Александра Иванова</span>
          <span className={styles.value}>Студентка, 3 курс</span>
        </div>
      </section>

      <section className={styles.card}>
        <div className={styles.row}>
          <span className={styles.label}>Факультет</span>
          <span className={styles.value}>Экономики и управления</span>
        </div>
        <div className={styles.row}>
          <span className={styles.label}>Группа</span>
          <span className={styles.value}>ЭК-04-22</span>
        </div>
        <div className={styles.row}>
          <span className={styles.label}>Куратор</span>
          <span className={styles.value}>Ирина Соколова</span>
        </div>
      </section>

       <section className={styles.stats}>
        {statCards.map((stat) => (
          <article key={stat.id} className={styles.statCard}>
            <header className={styles.statHeader}>
              <span className={styles.statTitle}>{stat.title}</span>
              <button type="button" className={styles.statAction} aria-label={stat.title}>
                <ArrowRightIcon className={styles.statActionIcon} />
              </button>
            </header>
            <div className={styles.statBody}>
              <span className={styles.statIcon} aria-hidden="true">
                {stat.icon}
              </span>
              <div className={styles.statValueGroup}>
                <span className={styles.statValue}>{stat.value}</span>
                <span className={styles.statSuffix}>{stat.suffix}</span>
                {stat.hint && <span className={styles.statHint}>{stat.hint}</span>}
              </div>
            </div>
          </article>
        ))}
      </section>

      <section className={styles.settings}>
        {settingsGroups.map((group) => (
          <article key={group.id} className={styles.settingsCard}>
            <div className={styles.settingsList}>
              {group.items.map((item) => (
                <button key={item.id} type="button" className={styles.settingsItem}>
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
        <button type="button" className={styles.logoutButton}>
          <span className={styles.logoutIcon} aria-hidden="true">
            ⎋
          </span>
          Выйти из аккаунта
        </button>
      </section>
    </div>
  );
}

