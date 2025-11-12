import { ArrowRightIcon } from '../icons';
import { newsItems } from '../../pages/MainPage/data';
import styles from './NewsSection.module.scss';

export function NewsSection() {
  return (
    <section className={styles.section}>
      <header className={styles.header}>
        <h2 className={styles.title}>Новости</h2>
        <button className={styles.moreButton} type="button" aria-label="Новости">
          <ArrowRightIcon className={styles.moreIcon} />
        </button>
      </header>
      <div className={styles.listWrapper}>
        <div className={styles.list}>
          {newsItems.map((news) => (
            <article key={news.id} className={styles.card}>
              <div className={styles.thumbnail}>
                <img src={news.image} alt={news.title} />
              </div>
              <div className={styles.content}>
                <h3 className={styles.newsTitle}>{news.title}</h3>
                <p className={styles.newsDescription}>{news.description}</p>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

