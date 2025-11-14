import { NewsList } from '@components/NewsFeed';
import { newsItems } from '@shared/data/mainPage';
import styles from './NewsPage.module.scss';

export function NewsPage() {
  return (
    <div className={styles.page}>
      <NewsList items={newsItems} pageSize={10} />
    </div>
  );
}

