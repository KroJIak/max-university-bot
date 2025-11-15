import type { DayTab, ScheduleItem } from '@shared/types/schedule';
import type { NewsItem } from '@shared/types/news';
import defaultNewsImage from './image.png';

export const dayTabs: DayTab[] = [
  { id: 'today', label: 'Сегодня, пн', description: 'Активное расписание' },
  { id: 'tomorrow', label: 'Завтра, вт', description: 'Предпросмотр' },
  { id: 'afterTomorrow', label: 'Послезавтра, ср', description: 'Предпросмотр' },
];

function getTodayDateString(): string {
  const today = new Date();
  const day = String(today.getDate()).padStart(2, '0');
  const month = String(today.getMonth() + 1).padStart(2, '0');
  const year = today.getFullYear();
  return `${day}.${month}.${year}`;
}

function getTomorrowDateString(): string {
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  const day = String(tomorrow.getDate()).padStart(2, '0');
  const month = String(tomorrow.getMonth() + 1).padStart(2, '0');
  const year = tomorrow.getFullYear();
  return `${day}.${month}.${year}`;
}

function getAfterTomorrowDateString(): string {
  const afterTomorrow = new Date();
  afterTomorrow.setDate(afterTomorrow.getDate() + 2);
  const day = String(afterTomorrow.getDate()).padStart(2, '0');
  const month = String(afterTomorrow.getMonth() + 1).padStart(2, '0');
  const year = afterTomorrow.getFullYear();
  return `${day}.${month}.${year}`;
}

export const scheduleByDay: Record<string, ScheduleItem[]> = {
  today: [
    {
      id: 'law-1',
      start: '11:40',
      end: '13:00',
      title: 'Правоведение',
      type: 'practice',
      room: 'Ауд. 304',
      note: 'Общая пара',
      audience: 'full',
      date: getTodayDateString(),
      teacher: 'Петров П.П.',
      additional_info: null,
      undergruop: undefined,
    },
    {
      id: 'physics-1',
      start: '13:30',
      end: '14:50',
      title: 'Физика',
      type: 'lab',
      room: 'Ауд. 304',
      note: 'Подгруппа 1',
      audience: 'subgroup1',
      date: getTodayDateString(),
      teacher: 'Иванова И.И.',
      additional_info: 'Принести калькулятор',
      undergruop: 'Подгруппа 1',
    },
    {
      id: 'logic-1',
      start: '15:00',
      end: '16:20',
      title: 'Математическая логика и теория алгоритмов',
      type: 'lecture',
      room: 'Ауд. 301',
      note: 'Общая пара',
      audience: 'full',
      date: getTodayDateString(),
      teacher: 'Сидоров С.С.',
      additional_info: null,
      undergruop: undefined,
    },
    {
      id: 'python-workshop-1',
      start: '16:30',
      end: '17:50',
      title: 'Практикум по Python',
      type: 'practice',
      room: 'Ауд. 208',
      note: 'Подгруппа 1',
      audience: 'subgroup1',
      date: getTodayDateString(),
      teacher: 'Орлов О.О.',
      additional_info: 'Домашнее задание на проверку',
      undergruop: 'Подгруппа 1',
    },
  ],
  tomorrow: [
    {
      id: 'english-1',
      start: '10:10',
      end: '11:30',
      title: 'Английский язык',
      type: 'practice',
      room: 'Ауд. 210',
      note: 'Подгруппа 2',
      audience: 'subgroup2',
      date: getTomorrowDateString(),
      teacher: 'Смирнова С.С.',
      additional_info: null,
      undergruop: 'Подгруппа 2',
    },
    {
      id: 'english-common',
      start: '11:40',
      end: '13:00',
      title: 'Английский — общий семинар',
      type: 'practice',
      room: 'Ауд. 210',
      note: 'Общая пара',
      audience: 'full',
      date: getTomorrowDateString(),
      teacher: 'Смирнова С.С.',
      additional_info: null,
      undergruop: undefined,
    },
  ],
  afterTomorrow: [
    {
      id: 'economics-1',
      start: '12:20',
      end: '13:40',
      title: 'Экономическая теория',
      type: 'lecture',
      room: 'Ауд. 104',
      note: 'Общая пара',
      audience: 'full',
      date: getAfterTomorrowDateString(),
      teacher: 'Козлова К.К.',
      additional_info: null,
      undergruop: undefined,
    },
  ],
};

// Единая картинка для всех новостей
const DEFAULT_NEWS_IMAGE = defaultNewsImage;

const rawNewsItems: NewsItem[] = [
  {
    id: 'news-001',
    title: 'Стартует зимний интенсив по Python',
    description: 'Институт цифровых технологий · 2 дек.',
    image: DEFAULT_NEWS_IMAGE,
    date: '2025-12-02',
  },
  {
    id: 'news-002',
    title: 'Команда ЧГУ победила в хакатоне «Витязь»',
    description: 'Пресс-служба ЧГУ · 30 нояб.',
    image: DEFAULT_NEWS_IMAGE,
    date: '2025-11-30',
  },
  {
    id: 'news-003',
    title: 'Запущена запись на весенний отбор в акселератор',
    description: 'Центр предпринимательства · 28 нояб.',
    image: DEFAULT_NEWS_IMAGE,
    date: '2025-11-28',
  },
  {
    id: 'news-004',
    title: 'Форум молодых исследователей собрал 600 участников',
    description: 'Управление науки · 27 нояб.',
    image: DEFAULT_NEWS_IMAGE,
    date: '2025-11-27',
  },
  {
    id: 'news-005',
    title: 'Открывается студенческая медиатека в корпусе Г',
    description: 'Библиотека ЧГУ · 26 нояб.',
    image: DEFAULT_NEWS_IMAGE,
    date: '2025-11-26',
  },
  {
    id: 'news-006',
    title: 'Студенты-добровольцы провели экологический субботник',
    description: 'Добровольческий центр · 25 нояб.',
    image: DEFAULT_NEWS_IMAGE,
    date: '2025-11-25',
  },
  {
    id: 'news-007',
    title: 'Стартует олимпиада «Профессионалы будущего»',
    description: 'Учебный отдел · 24 нояб.',
    image: DEFAULT_NEWS_IMAGE,
    date: '2025-11-24',
  },
  {
    id: 'news-008',
    title: 'Команда VR-лаборатории представила новый симулятор',
    description: 'VR-лаборатория · 23 нояб.',
    image: DEFAULT_NEWS_IMAGE,
    date: '2025-11-23',
  },
  {
    id: 'news-009',
    title: 'Факультет туризма организует стажировку в Приэльбрусье',
    description: 'Факультет туризма · 22 нояб.',
    image: DEFAULT_NEWS_IMAGE,
    date: '2025-11-22',
  },
  {
    id: 'news-010',
    title: 'Мастер-класс по дизайну интерфейсов прошёл в корпусе Б',
    description: 'Школа дизайна · 21 нояб.',
    image: DEFAULT_NEWS_IMAGE,
    date: '2025-11-21',
  },
  {
    id: 'news-011',
    title: 'Объявлены результаты грантовой программы ЧГУ',
    description: 'Фонд поддержки проектов · 20 нояб.',
    image: DEFAULT_NEWS_IMAGE,
    date: '2025-11-20',
  },
  {
    id: 'news-012',
    title: 'В общежитиях стартует программа «Чистая среда»',
    description: 'Управление кампуса · 19 нояб.',
    image: DEFAULT_NEWS_IMAGE,
    date: '2025-11-19',
  },
  {
    id: 'news-013',
    title: 'Наставники ЧГУ прошли обучение в Казани',
    description: 'Медицинский факультет · 18 нояб.',
    image: DEFAULT_NEWS_IMAGE,
    date: '2025-11-18',
  },
  {
    id: 'news-014',
    title: 'Студенты ЭК-04-22 посетили «Кейсистемс»',
    description: 'Экономический факультет · 17 нояб.',
    image: DEFAULT_NEWS_IMAGE,
    date: '2025-11-17',
  },
  {
    id: 'news-015',
    title: 'Презентация новых сервисов MAX прошла в ЧГУ',
    description: 'MAX · 16 нояб.',
    image: DEFAULT_NEWS_IMAGE,
    date: '2025-11-16',
  },
  {
    id: 'news-016',
    title: 'Обновилось меню столовой в корпусе А',
    description: 'Столовая ЧГУ · 15 нояб.',
    image: DEFAULT_NEWS_IMAGE,
    date: '2025-11-15',
  },
];

export const newsItems = rawNewsItems;


