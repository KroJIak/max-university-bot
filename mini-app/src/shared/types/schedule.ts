export type ScheduleType = 'lecture' | 'practice' | 'lab';

export type LessonAudience = 'full' | 'subgroup1' | 'subgroup2';

export type SubgroupSelection = 'full' | 'subgroup1' | 'subgroup2';

export type ScheduleItem = {
  id: string;
  start: string;
  end: string;
  title: string;
  type: ScheduleType;
  room: string;
  note: string;
  audience?: LessonAudience;
  // Дополнительные поля для детальной информации
  date?: string;
  teacher?: string;
  additional_info?: string | null;
  undergruop?: string;
};

export type DayTab = {
  id: string;
  label: string;
  description: string;
};

