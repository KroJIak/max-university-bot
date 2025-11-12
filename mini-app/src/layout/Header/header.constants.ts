export const headerActions = [
  { id: 'search', label: 'Поиск' as const },
  { id: 'notifications', label: 'Уведомления' as const },
] as const;

export type HeaderActionId = (typeof headerActions)[number]['id'];

