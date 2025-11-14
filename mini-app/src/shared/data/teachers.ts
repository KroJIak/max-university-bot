export type Teacher = {
  id: string;
  fullName: string;
  department: string;
  email: string;
  avatar: string;
};

export const teachers: Teacher[] = [
  {
    id: 'teacher-ivanova',
    fullName: 'Иванова Марина Олеговна',
    department: 'Кафедра информатики и вычислительной техники',
    email: 'm.ivanova@maxuniversity.ru',
    avatar: 'https://images.unsplash.com/photo-1544723795-3fb6469f5b39?auto=format&fit=crop&w=320&q=60',
  },
  {
    id: 'teacher-petrov',
    fullName: 'Петров Алексей Викторович',
    department: 'Кафедра высшей математики',
    email: 'a.petrov@maxuniversity.ru',
    avatar: 'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=320&q=60',
  },
  {
    id: 'teacher-kuznetsova',
    fullName: 'Кузнецова Елена Сергеевна',
    department: 'Кафедра экономического анализа',
    email: 'e.kuznetsova@maxuniversity.ru',
    avatar: 'https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=320&q=60',
  },
  {
    id: 'teacher-sidorov',
    fullName: 'Сидоров Дмитрий Валерьевич',
    department: 'Кафедра программной инженерии',
    email: 'd.sidorov@maxuniversity.ru',
    avatar: 'https://images.unsplash.com/photo-1527980965255-d3b416303d12?auto=format&fit=crop&w=320&q=60',
  },
];


