import type { FC } from 'react';

import { ArrowRightIcon } from '@components/icons';
import type { ServiceItem } from './types';
import styles from './PlatformsSection.module.scss';

type PlatformsSectionProps = {
  title: string;
  items: ServiceItem[];
  onOpen?: () => void;
  onItemSelect?: (item: ServiceItem) => void;
  showMoreButton?: boolean;
  layout?: 'rows' | 'grid';
  hideTitle?: boolean;
};

export const PlatformsSection: FC<PlatformsSectionProps> = ({
  title,
  items,
  onOpen,
  onItemSelect,
  showMoreButton = true,
  layout = 'rows',
  hideTitle = false,
}) => {
  if (layout === 'grid') {
    return (
      <section className={styles.section}>
        <header className={styles.header}>
          {!hideTitle && <h2 className={styles.title}>{title}</h2>}
          {showMoreButton ? (
            <button
              type="button"
              className={styles.moreButton}
              aria-label={`Открыть раздел ${title}`}
              onClick={onOpen}
            >
              <ArrowRightIcon className={styles.moreIcon} />
            </button>
          ) : (
            <span className={styles.headerPlaceholder} aria-hidden="true" />
          )}
        </header>

        <div className={styles.gridList}>
          {items.map((item, index) => {
            const isLastSingle = items.length % 2 === 1 && index === items.length - 1;
            const itemClassName = isLastSingle
              ? `${styles.item} ${styles.gridItemWide}`
              : styles.item;

            return (
              <div key={item.id} className={itemClassName}>
                <button
                  type="button"
                  className={styles.card}
                  aria-label={item.title}
                  onClick={() => onItemSelect?.(item)}
                >
                  <span className={styles.cardIcon} aria-hidden="true">
                    {item.icon}
                  </span>
                </button>
                <span className={styles.cardLabel}>{item.title}</span>
              </div>
            );
          })}
        </div>
      </section>
    );
  }

  const rows: ServiceItem[][] = [];

  for (let index = 0; index < items.length; index += 4) {
    rows.push(items.slice(index, index + 4));
  }

  if (!rows.length) {
    rows.push([]);
  }

  return (
    <section className={styles.section}>
      <header className={styles.header}>
        {!hideTitle && <h2 className={styles.title}>{title}</h2>}
        {showMoreButton ? (
          <button
            type="button"
            className={styles.moreButton}
            aria-label={`Открыть раздел ${title}`}
            onClick={onOpen}
          >
            <ArrowRightIcon className={styles.moreIcon} />
          </button>
        ) : (
          <span className={styles.headerPlaceholder} aria-hidden="true" />
        )}
      </header>

      <div className={styles.list}>
        {rows.map((row, rowIndex) => {
          const columns = row.length || 1;
          return (
            <div
              key={`row-${rowIndex}`}
              className={styles.row}
              style={{ gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))` }}
            >
              {row.map((item) => (
                <div key={item.id} className={styles.item}>
                  <button
                    type="button"
                    className={styles.card}
                    aria-label={item.title}
                    onClick={() => onItemSelect?.(item)}
                  >
                    <span className={styles.cardIcon} aria-hidden="true">
                      {item.icon}
                    </span>
                  </button>
                  <span className={styles.cardLabel}>{item.title}</span>
                </div>
              ))}
            </div>
          );
        })}
      </div>
    </section>
  );
};


