import { useEffect } from 'react';
import { ArrowRightIcon } from '@components/icons';
import styles from './ClubsPage.module.scss';

type ClubCard = {
  id: string;
  name: string;
  image: string;
  internalNumber: string;
  description: string;
  author: string;
  membersCount: number;
  chatUrl: string;
};

const clubCards: ClubCard[] = [
  {
    id: '1202corp',
    name: '1202 corp.',
    image: '💻',
    internalNumber: 'КЛ-001',
    description: 'Технологии, творчество, совместная разработка проектов и организация событий',
    author: 'Andrei Rastopshin',
    membersCount: 120,
    chatUrl: 'https://max.ru/join/chOYUhZ1oFxYkMm77gV9i7JJHXu4KsF8i6G9M3Ba-7M',
  },
  {
    id: 'sports',
    name: 'Спортивный клуб',
    image: '🏃',
    internalNumber: 'КЛ-002',
    description: 'Активный образ жизни, тренировки, соревнования',
    author: 'Иванов Иван',
    membersCount: 45,
    chatUrl: 'https://max.ru/join/chOYUhZ1oFxYkMm77gV9i7JJHXu4KsF8i6G9M3Ba-7M',
  },
  {
    id: 'music',
    name: 'Музыкальный клуб',
    image: '🎵',
    internalNumber: 'КЛ-003',
    description: 'Музыка, концерты, джем-сейшены',
    author: 'Петрова Мария',
    membersCount: 32,
    chatUrl: 'https://max.ru/join/chOYUhZ1oFxYkMm77gV9i7JJHXu4KsF8i6G9M3Ba-7M',
  },
  {
    id: 'tech',
    name: 'IT-клуб',
    image: '💻',
    internalNumber: 'КЛ-004',
    description: 'Программирование, хакатоны, разработка',
    author: 'Сидоров Алексей',
    membersCount: 67,
    chatUrl: 'https://max.ru/join/chOYUhZ1oFxYkMm77gV9i7JJHXu4KsF8i6G9M3Ba-7M',
  },
  {
    id: 'art',
    name: 'Творческий клуб',
    image: '🎨',
    internalNumber: 'КЛ-005',
    description: 'Рисование, дизайн, выставки',
    author: 'Козлова Анна',
    membersCount: 28,
    chatUrl: 'https://max.ru/join/chOYUhZ1oFxYkMm77gV9i7JJHXu4KsF8i6G9M3Ba-7M',
  },
  {
    id: 'debate',
    name: 'Клуб дебатов',
    image: '🗣️',
    internalNumber: 'КЛ-006',
    description: 'Публичные выступления, дискуссии, ораторское искусство',
    author: 'Морозов Дмитрий',
    membersCount: 19,
    chatUrl: 'https://max.ru/join/chOYUhZ1oFxYkMm77gV9i7JJHXu4KsF8i6G9M3Ba-7M',
  },
  {
    id: 'photo',
    name: 'Фото-клуб',
    image: '📸',
    internalNumber: 'КЛ-007',
    description: 'Фотография, обработка, выставки работ',
    author: 'Волкова Елена',
    membersCount: 41,
    chatUrl: 'https://max.ru/join/chOYUhZ1oFxYkMm77gV9i7JJHXu4KsF8i6G9M3Ba-7M',
  },
];

export function ClubsPage() {
  // Скролл к нужному разделу при открытии из поиска
  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    const scrollToElement = sessionStorage.getItem('scrollToElement');
    if (scrollToElement === 'clubs') {
      const timeoutId = setTimeout(() => {
        const element = document.querySelector('[data-section="clubs"]') || document.body.firstElementChild;
        if (element) {
          const elementRect = element.getBoundingClientRect();
          const absoluteElementTop = elementRect.top + window.pageYOffset;
          const middle = absoluteElementTop - (window.innerHeight / 2) + (elementRect.height / 2);
          window.scrollTo({
            top: Math.max(0, middle),
            behavior: 'smooth'
          });
        }
        sessionStorage.removeItem('scrollToElement');
      }, 300);
      return () => clearTimeout(timeoutId);
    }
  }, []);

  const handleClubClick = (club: ClubCard) => {
    // Открываем ссылку на чат клуба в новой вкладке
    window.open(club.chatUrl, '_blank', 'noopener,noreferrer');
  };

  return (
    <div className={styles.page} data-section="clubs">
      <div className={styles.list}>
        {clubCards.map((club) => (
          <div key={club.id} className={styles.card}>
            <div className={styles.cardContent}>
              <div className={styles.imageWrapper}>
                <span className={styles.image} aria-hidden="true">
                  {club.image}
                </span>
              </div>
              <div className={styles.info}>
                <div className={styles.header}>
                  <h3 className={styles.title}>{club.name}</h3>
                  <span className={styles.number}>{club.internalNumber}</span>
                </div>
                <p className={styles.description}>{club.description}</p>
                <div className={styles.details}>
                  <div className={styles.detailRow}>
                    <span className={styles.detailLabel}>Автор:</span>
                    <span className={styles.detailValue}>{club.author}</span>
                  </div>
                  <div className={styles.detailRow}>
                    <span className={styles.detailLabel}>Участников:</span>
                    <span className={styles.detailValue}>{club.membersCount}</span>
                  </div>
                </div>
              </div>
            </div>
            <button
              type="button"
              className={styles.chatButton}
              onClick={() => handleClubClick(club)}
              aria-label={`Открыть чат клуба ${club.name}`}
            >
              <ArrowRightIcon className={styles.arrowIcon} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

