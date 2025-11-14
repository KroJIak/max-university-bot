import { PlatformsSection, PrimaryServicesSection } from '@components/Services';
import type { ServiceItem } from '@components/Services';
import { platformServices, primaryServices } from '@shared/data/services';
import styles from './ServicesPage.module.scss';

type ServicesPageProps = {
  onOpenSchedule?: () => void;
  onOpenPrimaryServices?: () => void;
  onOpenPlatforms?: () => void;
  onOpenTeachers?: () => void;
};

export function ServicesPage({
  onOpenSchedule,
  onOpenPrimaryServices,
  onOpenPlatforms,
  onOpenTeachers,
}: ServicesPageProps) {
  const handlePrimarySelect = (item: ServiceItem) => {
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
        onOpen={onOpenPrimaryServices}
        onItemSelect={handlePrimarySelect}
      />
      <PlatformsSection title="Веб-платформы" items={platformServices} onOpen={onOpenPlatforms} />
    </div>
  );
}

