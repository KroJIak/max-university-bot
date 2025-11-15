import type { FC } from 'react';

import styles from './Profile.module.scss';

type InfoRow = {
  id: string;
  label: string;
  value: string;
};

type ProfileInfoSectionProps = {
  rows: InfoRow[];
};

export const ProfileInfoSection: FC<ProfileInfoSectionProps> = ({ rows }) => {
  return (
    <section className={styles.card}>
      <div className={styles.infoList}>
        {rows.map((row, index) => (
          <div
            key={row.id}
            className={styles.row}
            data-last={index === rows.length - 1 ? 'true' : undefined}
            data-profile-field={row.id}
          >
          <span className={styles.label}>{row.label}</span>
          <span className={styles.value}>{row.value}</span>
        </div>
      ))}
      </div>
    </section>
  );
};

