import type { FC } from 'react';

import styles from './Profile.module.scss';

type ProfileUniversitySectionProps = {
  name: string;
  subtitle?: string;
};

export const ProfileUniversitySection: FC<ProfileUniversitySectionProps> = ({ name, subtitle }) => {
  return (
    <section className={`${styles.card} ${styles.universityCard}`}>
      <div className={styles.universityText}>
        <span className={styles.universityName}>{name}</span>
        {subtitle ? <span className={styles.universitySubtitle}>{subtitle}</span> : null}
      </div>
    </section>
  );
};


