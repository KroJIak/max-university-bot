import type { DayTab, ScheduleItem } from '@shared/types/schedule';
import type { NewsItem } from '@shared/types/news';

export const dayTabs: DayTab[] = [
  { id: 'today', label: 'Сегодня, пн', description: 'Активное расписание' },
  { id: 'tomorrow', label: 'Завтра, вт', description: 'Предпросмотр' },
  { id: 'afterTomorrow', label: 'Послезавтра, ср', description: 'Предпросмотр' },
];

export const scheduleByDay: Record<string, ScheduleItem[]> = {
  today: [
    {
      id: 'law-1',
      start: '11:40',
      end: '13:00',
      title: 'Правоведение',
      type: 'practice',
      room: 'Г-304',
      note: 'Общая пара',
      audience: 'full',
    },
    {
      id: 'physics-1',
      start: '13:30',
      end: '14:50',
      title: 'Физика',
      type: 'lab',
      room: 'Г-304',
      note: 'Подгруппа 1',
      audience: 'full',
    },
    {
      id: 'logic-1',
      start: '15:00',
      end: '16:20',
      title: 'Математическая логика и теория алгоритмов',
      type: 'lecture',
      room: 'Г-301',
      note: 'Общая пара',
      audience: 'full',
    },
    {
      id: 'python-workshop-1',
      start: '16:30',
      end: '17:50',
      title: 'Практикум по Python',
      type: 'practice',
      room: 'Л-208',
      note: 'Подгруппа 1',
      audience: 'subgroup1',
    },
  ],
  tomorrow: [
    {
      id: 'english-1',
      start: '10:10',
      end: '11:30',
      title: 'Английский язык',
      type: 'practice',
      room: 'Б-210',
      note: 'Подгруппа 2',
      audience: 'subgroup2',
    },
    {
      id: 'english-common',
      start: '11:40',
      end: '13:00',
      title: 'Английский — общий семинар',
      type: 'practice',
      room: 'Б-210',
      note: 'Общая пара',
      audience: 'full',
    },
  ],
  afterTomorrow: [
    {
      id: 'economics-1',
      start: '12:20',
      end: '13:40',
      title: 'Экономическая теория',
      type: 'lecture',
      room: 'А-104',
      note: 'Общая пара',
      audience: 'full',
    },
  ],
};

const rawNewsItems: NewsItem[] = [
  {
    id: 'news-001',
    title: 'Стартует зимний интенсив по Python',
    description: 'Институт цифровых технологий · 2 дек.',
    image: 'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=400&q=80',
    date: '2025-12-02',
  },
  {
    id: 'news-002',
    title: 'Команда ЧГУ победила в хакатоне «Витязь»',
    description: 'Пресс-служба ЧГУ · 30 нояб.',
    image: 'https://images.unsplash.com/photo-1531297484001-80022131f5a1?auto=format&fit=crop&w=400&q=80',
    date: '2025-11-30',
  },
  {
    id: 'news-003',
    title: 'Запущена запись на весенний отбор в акселератор',
    description: 'Центр предпринимательства · 28 нояб.',
    image: 'https://images.unsplash.com/photo-1521737604893-d14cc237f11d?auto=format&fit=crop&w=400&q=80',
    date: '2025-11-28',
  },
  {
    id: 'news-004',
    title: 'Форум молодых исследователей собрал 600 участников',
    description: 'Управление науки · 27 нояб.',
    image: 'https://images.unsplash.com/photo-1489515217757-5fd1be406fef?auto=format&fit=crop&w=400&q=80',
    date: '2025-11-27',
  },
  {
    id: 'news-005',
    title: 'Открывается студенческая медиатека в корпусе Г',
    description: 'Библиотека ЧГУ · 26 нояб.',
    image: 'https://images.unsplash.com/photo-1516979187457-637abb4f9353?auto=format&fit=crop&w=400&q=80',
    date: '2025-11-26',
  },
  {
    id: 'news-006',
    title: 'Студенты-добровольцы провели экологический субботник',
    description: 'Добровольческий центр · 25 нояб.',
    image: 'https://images.unsplash.com/photo-1522098543979-ffc7f79d5aff?auto=format&fit=crop&w=400&q=80',
    date: '2025-11-25',
  },
  {
    id: 'news-007',
    title: 'Стартует олимпиада «Профессионалы будущего»',
    description: 'Учебный отдел · 24 нояб.',
    image: 'https://images.unsplash.com/photo-1509062522246-3755977927d7?auto=format&fit=crop&w=400&q=80',
    date: '2025-11-24',
  },
  {
    id: 'news-008',
    title: 'Команда VR-лаборатории представила новый симулятор',
    description: 'VR-лаборатория · 23 нояб.',
    image: 'https://images.unsplash.com/photo-1580894897634-16e7ddab3c94?auto=format&fit=crop&w=400&q=80',
    date: '2025-11-23',
  },
  {
    id: 'news-009',
    title: 'Факультет туризма организует стажировку в Приэльбрусье',
    description: 'Факультет туризма · 22 нояб.',
    image: 'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=400&q=80',
    date: '2025-11-22',
  },
  {
    id: 'news-010',
    title: 'Мастер-класс по дизайну интерфейсов прошёл в корпусе Б',
    description: 'Школа дизайна · 21 нояб.',
    image: 'https://images.unsplash.com/photo-1545239351-1141bd82e8a6?auto=format&fit=crop&w=400&q=80',
    date: '2025-11-21',
  },
  {
    id: 'news-011',
    title: 'Объявлены результаты грантовой программы ЧГУ',
    description: 'Фонд поддержки проектов · 20 нояб.',
    image: 'https://images.unsplash.com/photo-1521737604893-d14cc237f11d?auto=format&fit=crop&w=400&q=80',
    date: '2025-11-20',
  },
  {
    id: 'news-012',
    title: 'В общежитиях стартует программа «Чистая среда»',
    description: 'Управление кампуса · 19 нояб.',
    image: 'https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?auto=format&fit=crop&w=400&q=80',
    date: '2025-11-19',
  },
  {
    id: 'news-013',
    title: 'Наставники ЧГУ прошли обучение в Казани',
    description: 'Медицинский факультет · 18 нояб.',
    image: 'https://images.unsplash.com/photo-1523050854058-8df90110c9f1?auto=format&fit=crop&w=400&q=80',
    date: '2025-11-18',
  },
  {
    id: 'news-014',
    title: 'Студенты ЭК-04-22 посетили «Кейсистемс»',
    description: 'Экономический факультет · 17 нояб.',
    image: 'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=400&q=80',
    date: '2025-11-17',
  },
  {
    id: 'news-015',
    title: 'Презентация новых сервисов MAX прошла в ЧГУ',
    description: 'MAX · 16 нояб.',
    image: 'https://images.unsplash.com/photo-1525182008055-f88b95ff7980?auto=format&fit=crop&w=400&q=80',
    date: '2025-11-16',
  },
  {
    id: 'news-016',
    title: 'Обновилось меню столовой в корпусе А',
    description: 'Столовая ЧГУ · 15 нояб.',
    image: 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=400&q=80',
    date: '2025-11-15',
  },
];

export const newsItems = rawNewsItems;


