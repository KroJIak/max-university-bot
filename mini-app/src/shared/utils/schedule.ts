import type { LessonAudience, ScheduleItem, SubgroupSelection } from '../types/schedule';

const matchMap: Record<SubgroupSelection, LessonAudience | null> = {
  full: null,
  subgroup1: 'subgroup1',
  subgroup2: 'subgroup2',
};

export function filterLessonsBySubgroup(
  lessons: ScheduleItem[],
  subgroup: SubgroupSelection,
): ScheduleItem[] {
  const required = matchMap[subgroup];

  if (!required) {
    return lessons;
  }

  return lessons.filter((lesson) => {
    if (!lesson.audience || lesson.audience === 'full') {
      return true;
    }

    return lesson.audience === required;
  });
}


