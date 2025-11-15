import { useState, useEffect, useRef } from 'react';
import styles from './GradebookPage.module.scss';

type ExamItem = {
  id: string;
  subject: string;
  grade: number;
};

type CreditItem = {
  id: string;
  subject: string;
  passed: boolean;
};

type SemesterData = {
  semester: number;
  exams: ExamItem[];
  credits: CreditItem[];
};

// Моковые данные для демонстрации
const mockData: SemesterData[] = [
  {
    semester: 1,
    exams: [
      { id: '1', subject: 'Философия', grade: 5 },
      { id: '2', subject: 'Алгебра и геометрия', grade: 3 },
      { id: '3', subject: 'Информатика', grade: 3 },
      { id: '4', subject: 'Программирование', grade: 3 },
    ],
    credits: [
      { id: '1', subject: 'История России', passed: true },
      { id: '2', subject: 'Иностранный язык', passed: true },
      { id: '3', subject: 'Физическая культура и спорт', passed: true },
      { id: '4', subject: 'Основы российской государственности', passed: true },
    ],
  },
  {
    semester: 2,
    exams: [
      { id: '1', subject: 'История России', grade: 3 },
      { id: '2', subject: 'Математический анализ', grade: 5 },
      { id: '3', subject: 'Физика', grade: 4 },
      { id: '4', subject: 'Дискретная математика', grade: 5 },
      { id: '5', subject: 'Программирование', grade: 4 },
    ],
    credits: [
      { id: '1', subject: 'Иностранный язык', passed: true },
      { id: '2', subject: 'Элективные дисциплины (модули) по физической культуре', passed: true },
      { id: '3', subject: 'Экономика', passed: true },
    ],
  },
  {
    semester: 3,
    exams: [
      { id: '1', subject: 'Математический анализ', grade: 0 },
      { id: '2', subject: 'Физика', grade: 0 },
      { id: '3', subject: 'Математическая логика и теория алгоритмов', grade: 0 },
      { id: '4', subject: 'Электротехника и электроника', grade: 0 },
    ],
    credits: [
      { id: '1', subject: 'Иностранный язык', passed: false },
      { id: '2', subject: 'Правоведение', passed: false },
      { id: '3', subject: 'Основы военной подготовки', passed: false },
      { id: '4', subject: 'Вычислительная математика', passed: false },
    ],
  },
  {
    semester: 4,
    exams: [
      { id: '1', subject: 'Иностранный язык', grade: 0 },
      { id: '2', subject: 'Теория вероятностей, математическая статистика и случайные процессы', grade: 0 },
      { id: '3', subject: 'Цифровая схемотехника', grade: 0 },
      { id: '4', subject: 'Структуры и алгоритмы обработки данных', grade: 0 },
      { id: '5', subject: 'Объектно-ориентированное программирование', grade: 0 },
    ],
    credits: [
      { id: '1', subject: 'Элективные дисциплины (модули) по физической культуре', passed: false },
      { id: '2', subject: 'Гибкие навыки развития карьеры', passed: false },
      { id: '3', subject: 'ЭВМ и периферийные устройства', passed: false },
    ],
  },
  {
    semester: 5,
    exams: [
      { id: '1', subject: 'Базы данных', grade: 0 },
      { id: '2', subject: 'Компьютерные сети', grade: 0 },
      { id: '3', subject: 'Операционные системы', grade: 0 },
      { id: '4', subject: 'Технологии разработки программного обеспечения', grade: 0 },
    ],
    credits: [
      { id: '1', subject: 'Иностранный язык', passed: false },
      { id: '2', subject: 'Элективные дисциплины (модули) по физической культуре', passed: false },
      { id: '3', subject: 'Этика делового общения', passed: false },
    ],
  },
  {
    semester: 6,
    exams: [
      { id: '1', subject: 'Системы искусственного интеллекта', grade: 0 },
      { id: '2', subject: 'Кибербезопасность', grade: 0 },
      { id: '3', subject: 'Веб-технологии', grade: 0 },
      { id: '4', subject: 'Мобильная разработка', grade: 0 },
    ],
    credits: [
      { id: '1', subject: 'Иностранный язык', passed: false },
      { id: '2', subject: 'Элективные дисциплины (модули) по физической культуре', passed: false },
      { id: '3', subject: 'Проектный менеджмент', passed: false },
    ],
  },
  {
    semester: 7,
    exams: [
      { id: '1', subject: 'Машинное обучение', grade: 0 },
      { id: '2', subject: 'Распределённые системы', grade: 0 },
      { id: '3', subject: 'Архитектура программного обеспечения', grade: 0 },
      { id: '4', subject: 'Тестирование программного обеспечения', grade: 0 },
    ],
    credits: [
      { id: '1', subject: 'Иностранный язык', passed: false },
      { id: '2', subject: 'Элективные дисциплины (модули) по физической культуре', passed: false },
      { id: '3', subject: 'Преддипломная практика', passed: false },
    ],
  },
  {
    semester: 8,
    exams: [
      { id: '1', subject: 'Дипломная работа', grade: 0 },
    ],
    credits: [
      { id: '1', subject: 'Предзащита дипломной работы', passed: false },
    ],
  },
];

export function GradebookPage() {
  const [selectedSemester, setSelectedSemester] = useState(1);
  const semesterSelectorRef = useRef<HTMLDivElement>(null);
  const buttonRefs = useRef<Record<number, HTMLButtonElement | null>>({});

  const currentData = mockData.find((data) => data.semester === selectedSemester) || mockData[0];

  useEffect(() => {
    const activeButton = buttonRefs.current[selectedSemester];
    const selector = semesterSelectorRef.current;

    if (activeButton && selector) {
      const buttonRect = activeButton.getBoundingClientRect();
      const selectorRect = selector.getBoundingClientRect();
      const buttonCenter = buttonRect.left + buttonRect.width / 2;
      const selectorCenter = selectorRect.left + selectorRect.width / 2;
      const scrollOffset = buttonCenter - selectorCenter;

      selector.scrollBy({
        left: scrollOffset,
        behavior: 'smooth',
      });
    }
  }, [selectedSemester]);

  const getGradeColor = (grade: number): string => {
    if (grade === 5) return styles.gradeExcellent;
    if (grade === 4) return styles.gradeGood;
    if (grade === 3) return styles.gradeSatisfactory;
    return styles.gradeEmpty;
  };

  return (
    <div className={styles.page}>
      <div ref={semesterSelectorRef} className={styles.semesterSelector}>
        {mockData.map((data) => (
          <button
            key={data.semester}
            ref={(el) => {
              buttonRefs.current[data.semester] = el;
            }}
            type="button"
            className={`${styles.semesterButton} ${selectedSemester === data.semester ? styles.semesterButtonActive : ''}`}
            onClick={() => setSelectedSemester(data.semester)}
          >
            {data.semester} семестр
          </button>
        ))}
      </div>

      <div className={styles.content}>
        <section className={styles.card}>
          <h2 className={styles.sectionTitle}>Экзамены</h2>
          <div className={styles.list}>
            {currentData.exams.map((exam) => (
              <div key={exam.id} className={styles.item}>
                <span className={styles.subject}>{exam.subject}</span>
                {exam.grade > 0 ? (
                  <span className={`${styles.grade} ${getGradeColor(exam.grade)}`}>{exam.grade}</span>
                ) : (
                  <span className={styles.gradeEmpty} />
                )}
              </div>
            ))}
          </div>
        </section>

        <section className={styles.card}>
          <h2 className={styles.sectionTitle}>Зачеты</h2>
          <div className={styles.list}>
            {currentData.credits.map((credit) => (
              <div key={credit.id} className={styles.item}>
                <span className={styles.subject}>{credit.subject}</span>
                {credit.passed ? (
                  <span className={`${styles.credit} ${styles.creditPassed}`}>зачтено</span>
                ) : (
                  <span className={styles.creditEmpty} />
                )}
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

