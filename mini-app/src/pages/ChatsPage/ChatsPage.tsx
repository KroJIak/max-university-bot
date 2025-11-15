import { useEffect } from 'react';
import styles from './ChatsPage.module.scss';

type ChatCard = {
  id: string;
  title: string;
  icon: string;
  description?: string;
  url: string;
};

const chatCards: ChatCard[] = [
  {
    id: 'university',
    title: 'Чат университета',
    icon: '🏫',
    description: 'Общий чат университета',
    url: 'https://max.ru/join/chOYUhZ1oFxYkMm77gV9i7JJHXu4KsF8i6G9M3Ba-7M',
  },
  {
    id: 'faculty',
    title: 'Чат факультета',
    icon: '🏛️',
    description: 'Общий чат факультета',
    url: 'https://max.ru/join/_hUEhu3GAKV7jYgDkFg-U4u3gLp29RB4GvCsymD8z90',
  },
  {
    id: 'course',
    title: 'Чат курса',
    icon: '📚',
    description: 'Общий чат вашего курса',
    url: 'https://max.ru/join/bAABdA87H15VcMUqw3U7ZkLjPy9wXD7KXVklXedeU_Y',
  },
  {
    id: 'group',
    title: 'Чат студентов группы',
    icon: '👥',
    description: 'Чат вашей группы',
    url: 'https://max.ru/join/dP3jK3-tqSqwkkmiG8Vs_6hNBUeBP5R9i5zQMbb8Mls',
  },
  {
    id: 'curator',
    title: 'Чат с куратором группы',
    icon: '👩‍🏫',
    description: 'Личные сообщения с куратором',
    url: 'https://max.ru/join/qIdf56Ff7nqgoScPoaCGAga3VpKGEkT7i7EaSmINnvw',
  },
];

export function ChatsPage() {
  // Скролл к нужному разделу при открытии из поиска
  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    const scrollToElement = sessionStorage.getItem('scrollToElement');
    if (scrollToElement === 'chats') {
      const timeoutId = setTimeout(() => {
        const element = document.querySelector('[data-section="chats"]') || document.body.firstElementChild;
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

  const handleChatClick = (chat: ChatCard) => {
    // Открываем ссылку на чат в новой вкладке
    window.open(chat.url, '_blank', 'noopener,noreferrer');
  };

  return (
    <div className={styles.page} data-section="chats">
      <div className={styles.list}>
        {chatCards.map((chat) => (
          <button
            key={chat.id}
            type="button"
            className={styles.card}
            onClick={() => handleChatClick(chat)}
          >
            <div className={styles.iconWrapper}>
              <span className={styles.icon} aria-hidden="true">
                {chat.icon}
              </span>
            </div>
            <div className={styles.content}>
              <span className={styles.title}>{chat.title}</span>
              {chat.description && <span className={styles.description}>{chat.description}</span>}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

