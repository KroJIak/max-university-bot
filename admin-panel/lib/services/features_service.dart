import '../models/feature.dart';

class FeaturesService {
  // Список функций по категориям (как в HTML версии)
  static final Map<String, List<Feature>> featuresByCategory = {
    'management': [
      Feature(
        id: 'students_login',
        name: 'Логин студентов',
        description: 'Выполнить логин на сайте университета, вернуть cookies',
        defaultEndpoint: '/students/login',
        category: 'management',
      ),
      Feature(
        id: 'students_personal_data',
        name: 'Данные студента',
        description: 'Получить данные студента с lk.chuvsu.ru',
        defaultEndpoint: '/students/personal_data',
        category: 'management',
      ),
    ],
    'services': [
      Feature(
        id: 'students_teachers',
        name: 'Список преподавателей',
        description: 'Получить список всех преподавателей',
        defaultEndpoint: '/students/teachers',
        category: 'services',
      ),
      Feature(
        id: 'students_schedule',
        name: 'Расписание',
        description: 'Получить расписание занятий (текущая или следующая неделя)',
        defaultEndpoint: '/students/schedule',
        category: 'services',
      ),
      Feature(
        id: 'students_contacts',
        name: 'Контакты',
        description: 'Получить контакты деканатов и кафедр',
        defaultEndpoint: '/students/contacts',
        category: 'services',
      ),
      Feature(
        id: 'students_platforms',
        name: 'Веб-платформы',
        description: 'Получить список полезных веб-платформ',
        defaultEndpoint: '/students/platforms',
        category: 'services',
      ),
    ],
    'additional': [
      Feature(
        id: 'students_teacher_info',
        name: 'Информация о преподавателе',
        description: 'Получить информацию о конкретном преподавателе (кафедры, фото)',
        defaultEndpoint: '/students/teacher_info',
        category: 'additional',
      ),
    ],
  };

  // Получить все функции
  static List<Feature> getAllFeatures() {
    return [
      ...featuresByCategory['management']!,
      ...featuresByCategory['services']!,
      ...featuresByCategory['additional']!,
    ];
  }

  // Получить функции по категории
  static List<Feature> getFeaturesByCategory(String category) {
    return featuresByCategory[category] ?? [];
  }
}

