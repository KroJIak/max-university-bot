import type { FC } from 'react';

import { ArrowRightIcon } from '@components/icons';
import type { ServiceItem } from './types';
import styles from './PrimaryServicesSection.module.scss';

type PrimaryServicesSectionProps = {
  title: string;
  items: ServiceItem[];
  onOpen?: () => void;
  onItemSelect?: (item: ServiceItem) => void;
  showMoreButton?: boolean;
  hideTitle?: boolean;
};

export const PrimaryServicesSection: FC<PrimaryServicesSectionProps> = ({
  title,
  items,
  onOpen,
  onItemSelect,
  showMoreButton = true,
  hideTitle = false,
}) => {
  const cards = items.map((item, index) => {
    const isLastSingle = items.length % 2 === 1 && index === items.length - 1;
    const cardClassName = isLastSingle ? `${styles.card} ${styles.cardWide}` : styles.card;

    return (
      <button
        key={item.id}
        type="button"
        className={cardClassName}
        onClick={() => onItemSelect?.(item)}
      >
        <span className={styles.cardTitle}>{item.title}</span>
        <span className={styles.cardIcon} aria-hidden="true">
          {item.icon}
        </span>
      </button>
    );
  });

  if (hideTitle) {
    return (
      <section className={styles.section}>
        <div className={styles.grid}>{cards}</div>
      </section>
    );
  }

  return (
    <section className={styles.section}>
      <header className={styles.header}>
        <h2 className={styles.title}>{title}</h2>
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

      <div className={styles.grid}>{cards}</div>
    </section>
  );
};


