import { ArrowRightIcon } from '@components/icons';
import type { NewsItem } from '@shared/types/news';
import { newsItems } from '@shared/data/mainPage';
import styles from './NewsSection.module.scss';

type NewsSectionProps = {
  onOpenAll?: () => void;
};

const PREVIEW_COUNT = 3;

function NewsPreviewList({ items }: { items: NewsItem[] }) {
  return (
    <div className={styles.listWrapper}>
      <div className={styles.list}>
        {items.map((news) => (
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
  );
}

export function NewsSection({ onOpenAll }: NewsSectionProps) {
  const previewItems = newsItems.slice(0, PREVIEW_COUNT);

  return (
    <section className={styles.section}>
      <header className={styles.header}>
        <h2 className={styles.title}>Новости</h2>
        <button
          className={styles.moreButton}
          type="button"
          aria-label="Все новости"
          onClick={onOpenAll}
        >
          <ArrowRightIcon className={styles.moreIcon} />
        </button>
      </header>
      <NewsPreviewList items={previewItems} />
    </section>
  );
}

