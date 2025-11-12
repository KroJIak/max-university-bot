import type { DayTab, ScheduleItem } from '../../shared/types/schedule';

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
    },
    {
      id: 'physics-1',
      start: '13:30',
      end: '14:50',
      title: 'Физика',
      type: 'practice',
      room: 'Г-304',
      note: 'Общая пара',
    },
    {
      id: 'logic-1',
      start: '15:00',
      end: '16:20',
      title: 'Математическая логика и теория алгоритмов',
      type: 'lecture',
      room: 'Г-301',
      note: 'Общая пара',
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
      note: 'Работа в группах',
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
    },
  ],
};

export const newsItems = [
  {
    id: 'news-1',
    title: 'С Днём рождения, Виктория!',
    description: 'Спортивная жизнь ЧГУ · 11 нояб.',
    image: 'https://images.unsplash.com/photo-1545239351-1141bd82e8a6?auto=format&fit=crop&w=300&q=80',
  },
  {
    id: 'news-2',
    title: 'Корпус наставников на форуме в Казани',
    description: 'Медицинский факультет · 11 ноября',
    image: 'https://images.unsplash.com/photo-1523050854058-8df90110c9f1?auto=format&fit=crop&w=300&q=80',
  },
  {
    id: 'news-3',
    title: 'Студенты ЭК-04-22 посетили «Кейсистемс»',
    description: 'Экономический факультет · 11 ноября',
    image: 'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=300&q=80',
  },
];


