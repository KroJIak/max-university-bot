import type { ServiceItem } from '@components/Services';
import { PrimaryServicesSection } from '@components/Services';
import { primaryServices } from '@shared/data/services';
import styles from './PrimaryServicesPage.module.scss';

type PrimaryServicesPageProps = {
  onOpenSchedule?: () => void;
  onOpenTeachers?: () => void;
};

export function PrimaryServicesPage({ onOpenSchedule, onOpenTeachers }: PrimaryServicesPageProps) {
  const handleSelect = (item: ServiceItem) => {
    if (item.id === 'schedule') {
      onOpenSchedule?.();
      return;
    }

    if (item.id === 'teachers') {
      onOpenTeachers?.();
    }
  };

  return (
    <div className={styles.page}>
      <PrimaryServicesSection
        title="Основные сервисы"
        items={primaryServices}
        showMoreButton={false}
        hideTitle
        onItemSelect={handleSelect}
      />
    </div>
  );
}


