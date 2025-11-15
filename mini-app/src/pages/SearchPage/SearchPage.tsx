import { useState, useMemo, useCallback } from 'react';
import styles from './SearchPage.module.scss';

export type SearchResult = {
  id: string;
  title: string;
  category?: string;
  keywords: string[];
  onNavigate: () => void;
};

type SearchPageProps = {
  onNavigate: (page: string) => void;
  onNavigateToProfile: (section?: string) => void;
};

// Список всех доступных страниц и разделов
const searchableItems: SearchResult[] = [
  // Основные страницы
  { 
    id: 'home', 
    title: 'Главная', 
    keywords: ['главная', 'home', 'главная страница', 'начало', 'старт', 'main', 'главная страница'], 
    onNavigate: () => {} 
  },
  { 
    id: 'news', 
    title: 'Новости', 
    keywords: ['новости', 'news', 'объявления', 'события', 'анонсы', 'обновления', 'новое', 'latest'], 
    onNavigate: () => {} 
  },
  { 
    id: 'schedule', 
    title: 'Расписание', 
    keywords: [
      'расписание', 'schedule', 'пары', 'занятия', 'уроки', 'лекции', 
      'практики', 'лабораторные', 'таймтейбл', 'timetable', 'пара', 
      'занятие', 'урок', 'лекция', 'практика', 'лабораторная'
    ], 
    onNavigate: () => {} 
  },
  { 
    id: 'services', 
    title: 'Сервисы', 
    keywords: [
      'сервисы', 'services', 'услуги', 'сервис', 'service', 'инструменты', 
      'tools', 'функции', 'features', 'возможности'
    ], 
    onNavigate: () => {} 
  },
  { 
    id: 'profile', 
    title: 'Профиль', 
    keywords: [
      'профиль', 'profile', 'личный кабинет', 'аккаунт', 'account', 
      'пользователь', 'user', 'мой профиль', 'настройки профиля', 
      'личные данные', 'данные', 'информация о себе', 'id', 'макс id'
    ], 
    onNavigate: () => {} 
  },

  // Сервисы
  { 
    id: 'primaryServices', 
    title: 'Основные сервисы', 
    category: 'Сервисы', 
    keywords: [
      'основные', 'сервисы', 'primary', 'главные сервисы', 'основные услуги',
      'primary services', 'main services', 'базовые сервисы'
    ], 
    onNavigate: () => {} 
  },
  { 
    id: 'platforms', 
    title: 'Веб-платформы', 
    category: 'Сервисы', 
    keywords: [
      'платформы', 'веб', 'platforms', 'ссылки', 'веб-платформы', 
      'web platforms', 'ссылки на платформы', 'онлайн платформы',
      'образовательные платформы', 'ресурсы', 'веб ресурсы'
    ], 
    onNavigate: () => {} 
  },
  { 
    id: 'teachers', 
    title: 'Преподаватели', 
    category: 'Сервисы', 
    keywords: [
      'преподаватели', 'учителя', 'teachers', 'преподы', 'преподаватель',
      'учитель', 'teacher', 'педагоги', 'преподавательский состав',
      'препод', 'преподавательский', 'faculty', 'staff'
    ], 
    onNavigate: () => {} 
  },
  { 
    id: 'maps', 
    title: 'Карты', 
    category: 'Сервисы', 
    keywords: [
      'карты', 'maps', 'корпуса', 'адреса', 'карта', 'map', 'геолокация',
      'location', 'где находится', 'адрес', 'корпус', 'здание', 'building',
      'yandex карты', 'google карты', '2gis', 'яндекс карты'
    ], 
    onNavigate: () => {} 
  },
  { 
    id: 'contacts', 
    title: 'Контакты', 
    category: 'Сервисы', 
    keywords: [
      'контакты', 'contacts', 'телефоны', 'адреса', 'контакт', 'contact',
      'телефон', 'phone', 'email', 'почта', 'email', 'связаться', 'связь',
      'деканаты', 'кафедры', 'отделы', 'контактная информация'
    ], 
    onNavigate: () => {} 
  },
  { 
    id: 'chats', 
    title: 'Чаты', 
    category: 'Сервисы', 
    keywords: [
      'чаты', 'chats', 'беседы', 'группы', 'чат', 'chat', 'беседа', 
      'группа', 'group', 'общение', 'сообщения', 'переписка',
      'университет чат', 'факультет чат', 'курс чат', 'куратор'
    ], 
    onNavigate: () => {} 
  },
  { 
    id: 'requests', 
    title: 'Запросы и справки', 
    category: 'Сервисы', 
    keywords: [
      'запросы', 'справки', 'requests', 'документы', 'запрос', 'request',
      'справка', 'document', 'документ', 'получить справку', 'оформить',
      'заказать справку', 'выписка', 'справка об обучении'
    ], 
    onNavigate: () => {} 
  },
  { 
    id: 'practice', 
    title: 'Практика', 
    category: 'Сервисы', 
    keywords: [
      'практика', 'practice', 'стажировка', 'internship', 'практические занятия',
      'производственная практика', 'учебная практика', 'практикант'
    ], 
    onNavigate: () => {} 
  },

  // Профиль - данные
  { 
    id: 'profile-faculty', 
    title: 'Факультет', 
    category: 'Профиль', 
    keywords: [
      'факультет', 'faculty', 'деканат', 'dean', 'факультет', 'институт', 'institute'
    ], 
    onNavigate: () => {} 
  },
  { 
    id: 'profile-speciality', 
    title: 'Специальность', 
    category: 'Профиль', 
    keywords: [
      'специальность', 'speciality', 'специализация', 'specialization', 'направление', 'direction'
    ], 
    onNavigate: () => {} 
  },
  { 
    id: 'profile-major', 
    title: 'Профиль обучения', 
    category: 'Профиль', 
    keywords: [
      'профиль', 'major', 'профиль обучения', 'образовательный профиль', 'education profile'
    ], 
    onNavigate: () => {} 
  },
  { 
    id: 'profile-group', 
    title: 'Группа', 
    category: 'Профиль', 
    keywords: [
      'группа', 'group', 'учебная группа', 'study group', 'academic group'
    ], 
    onNavigate: () => {} 
  },
  { 
    id: 'profile-gradebook-number', 
    title: 'Номер зачётки', 
    category: 'Профиль', 
    keywords: [
      'номер зачётки', 'зачётка номер', 'зачётная книжка номер', 'gradebook number',
      'номер зачётной книжки', 'зачётки', 'zachetka', 'gradebook'
    ], 
    onNavigate: () => {} 
  },
  { 
    id: 'profile-max-id', 
    title: 'MAX ID', 
    category: 'Профиль', 
    keywords: [
      'max id', 'макс id', 'id', 'identifier', 'user id', 'userid', 'user_id',
      'мой id', 'мой max id', 'мой макс id', 'идентификатор'
    ], 
    onNavigate: () => {} 
  },
  { 
    id: 'profile-max-username', 
    title: 'MAX username', 
    category: 'Профиль', 
    keywords: [
      'max username', 'макс username', 'username', 'юзернейм', 'ник', 'nickname',
      'мой username', 'мой ник', 'max ник'
    ], 
    onNavigate: () => {} 
  },
  { 
    id: 'profile-phone', 
    title: 'Телефон', 
    category: 'Профиль', 
    keywords: [
      'телефон', 'phone', 'телефонный номер', 'phone number', 'номер телефона',
      'мобильный', 'mobile', 'сотовый', 'cell phone'
    ], 
    onNavigate: () => {} 
  },
  { 
    id: 'profile-birthday', 
    title: 'Дата рождения', 
    category: 'Профиль', 
    keywords: [
      'дата рождения', 'birthday', 'день рождения', 'дата', 'birth date',
      'др', 'год рождения', 'birth year', 'возраст', 'age'
    ], 
    onNavigate: () => {} 
  },
  { 
    id: 'profile-subgroup', 
    title: 'Подгруппа', 
    category: 'Профиль', 
    keywords: [
      'подгруппа', 'subgroup', 'подгруппа 1', 'подгруппа 2', 'subgroup 1', 'subgroup 2',
      'группа подгруппа', 'учебная подгруппа'
    ], 
    onNavigate: () => {} 
  },
  { 
    id: 'gradebook', 
    title: 'Зачётная книжка', 
    category: 'Профиль', 
    keywords: [
      'зачётка', 'зачётная', 'gradebook', 'оценки', 'зачёты', 'зачётная книжка',
      'зачёты', 'экзамены', 'exams', 'оценка', 'grade', 'баллы', 'points',
      'успеваемость', 'academic performance', 'табель', 'ведомость'
    ], 
    onNavigate: () => {} 
  },
  { 
    id: 'debts', 
    title: 'Долги', 
    category: 'Профиль', 
    keywords: [
      'долги', 'debts', 'задолженности', 'долг', 'debt', 'задолженность',
      'незакрытые', 'не сданные', 'просроченные', 'незачёты', 'пересдачи',
      'долги по учёбе', 'академическая задолженность'
    ], 
    onNavigate: () => {} 
  },
  { 
    id: 'theme', 
    title: 'Внешний вид', 
    category: 'Профиль', 
    keywords: [
      'внешний вид', 'тема', 'theme', 'оформление', 'тёмная', 'светлая',
      'appearance', 'dark', 'light', 'автоматическая', 'automatic', 'auto',
      'тёмная тема', 'светлая тема', 'dark theme', 'light theme', 'night mode',
      'дневной режим', 'цветовая схема', 'дизайн', 'design'
    ], 
    onNavigate: () => {} 
  },
  { 
    id: 'notifications', 
    title: 'Уведомления и звуки', 
    category: 'Профиль', 
    keywords: [
      'уведомления', 'notifications', 'звуки', 'алерты', 'уведомление',
      'notification', 'alert', 'push', 'push-уведомления', 'звук', 'sound',
      'настройки уведомлений', 'notification settings', 'колокольчик', 'bell',
      'скоро пара', 'изменение расписания', 'оценка в зачётку'
    ], 
    onNavigate: () => {} 
  },
  { 
    id: 'about', 
    title: 'О приложении', 
    category: 'Профиль', 
    keywords: [
      'о приложении', 'about', 'информация', 'разработчики', 'about app',
      'версия', 'version', 'версия приложения', 'разработка', 'development',
      'разработчики', 'developers', 'команда', 'team', 'создатели', 'creators',
      'goliluha', 'krojiak', 'информация о приложении'
    ], 
    onNavigate: () => {} 
  },
  { 
    id: 'support', 
    title: 'Служба поддержки', 
    category: 'Профиль', 
    keywords: [
      'поддержка', 'support', 'помощь', 'техподдержка', 'help', 'помочь',
      'проблема', 'problem', 'вопрос', 'question', 'обратиться', 'contact',
      'техническая поддержка', 'техподдержка', 'служба поддержки', 'help desk',
      'связаться с поддержкой', 'помощь и поддержка'
    ], 
    onNavigate: () => {} 
  },
  { 
    id: 'improvements', 
    title: 'Предложить улучшение', 
    category: 'Профиль', 
    keywords: [
      'предложить', 'улучшение', 'improvements', 'обратная связь', 'feedback',
      'предложение', 'suggestion', 'идея', 'idea', 'улучшить', 'improve',
      'отзыв', 'review', 'комментарий', 'comment', 'сообщить об ошибке',
      'report bug', 'feature request', 'запрос функции', 'forms', 'форма'
    ], 
    onNavigate: () => {} 
  },

  // Полезные ссылки
  { 
    id: 'usefulLinks', 
    title: 'Полезные ссылки', 
    keywords: [
      'полезные', 'ссылки', 'links', 'ресурсы', 'useful links', 
      'полезные ресурсы', 'полезные ссылки', 'дополнительные ресурсы',
      'внешние ссылки', 'external links', 'рекомендуемые ссылки'
    ], 
    onNavigate: () => {} 
  },
];

export function SearchPage({ onNavigate, onNavigateToProfile }: SearchPageProps) {
  const [searchQuery, setSearchQuery] = useState('');

  // Фильтрация результатов поиска
  const filteredResults = useMemo(() => {
    if (!searchQuery.trim()) {
      return searchableItems;
    }

    const query = searchQuery.toLowerCase().trim();
    const queryWords = query.split(/\s+/).filter(word => word.length > 0);

    return searchableItems
      .map((item) => {
        // Проверяем совпадения в названии, категории и ключевых словах
        const titleLower = item.title.toLowerCase();
        const categoryLower = item.category?.toLowerCase() || '';
        const keywordsLower = item.keywords.join(' ').toLowerCase();
        const fullText = `${titleLower} ${categoryLower} ${keywordsLower}`;
        const fullTextWithSpaces = ` ${fullText} `; // Для поиска целых слов

        // Подсчитываем количество совпадений
        let score = 0;

        // Точное совпадение в названии - самый высокий приоритет
        if (titleLower === query) {
          score += 200; // Точное совпадение названия
        } else if (titleLower.includes(query)) {
          score += 100; // Частичное совпадение в названии
        }

        // Точное совпадение в ключевых словах
        if (keywordsLower.includes(` ${query} `) || keywordsLower.startsWith(query + ' ') || keywordsLower.endsWith(' ' + query)) {
          score += 80; // Целое слово в ключевых словах
        } else if (keywordsLower.includes(query)) {
          score += 60; // Частичное совпадение в ключевых словах
        }

        // Совпадение в категории
        if (categoryLower && categoryLower.includes(query)) {
          score += 50;
        }

        // Совпадения отдельных слов запроса
        queryWords.forEach((word) => {
          if (word.length < 2) return; // Игнорируем очень короткие слова
          
          // Целое слово в тексте (окруженное пробелами или границами)
          const wordPattern = new RegExp(`\\b${word}\\b`, 'i');
          if (wordPattern.test(fullText)) {
            score += 15; // Целое слово
          } else if (fullText.includes(word)) {
            score += 8; // Частичное совпадение слова
          }
        });

        // Бонус за совпадение начала названия или ключевых слов
        if (titleLower.startsWith(query) || keywordsLower.startsWith(query)) {
          score += 30;
        }

        // Бонус за совпадение всех слов запроса
        const allWordsMatch = queryWords.every(word => 
          fullText.includes(word) || titleLower.includes(word)
        );
        if (allWordsMatch && queryWords.length > 1) {
          score += 25;
        }

        return { item, score };
      })
      .filter(({ score }) => score > 0)
      .sort((a, b) => {
        // Сначала сортируем по очкам
        if (b.score !== a.score) {
          return b.score - a.score;
        }
        // Если очки равны, сортируем по длине названия (короткие первыми)
        return a.item.title.length - b.item.title.length;
      })
      .map(({ item }) => item);
  }, [searchQuery]);

  const handleItemClick = useCallback(
    (item: SearchResult) => {
      // Определяем, куда навигировать
      if (item.category === 'Профиль') {
        // Для разделов профиля используем специальную функцию
        if (item.id === 'gradebook') {
          onNavigateToProfile('gradebook');
        } else if (item.id === 'debts') {
          onNavigateToProfile('debts');
        } else if (item.id === 'theme') {
          onNavigateToProfile('theme');
        } else if (item.id === 'notifications') {
          onNavigateToProfile('notifications');
        } else if (item.id === 'about' || item.id === 'support' || item.id === 'improvements') {
          // Для этих разделов переходим на профиль и скроллим к нужному элементу
          onNavigateToProfile(item.id);
        } else if (item.id.startsWith('profile-')) {
          // Для полей профиля (факультет, телефон и т.д.) переходим на профиль и скроллим к нужному полю
          onNavigateToProfile(item.id);
        } else {
          // Для остальных разделов профиля просто переходим на профиль
          onNavigate('profile');
        }
      } else {
        // Для остальных страниц используем обычную навигацию
        onNavigate(item.id);
      }
    },
    [onNavigate, onNavigateToProfile],
  );

  return (
    <div className={styles.page}>
      <div className={styles.searchContainer}>
        <div className={styles.searchBox}>
          <input
            type="text"
            className={styles.searchInput}
            placeholder="Поиск..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            autoFocus
          />
        </div>

        <div className={styles.results}>
          {filteredResults.length === 0 ? (
            <div className={styles.emptyState}>
              <p>Ничего не найдено</p>
              <span>Попробуйте изменить запрос</span>
            </div>
          ) : (
            <>
              {!searchQuery.trim() && <div className={styles.sectionTitle}>Все разделы</div>}
              {filteredResults.map((item) => (
                <button key={item.id} className={styles.resultItem} onClick={() => handleItemClick(item)}>
                  <div className={styles.resultContent}>
                    <span className={styles.resultTitle}>{item.title}</span>
                    {item.category && <span className={styles.resultCategory}>{item.category}</span>}
                  </div>
                  <span className={styles.resultArrow}>→</span>
                </button>
              ))}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

