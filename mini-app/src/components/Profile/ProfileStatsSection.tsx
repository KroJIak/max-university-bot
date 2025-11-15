import type { FC } from 'react';

import { ArrowRightIcon } from '@components/icons';
import styles from './Profile.module.scss';

type StatCard = {
  id: string;
  title: string;
  value: string;
  suffix: string;
  icon: string;
};

type ProfileStatsSectionProps = {
  cards: StatCard[];
  onCardClick?: (cardId: string) => void;
};

export const ProfileStatsSection: FC<ProfileStatsSectionProps> = ({ cards, onCardClick }) => {
  const handleCardClick = (cardId: string) => {
    if (onCardClick) {
      onCardClick(cardId);
    }
  };

  return (
    <section className={styles.stats}>
      {cards.map((stat) => (
        <article key={stat.id} className={styles.statCard}>
          <header className={styles.statHeader}>
            <span className={styles.statTitle}>{stat.title}</span>
            <button
              type="button"
              className={styles.statAction}
              aria-label={stat.title}
              onClick={() => handleCardClick(stat.id)}
            >
              <ArrowRightIcon className={styles.statActionIcon} />
            </button>
          </header>
          <div className={styles.statBody}>
            <span className={styles.statIcon} aria-hidden="true">
              {stat.icon}
            </span>
            <div className={styles.statValueGroup}>
              <span className={styles.statValue}>{stat.value}</span>
              <span className={styles.statSuffix}>{stat.suffix}</span>
            </div>
          </div>
        </article>
      ))}
    </section>
  );
};

