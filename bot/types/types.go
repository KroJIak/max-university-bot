package types

// Page представляет тип страницы в боте
type Page string

const (
	PageMain       Page = "main"
	PageServices   Page = "services"
	PageProfile    Page = "profile"
	PageSchedule   Page = "schedule"
	PageNews       Page = "news"
	PageTeachers   Page = "teachers"
	PageContacts   Page = "contacts"
	PageMaps       Page = "maps"
	PageChats      Page = "chats"
	PageDebts      Page = "debts"
	PageGradebook  Page = "gradebook"
	PageNotifications Page = "notifications"
	PageTheme      Page = "theme"
	PagePlatforms  Page = "platforms"
)

// NewsItem представляет новость
type NewsItem struct {
	ID          string
	Title       string
	Description string
	Date        string
}

// ScheduleItem представляет элемент расписания
type ScheduleItem struct {
	ID            string
	Start         string
	End           string
	Title         string
	Type          string // lecture, practice, lab
	Room          string
	Note          string
	Teacher       string
	Date          string
	AdditionalInfo string
	Audience      string // full, subgroup1, subgroup2
}

// ServiceItem представляет сервис
type ServiceItem struct {
	ID    string
	Title string
	Icon  string
	URL   string // опционально для платформ
}

// TeacherItem представляет преподавателя
type TeacherItem struct {
	ID        string
	Name      string
	Position  string
	Contacts  string
}

// NavigationAction представляет действие навигации
type NavigationAction string

const (
	ActionOpenMain       NavigationAction = "open_main"
	ActionOpenServices   NavigationAction = "open_services"
	ActionOpenProfile    NavigationAction = "open_profile"
	ActionOpenSchedule   NavigationAction = "open_schedule"
	ActionOpenNews       NavigationAction = "open_news"
	ActionOpenTeachers   NavigationAction = "open_teachers"
	ActionOpenContacts   NavigationAction = "open_contacts"
	ActionOpenMaps       NavigationAction = "open_maps"
	ActionOpenChats      NavigationAction = "open_chats"
	ActionOpenDebts      NavigationAction = "open_debts"
	ActionOpenGradebook  NavigationAction = "open_gradebook"
	ActionOpenNotifications NavigationAction = "open_notifications"
	ActionOpenTheme      NavigationAction = "open_theme"
	ActionOpenPlatforms  NavigationAction = "open_platforms"
	ActionScheduleToday  NavigationAction = "schedule_today"
	ActionScheduleTomorrow NavigationAction = "schedule_tomorrow"
	ActionScheduleAfterTomorrow NavigationAction = "schedule_after_tomorrow"
	ActionSubgroupFull   NavigationAction = "subgroup_full"
	ActionSubgroupGroup1 NavigationAction = "subgroup_group1"
	ActionSubgroupGroup2 NavigationAction = "subgroup_group2"
	ActionBack           NavigationAction = "back"
	ActionHome           NavigationAction = "home"
)

