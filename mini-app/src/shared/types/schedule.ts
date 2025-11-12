export type ScheduleType = 'lecture' | 'practice';

export type ScheduleItem = {
  id: string;
  start: string;
  end: string;
  title: string;
  type: ScheduleType;
  room: string;
  note: string;
};

export type DayTab = {
  id: string;
  label: string;
  description: string;
};

