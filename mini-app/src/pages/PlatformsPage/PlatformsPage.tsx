import { PrimaryServicesSection } from '@components/Services';
import { platformServices } from '@shared/data/services';
import styles from './PlatformsPage.module.scss';

export function PlatformsPage() {
  return (
    <div className={styles.page}>
      <PrimaryServicesSection title="Веб-платформы" items={platformServices} showMoreButton={false} hideTitle />
    </div>
  );
}


