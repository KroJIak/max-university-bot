import styles from './DebtsPage.module.scss';

export function DebtsPage() {
  return (
    <div className={styles.page}>
      <div className={styles.emptyState}>
        <p className={styles.message}>Пока долгов нет</p>
      </div>
    </div>
  );
}

