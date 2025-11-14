import type { Teacher } from '@shared/data/teachers';
import styles from './TeacherDetailPage.module.scss';

type TeacherDetailPageProps = {
  teacher: Teacher;
};

export function TeacherDetailPage({ teacher }: TeacherDetailPageProps) {
  return (
    <div className={styles.page}>
      <article className={styles.card}>
        <div className={styles.avatarWrapper}>
          <img className={styles.avatar} src={teacher.avatar} alt={teacher.fullName} />
        </div>

        <div className={styles.info}>
          <section className={styles.details}>
            <div className={styles.row}>
              <span className={styles.label}>ФИО</span>
              <span className={styles.value}>{teacher.fullName}</span>
            </div>
            <div className={styles.separator} />
            <div className={styles.row}>
              <span className={styles.label}>Кафедра</span>
              <span className={styles.value}>{teacher.department}</span>
            </div>
            <div className={styles.separator} />
            <div className={styles.row}>
              <span className={styles.label}>Почта</span>
              <a className={styles.link} href={`mailto:${teacher.email}`}>
                {teacher.email}
              </a>
            </div>
          </section>
        </div>
      </article>
    </div>
  );
}


