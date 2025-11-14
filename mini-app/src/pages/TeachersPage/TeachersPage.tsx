import { useEffect, useMemo, useRef, useState } from 'react';

import type { Teacher } from '@shared/data/teachers';
import { teachers } from '@shared/data/teachers';
import styles from './TeachersPage.module.scss';

type TeachersPageProps = {
  onSelectTeacher?: (teacherId: string) => void;
};

const PAGE_SIZE = 10;

export function TeachersPage({ onSelectTeacher }: TeachersPageProps) {
  const [query, setQuery] = useState('');
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE);
  const loaderRef = useRef<HTMLDivElement | null>(null);

  const filteredTeachers = useMemo(() => {
    const value = query.trim().toLowerCase();
    if (!value) {
      return teachers;
    }

    return teachers.filter((teacher) => teacher.fullName.toLowerCase().includes(value));
  }, [query]);

  const displayedTeachers = useMemo(
    () => filteredTeachers.slice(0, visibleCount),
    [filteredTeachers, visibleCount],
  );

  useEffect(() => {
    setVisibleCount(PAGE_SIZE);
  }, [query]);

  useEffect(() => {
    const node = loaderRef.current;
    if (!node) {
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        const [entry] = entries;
        if (entry.isIntersecting) {
          setVisibleCount((count) => {
            if (count >= filteredTeachers.length) {
              return count;
            }
            return Math.min(filteredTeachers.length, count + PAGE_SIZE);
          });
        }
      },
      {
        rootMargin: '120px',
      },
    );

    observer.observe(node);

    return () => {
      observer.disconnect();
    };
  }, [filteredTeachers.length]);

  const handleSelect = (teacher: Teacher) => {
    onSelectTeacher?.(teacher.id);
  };

  return (
    <div className={styles.page}>
      <div className={styles.search}>
        <input
          type="search"
          className={styles.searchInput}
          placeholder="Поиск преподавателя"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />
      </div>

      {displayedTeachers.length ? (
        <ul className={styles.list}>
          {displayedTeachers.map((teacher) => (
            <li key={teacher.id}>
              <button type="button" className={styles.card} onClick={() => handleSelect(teacher)}>
                <span className={styles.name}>{teacher.fullName}</span>
              </button>
            </li>
          ))}
        </ul>
      ) : (
        <p className={styles.empty}>Преподаватели не найдены</p>
      )}

      <div ref={loaderRef} aria-hidden="true" />
    </div>
  );
}


