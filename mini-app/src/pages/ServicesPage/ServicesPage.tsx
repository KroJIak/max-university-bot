import styles from './ServicesPage.module.scss';

type ServiceItem = {
  id: string;
  title: string;
  icon: string;
};

type ServiceSection = {
  id: string;
  title: string;
  items: ServiceItem[];
};

const serviceSections: ServiceSection[] = [
  {
    id: 'primary',
    title: 'Основные сервисы',
    items: [
      { id: 'schedule', title: 'Расписание', icon: '🗓️' },
      { id: 'webinars', title: 'Вебинары', icon: '🎥' },
      { id: 'teachers', title: 'Преподаватели', icon: '👩‍🏫' },
      { id: 'requests', title: 'Справки и запросы', icon: '📝' },
      { id: 'library', title: 'Библиотека', icon: '📚' },
      { id: 'contacts', title: 'Контакты', icon: '☎️' },
    ],
  },
];

export function ServicesPage() {
  return (
    <div className={styles.page}>
      {serviceSections.map((section) => (
        <section key={section.id} className={styles.section}>
          <h2 className={styles.sectionTitle}>{section.title}</h2>
          <div className={styles.grid}>
            {section.items.map((item) => (
              <button key={item.id} type="button" className={styles.card}>
                <span className={styles.cardTitle}>{item.title}</span>
                <span className={styles.cardIcon} aria-hidden="true">
                  {item.icon}
                </span>
              </button>
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}

