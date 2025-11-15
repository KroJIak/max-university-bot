import type { FC } from 'react';

import unknownUserImage from '@shared/data/unknown_user.jpg';
import styles from './Profile.module.scss';

type ProfileSummarySectionProps = {
  name: string;
  subtitle: string;
  photo?: string;
};

export const ProfileSummarySection: FC<ProfileSummarySectionProps> = ({ name, subtitle, photo }) => {
  const avatarSrc = photo || unknownUserImage;

  return (
    <section className={styles.card}>
      <div className={styles.summary}>
        <img className={styles.avatar} src={avatarSrc} alt={name} />
        <div className={styles.info}>
          <span className={styles.name}>{name}</span>
          <span className={styles.value}>{subtitle}</span>
        </div>
      </div>
    </section>
  );
};

