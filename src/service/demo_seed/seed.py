from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.core.config import settings
from src.core.security.utils import get_password_hash
from src.db.choices import (
    ApplicationStatus,
    EventFormat,
    EventStatus,
    ProjectFormat,
    ProjectStatus,
    ProjectType,
)
from src.db.models import (
    Application,
    City,
    Event,
    Organization,
    PortfolioItem,
    Project,
    ProjectVacancy,
    Role,
    Skill,
    TeamMember,
    TeamRole,
    University,
    User,
    UserProfile,
)

DEMO_PASSWORD = "campus-demo-2026"
EXPECTED_CITY_COUNT = 50
EXPECTED_UNIVERSITY_COUNT = 20

CITIES = [
    "Москва",
    "Санкт-Петербург",
    "Казань",
    "Новосибирск",
    "Екатеринбург",
    "Нижний Новгород",
    "Самара",
    "Ростов-на-Дону",
    "Уфа",
    "Краснодар",
    "Пермь",
    "Воронеж",
    "Волгоград",
    "Саратов",
    "Тюмень",
    "Томск",
    "Иркутск",
    "Красноярск",
    "Владивосток",
    "Калининград",
    "Челябинск",
    "Омск",
    "Барнаул",
    "Кемерово",
    "Ярославль",
    "Тула",
    "Рязань",
    "Ижевск",
    "Оренбург",
    "Пенза",
    "Ульяновск",
    "Чебоксары",
    "Ставрополь",
    "Сочи",
    "Астрахань",
    "Махачкала",
    "Владикавказ",
    "Смоленск",
    "Тверь",
    "Киров",
    "Курск",
    "Белгород",
    "Липецк",
    "Орёл",
    "Вологда",
    "Петрозаводск",
    "Мурманск",
    "Архангельск",
    "Сургут",
    "Якутск",
]

UNIVERSITIES = [
    ("Московский государственный университет имени М. В. Ломоносова", "МГУ", "Москва"),
    ("Казанский федеральный университет", "КФУ", "Казань"),
    ("Санкт-Петербургский государственный университет", "СПбГУ", "Санкт-Петербург"),
    ("Университет ИТМО", "ИТМО", "Санкт-Петербург"),
    (
        "Национальный исследовательский университет Высшая школа экономики",
        "ВШЭ",
        "Москва",
    ),
    (
        "Московский государственный технический университет имени Н. Э. Баумана",
        "МГТУ",
        "Москва",
    ),
    ("Московский физико-технический институт", "МФТИ", "Москва"),
    ("Национальный исследовательский ядерный университет МИФИ", "МИФИ", "Москва"),
    ("Новосибирский государственный университет", "НГУ", "Новосибирск"),
    (
        "Уральский федеральный университет имени первого Президента России Б. Н. Ельцина",
        "УрФУ",
        "Екатеринбург",
    ),
    ("Томский государственный университет", "ТГУ", "Томск"),
    ("Томский политехнический университет", "ТПУ", "Томск"),
    ("Дальневосточный федеральный университет", "ДВФУ", "Владивосток"),
    ("Сибирский федеральный университет", "СФУ", "Красноярск"),
    (
        "Самарский национальный исследовательский университет имени академика С. П. Королева",
        "Самарский университет",
        "Самара",
    ),
    ("Южный федеральный университет", "ЮФУ", "Ростов-на-Дону"),
    (
        "Пермский национальный исследовательский политехнический университет",
        "ПНИПУ",
        "Пермь",
    ),
    (
        "Нижегородский государственный университет имени Н. И. Лобачевского",
        "ННГУ",
        "Нижний Новгород",
    ),
    ("Балтийский федеральный университет имени Иммануила Канта", "БФУ", "Калининград"),
    ("Тюменский государственный университет", "ТюмГУ", "Тюмень"),
]

SKILLS = [
    "Python",
    "FastAPI",
    "PostgreSQL",
    "SQLAlchemy",
    "Docker",
    "React",
    "TypeScript",
    "Vue",
    "UI/UX дизайн",
    "Figma",
    "Data Science",
    "Machine Learning",
    "Computer Vision",
    "NLP",
    "Product Management",
    "Project Management",
    "Бизнес-аналитика",
    "Маркетинг",
    "QA",
    "DevOps",
    "Mobile",
    "Flutter",
    "Kotlin",
    "Swift",
    "Информационная безопасность",
    "AR/VR",
    "Геймдизайн",
    "Копирайтинг",
    "Исследования пользователей",
    "Презентации",
]

TEAM_ROLES = [
    ("Backend-разработчик", "Проектирует API, бизнес-логику и интеграции."),
    ("Frontend-разработчик", "Создает клиентский интерфейс и UX-потоки."),
    ("UI/UX дизайнер", "Отвечает за исследование, прототипы и визуальный язык."),
    ("Data Scientist", "Строит модели, анализирует данные и проверяет гипотезы."),
    ("ML-инженер", "Готовит ML-пайплайны и внедряет модели в продукт."),
    ("Project Manager", "Ведет план, коммуникации, риски и ритм команды."),
    ("Product Manager", "Формирует продуктовые гипотезы и приоритизацию."),
    ("QA-инженер", "Проверяет качество, регрессии и пользовательские сценарии."),
    ("DevOps-инженер", "Настраивает окружения, CI/CD и эксплуатацию."),
    ("Маркетолог", "Отвечает за позиционирование и привлечение аудитории."),
]

USERS = [
    (
        "anna.sokolova@campus.demo",
        "Анна",
        "Соколова",
        "Москва",
        "МГУ",
        ["Python", "FastAPI", "PostgreSQL", "Product Management"],
    ),
    (
        "ivan.petrov@campus.demo",
        "Иван",
        "Петров",
        "Санкт-Петербург",
        "ИТМО",
        ["React", "TypeScript", "Figma", "UI/UX дизайн"],
    ),
    (
        "daria.volkova@campus.demo",
        "Дарья",
        "Волкова",
        "Казань",
        "КФУ",
        ["Data Science", "Machine Learning", "Python", "Презентации"],
    ),
    (
        "timur.garipov@campus.demo",
        "Тимур",
        "Гарипов",
        "Казань",
        "КФУ",
        ["FastAPI", "Docker", "DevOps", "SQLAlchemy"],
    ),
    (
        "maria.kuznetsova@campus.demo",
        "Мария",
        "Кузнецова",
        "Москва",
        "ВШЭ",
        [
            "Product Management",
            "Бизнес-аналитика",
            "Маркетинг",
            "Исследования пользователей",
        ],
    ),
    (
        "nikita.orlov@campus.demo",
        "Никита",
        "Орлов",
        "Москва",
        "МГТУ",
        ["Информационная безопасность", "Python", "DevOps", "PostgreSQL"],
    ),
    (
        "polina.morozova@campus.demo",
        "Полина",
        "Морозова",
        "Санкт-Петербург",
        "СПбГУ",
        ["UI/UX дизайн", "Figma", "Копирайтинг", "Исследования пользователей"],
    ),
    (
        "egor.ivanov@campus.demo",
        "Егор",
        "Иванов",
        "Новосибирск",
        "НГУ",
        ["Computer Vision", "Machine Learning", "Python", "Data Science"],
    ),
    (
        "alisa.fedorova@campus.demo",
        "Алиса",
        "Федорова",
        "Екатеринбург",
        "УрФУ",
        ["Project Management", "Презентации", "Бизнес-аналитика", "QA"],
    ),
    (
        "sergey.nikolaev@campus.demo",
        "Сергей",
        "Николаев",
        "Томск",
        "ТГУ",
        ["NLP", "Python", "Machine Learning", "Data Science"],
    ),
    (
        "sofia.lebedeva@campus.demo",
        "София",
        "Лебедева",
        "Томск",
        "ТПУ",
        ["Flutter", "Mobile", "QA", "Product Management"],
    ),
    (
        "artem.belov@campus.demo",
        "Артем",
        "Белов",
        "Владивосток",
        "ДВФУ",
        ["Vue", "TypeScript", "React", "UI/UX дизайн"],
    ),
    (
        "ksenia.popova@campus.demo",
        "Ксения",
        "Попова",
        "Красноярск",
        "СФУ",
        ["AR/VR", "Геймдизайн", "Figma", "Презентации"],
    ),
    (
        "roman.smirnov@campus.demo",
        "Роман",
        "Смирнов",
        "Самара",
        "Самарский университет",
        ["Kotlin", "Mobile", "Docker", "QA"],
    ),
    (
        "elena.vasilieva@campus.demo",
        "Елена",
        "Васильева",
        "Ростов-на-Дону",
        "ЮФУ",
        ["Маркетинг", "Копирайтинг", "Product Management", "Презентации"],
    ),
    (
        "denis.karpov@campus.demo",
        "Денис",
        "Карпов",
        "Пермь",
        "ПНИПУ",
        ["DevOps", "Docker", "PostgreSQL", "Информационная безопасность"],
    ),
    (
        "viktoria.medvedeva@campus.demo",
        "Виктория",
        "Медведева",
        "Нижний Новгород",
        "ННГУ",
        ["Бизнес-аналитика", "QA", "Project Management", "Исследования пользователей"],
    ),
    (
        "kirill.antonov@campus.demo",
        "Кирилл",
        "Антонов",
        "Калининград",
        "БФУ",
        ["Swift", "Mobile", "UI/UX дизайн", "Product Management"],
    ),
    (
        "yana.mikhailova@campus.demo",
        "Яна",
        "Михайлова",
        "Тюмень",
        "ТюмГУ",
        ["Data Science", "PostgreSQL", "Python", "Бизнес-аналитика"],
    ),
    (
        "pavel.romanov@campus.demo",
        "Павел",
        "Романов",
        "Москва",
        "МФТИ",
        ["Machine Learning", "NLP", "FastAPI", "Docker"],
    ),
]

ORGANIZATIONS = [
    (
        "Campus Lab",
        "Студенческая лаборатория проектного обучения.",
        "anna.sokolova@campus.demo",
    ),
    (
        "ITMO Students Hub",
        "Сообщество студенческих продуктовых команд.",
        "ivan.petrov@campus.demo",
    ),
    (
        "Kazan Digital Club",
        "Клуб цифровых инициатив и хакатонов.",
        "daria.volkova@campus.demo",
    ),
    (
        "HSE Product Studio",
        "Образовательная студия продуктовой разработки.",
        "maria.kuznetsova@campus.demo",
    ),
]

EVENTS = [
    (
        "Campus Hack Spring 2026",
        "48 часов на прототип сервиса для университетской среды.",
        "Campus Lab",
        "Москва",
        EventFormat.OFFLINE,
        EventStatus.REGISTRATION_OPEN,
        datetime(2026, 6, 12, 10),
        datetime(2026, 6, 14, 18),
        datetime(2026, 6, 5, 23, 59),
    ),
    (
        "ITMO AI Challenge",
        "Соревнование по прикладному ML для студенческих команд.",
        "ITMO Students Hub",
        "Санкт-Петербург",
        EventFormat.OFFLINE,
        EventStatus.PUBLISHED,
        datetime(2026, 7, 3, 11),
        datetime(2026, 7, 5, 19),
        datetime(2026, 6, 25, 23, 59),
    ),
    (
        "Kazan Startup Weekend",
        "Выходные для проверки стартап-гипотез и сборки MVP.",
        "Kazan Digital Club",
        "Казань",
        EventFormat.ONLINE,
        EventStatus.REGISTRATION_OPEN,
        datetime(2026, 8, 21, 10),
        datetime(2026, 8, 23, 18),
        datetime(2026, 8, 10, 23, 59),
    ),
    (
        "Product Research Day",
        "День исследований пользователей и продуктовой аналитики.",
        "HSE Product Studio",
        "Москва",
        EventFormat.ONLINE,
        EventStatus.PUBLISHED,
        datetime(2026, 9, 18, 12),
        datetime(2026, 9, 18, 20),
        datetime(2026, 9, 12, 23, 59),
    ),
]

PROJECTS = [
    (
        "Campus Match",
        "Умный подбор студенческих проектов по навыкам, городу и роли.",
        "anna.sokolova@campus.demo",
        "Москва",
        "Campus Hack Spring 2026",
        ProjectType.STARTUP,
        ProjectFormat.HYBRID,
        ProjectStatus.NEW,
        datetime(2026, 7, 1, 23, 59),
    ),
    (
        "Study Buddy",
        "Сервис взаимопомощи для подготовки к экзаменам и проектным защитам.",
        "maria.kuznetsova@campus.demo",
        "Москва",
        "Product Research Day",
        ProjectType.STUDY,
        ProjectFormat.ONLINE,
        ProjectStatus.NEW,
        datetime(2026, 8, 15, 23, 59),
    ),
    (
        "Green Campus Map",
        "Карта инициатив устойчивого развития на территории университетов.",
        "polina.morozova@campus.demo",
        "Санкт-Петербург",
        None,
        ProjectType.STUDY,
        ProjectFormat.HYBRID,
        ProjectStatus.STARTED,
        datetime(2026, 9, 1, 23, 59),
    ),
    (
        "AI Tutor Lite",
        "Ассистент, который помогает студентам разбирать сложные темы короткими шагами.",
        "pavel.romanov@campus.demo",
        "Москва",
        "ITMO AI Challenge",
        ProjectType.HACKATHON,
        ProjectFormat.ONLINE,
        ProjectStatus.NEW,
        datetime(2026, 7, 10, 23, 59),
    ),
    (
        "Dorm Service Desk",
        "Единая витрина заявок по общежитиям, ремонтам и бытовым вопросам.",
        "timur.garipov@campus.demo",
        "Казань",
        "Kazan Startup Weekend",
        ProjectType.COMMERCIAL,
        ProjectFormat.HYBRID,
        ProjectStatus.SELECTION_COMPLETED,
        datetime(2026, 8, 30, 23, 59),
    ),
    (
        "Hackathon Radar",
        "Агрегатор соревнований, дедлайнов и командных вакансий.",
        "daria.volkova@campus.demo",
        "Казань",
        None,
        ProjectType.STARTUP,
        ProjectFormat.ONLINE,
        ProjectStatus.NEW,
        datetime(2026, 6, 30, 23, 59),
    ),
    (
        "Portfolio Builder",
        "Конструктор студенческого портфолио с экспортом в PDF и публичной ссылкой.",
        "ivan.petrov@campus.demo",
        "Санкт-Петербург",
        None,
        ProjectType.STARTUP,
        ProjectFormat.ONLINE,
        ProjectStatus.STARTED,
        datetime(2026, 10, 1, 23, 59),
    ),
    (
        "Secure Campus Wi-Fi",
        "Аудит и учебный стенд по безопасности университетских сетей.",
        "nikita.orlov@campus.demo",
        "Москва",
        None,
        ProjectType.STUDY,
        ProjectFormat.OFFLINE,
        ProjectStatus.NEW,
        datetime(2026, 9, 20, 23, 59),
    ),
    (
        "VR Lab Tour",
        "VR-экскурсия по лабораториям для абитуриентов и новых студентов.",
        "ksenia.popova@campus.demo",
        "Красноярск",
        None,
        ProjectType.STUDY,
        ProjectFormat.HYBRID,
        ProjectStatus.NEW,
        datetime(2026, 11, 15, 23, 59),
    ),
    (
        "Mobile Queue",
        "Мобильная запись в деканат, библиотеку и сервисные окна кампуса.",
        "sofia.lebedeva@campus.demo",
        "Томск",
        None,
        ProjectType.COMMERCIAL,
        ProjectFormat.HYBRID,
        ProjectStatus.NEW,
        datetime(2026, 8, 5, 23, 59),
    ),
    (
        "Event Pulse",
        "Аналитика регистрации и вовлеченности участников студенческих событий.",
        "alisa.fedorova@campus.demo",
        "Екатеринбург",
        None,
        ProjectType.STARTUP,
        ProjectFormat.ONLINE,
        ProjectStatus.STARTED,
        datetime(2026, 9, 30, 23, 59),
    ),
    (
        "Research Navigator",
        "Поиск научных руководителей, лабораторий и тем для студенческих исследований.",
        "sergey.nikolaev@campus.demo",
        "Томск",
        None,
        ProjectType.STUDY,
        ProjectFormat.ONLINE,
        ProjectStatus.NEW,
        datetime(2026, 12, 1, 23, 59),
    ),
]

VACANCIES = [
    (
        "Campus Match",
        "Backend-разработчик",
        2,
        ["Python", "FastAPI", "PostgreSQL"],
        "Нужен API для поиска, откликов и рекомендаций.",
    ),
    (
        "Campus Match",
        "UI/UX дизайнер",
        1,
        ["Figma", "UI/UX дизайн", "Исследования пользователей"],
        "Нужны прототипы сценариев подбора команды.",
    ),
    (
        "Study Buddy",
        "Product Manager",
        1,
        ["Product Management", "Бизнес-аналитика"],
        "Нужно оформить гипотезы и метрики ценности.",
    ),
    (
        "Study Buddy",
        "Frontend-разработчик",
        2,
        ["React", "TypeScript"],
        "Нужен личный кабинет и карточки учебных пар.",
    ),
    (
        "Green Campus Map",
        "Frontend-разработчик",
        1,
        ["Vue", "TypeScript", "UI/UX дизайн"],
        "Интерактивная карта и фильтры инициатив.",
    ),
    (
        "AI Tutor Lite",
        "ML-инженер",
        2,
        ["NLP", "Machine Learning", "Python"],
        "Нужен прототип пайплайна объяснений.",
    ),
    (
        "Dorm Service Desk",
        "DevOps-инженер",
        1,
        ["Docker", "DevOps", "PostgreSQL"],
        "Нужны окружения и мониторинг демо-стенда.",
    ),
    (
        "Hackathon Radar",
        "Data Scientist",
        1,
        ["Data Science", "Python", "Бизнес-аналитика"],
        "Нужно ранжировать события под интересы студента.",
    ),
    (
        "Portfolio Builder",
        "QA-инженер",
        1,
        ["QA", "Презентации"],
        "Нужен регресс ключевых сценариев портфолио.",
    ),
    (
        "Secure Campus Wi-Fi",
        "Backend-разработчик",
        1,
        ["Python", "Информационная безопасность"],
        "Нужен стенд с учебными сценариями аудита.",
    ),
    (
        "VR Lab Tour",
        "UI/UX дизайнер",
        1,
        ["AR/VR", "Figma", "Геймдизайн"],
        "Нужен маршрут и визуальные состояния VR-тура.",
    ),
    (
        "Mobile Queue",
        "Frontend-разработчик",
        1,
        ["Flutter", "Mobile"],
        "Нужно мобильное приложение для записи и статусов.",
    ),
    (
        "Event Pulse",
        "Data Scientist",
        1,
        ["Data Science", "PostgreSQL", "Презентации"],
        "Нужны витрины метрик и выводы по событиям.",
    ),
    (
        "Research Navigator",
        "ML-инженер",
        1,
        ["NLP", "Machine Learning", "Python"],
        "Нужен поиск похожих тем и научных направлений.",
    ),
]

APPLICATIONS = [
    (
        "Campus Match",
        "Backend-разработчик",
        "timur.garipov@campus.demo",
        ApplicationStatus.ACCEPTED,
    ),
    (
        "Campus Match",
        "Backend-разработчик",
        "denis.karpov@campus.demo",
        ApplicationStatus.PENDING,
    ),
    (
        "Campus Match",
        "UI/UX дизайнер",
        "polina.morozova@campus.demo",
        ApplicationStatus.PENDING,
    ),
    (
        "Study Buddy",
        "Product Manager",
        "viktoria.medvedeva@campus.demo",
        ApplicationStatus.ACCEPTED,
    ),
    (
        "Study Buddy",
        "Frontend-разработчик",
        "artem.belov@campus.demo",
        ApplicationStatus.PENDING,
    ),
    (
        "Green Campus Map",
        "Frontend-разработчик",
        "ivan.petrov@campus.demo",
        ApplicationStatus.ACCEPTED,
    ),
    (
        "AI Tutor Lite",
        "ML-инженер",
        "sergey.nikolaev@campus.demo",
        ApplicationStatus.PENDING,
    ),
    (
        "AI Tutor Lite",
        "ML-инженер",
        "egor.ivanov@campus.demo",
        ApplicationStatus.ACCEPTED,
    ),
    (
        "Dorm Service Desk",
        "DevOps-инженер",
        "denis.karpov@campus.demo",
        ApplicationStatus.ACCEPTED,
    ),
    (
        "Hackathon Radar",
        "Data Scientist",
        "yana.mikhailova@campus.demo",
        ApplicationStatus.PENDING,
    ),
    (
        "Portfolio Builder",
        "QA-инженер",
        "alisa.fedorova@campus.demo",
        ApplicationStatus.ACCEPTED,
    ),
    (
        "Secure Campus Wi-Fi",
        "Backend-разработчик",
        "nikita.orlov@campus.demo",
        ApplicationStatus.REJECTED,
    ),
    (
        "VR Lab Tour",
        "UI/UX дизайнер",
        "kirill.antonov@campus.demo",
        ApplicationStatus.PENDING,
    ),
    (
        "Mobile Queue",
        "Frontend-разработчик",
        "roman.smirnov@campus.demo",
        ApplicationStatus.PENDING,
    ),
    (
        "Event Pulse",
        "Data Scientist",
        "yana.mikhailova@campus.demo",
        ApplicationStatus.ACCEPTED,
    ),
    (
        "Research Navigator",
        "ML-инженер",
        "pavel.romanov@campus.demo",
        ApplicationStatus.PENDING,
    ),
]


async def bootstrap_demo_seed(session: AsyncSession) -> None:
    _validate_seed_shape()

    cities = await _ensure_cities(session)
    universities = await _ensure_universities(session, cities)
    skills = await _ensure_skills(session)
    team_roles = await _ensure_team_roles(session)
    user_role = await _get_default_user_role(session)
    users = await _ensure_users(session, cities, universities, skills, user_role)
    organizations = await _ensure_organizations(session, users)
    events = await _ensure_events(session, cities, organizations)
    projects = await _ensure_projects(session, cities, events, users)
    vacancies = await _ensure_vacancies(session, projects, team_roles, skills)
    await _ensure_applications(session, vacancies, users)
    await _ensure_team_members(session, projects, users, team_roles)
    await _ensure_portfolio_items(session, users, team_roles)

    await session.commit()


def _validate_seed_shape() -> None:
    if len(CITIES) != EXPECTED_CITY_COUNT:
        msg = "Demo seed must contain exactly 50 cities"
        raise ValueError(msg)
    if len(UNIVERSITIES) != EXPECTED_UNIVERSITY_COUNT:
        msg = "Demo seed must contain exactly 20 universities"
        raise ValueError(msg)


async def _ensure_cities(session: AsyncSession) -> dict[str, City]:
    result = await session.execute(select(City).where(City.name.in_(CITIES)))
    cities = {city.name: city for city in result.scalars().all()}
    for city_name in CITIES:
        if city_name not in cities:
            city = City(name=city_name)
            session.add(city)
            cities[city_name] = city
    await session.flush()
    return cities


async def _ensure_universities(
    session: AsyncSession,
    cities: dict[str, City],
) -> dict[str, University]:
    short_names = [short_name for _, short_name, _ in UNIVERSITIES]
    result = await session.execute(
        select(University).where(University.short_name.in_(short_names))
    )
    universities = {
        university.short_name: university for university in result.scalars().all()
    }

    for name, short_name, city_name in UNIVERSITIES:
        city = cities[city_name]
        university = universities.get(short_name)
        if university:
            university.name = name
            university.city = city
            continue
        university = University(name=name, short_name=short_name, city=city)
        session.add(university)
        universities[short_name] = university

    await session.flush()
    return universities


async def _ensure_skills(session: AsyncSession) -> dict[str, Skill]:
    result = await session.execute(select(Skill).where(Skill.name.in_(SKILLS)))
    skills = {skill.name: skill for skill in result.scalars().all()}
    for skill_name in SKILLS:
        if skill_name not in skills:
            skill = Skill(name=skill_name)
            session.add(skill)
            skills[skill_name] = skill
    await session.flush()
    return skills


async def _ensure_team_roles(session: AsyncSession) -> dict[str, TeamRole]:
    role_names = [name for name, _ in TEAM_ROLES]
    result = await session.execute(
        select(TeamRole).where(TeamRole.name.in_(role_names))
    )
    team_roles = {role.name: role for role in result.scalars().all()}

    for name, description in TEAM_ROLES:
        role = team_roles.get(name)
        if role:
            role.description = description
            continue
        role = TeamRole(name=name, description=description)
        session.add(role)
        team_roles[name] = role

    await session.flush()
    return team_roles


async def _get_default_user_role(session: AsyncSession) -> Role | None:
    result = await session.execute(select(Role).where(Role.name == "user"))
    user_role = result.scalar_one_or_none()
    if user_role:
        return user_role

    result = await session.execute(
        select(Role).where(Role.name == settings.rbac.public_role_name)
    )
    return result.scalar_one_or_none()


async def _ensure_users(
    session: AsyncSession,
    cities: dict[str, City],
    universities: dict[str, University],
    skills: dict[str, Skill],
    user_role: Role | None,
) -> dict[str, User]:
    emails = [email for email, *_ in USERS]
    result = await session.execute(
        select(User)
        .where(User.email.in_(emails))
        .options(
            selectinload(User.profile),
            selectinload(User.roles),
            selectinload(User.skills),
        )
    )
    users = {user.email: user for user in result.scalars().all()}
    password_hash = get_password_hash(DEMO_PASSWORD)

    for (
        email,
        first_name,
        last_name,
        city_name,
        university_short_name,
        skill_names,
    ) in USERS:
        user = users.get(email)
        if not user:
            user = User(
                email=email,
                password_hash=password_hash,
                is_active=True,
                is_verified=True,
                is_profile_completed=True,
            )
            session.add(user)
            users[email] = user
        else:
            user.is_active = True
            user.is_verified = True
            user.is_profile_completed = True

        if user_role and user_role not in user.roles:
            user.roles.append(user_role)

        user.skills = [skills[name] for name in skill_names]
        bio = (
            f"{first_name} участвует в студенческих проектах Campus и открыт(а) "
            "к командам, где можно быстро проверить продуктовую гипотезу."
        )
        if user.profile:
            user.profile.first_name = first_name
            user.profile.last_name = last_name
            user.profile.bio = bio
            user.profile.city = cities[city_name]
            user.profile.university = universities[university_short_name]
        else:
            user.profile = UserProfile(
                first_name=first_name,
                last_name=last_name,
                bio=bio,
                city=cities[city_name],
                university=universities[university_short_name],
            )

    await session.flush()
    return users


async def _ensure_organizations(
    session: AsyncSession,
    users: dict[str, User],
) -> dict[str, Organization]:
    names = [name for name, _, _ in ORGANIZATIONS]
    result = await session.execute(
        select(Organization).where(Organization.name.in_(names))
    )
    organizations = {
        organization.name: organization for organization in result.scalars().all()
    }

    for name, description, owner_email in ORGANIZATIONS:
        organization = organizations.get(name)
        owner = users[owner_email]
        contact_email = f"hello@{owner_email.split('@')[0].replace('.', '-')}.demo"
        if organization:
            organization.description = description
            organization.owner = owner
            organization.contact_email = contact_email
            continue
        organization = Organization(
            name=name,
            description=description,
            owner=owner,
            contact_email=contact_email,
        )
        session.add(organization)
        organizations[name] = organization

    await session.flush()
    return organizations


async def _ensure_events(
    session: AsyncSession,
    cities: dict[str, City],
    organizations: dict[str, Organization],
) -> dict[str, Event]:
    titles = [event[0] for event in EVENTS]
    result = await session.execute(select(Event).where(Event.title.in_(titles)))
    events = {event.title: event for event in result.scalars().all()}

    for (
        title,
        description,
        organization_name,
        city_name,
        event_format,
        status,
        date_start,
        date_end,
        application_deadline,
    ) in EVENTS:
        event = events.get(title)
        values: dict[str, Any] = {
            "description": description,
            "organizer": organizations[organization_name],
            "city": cities[city_name],
            "format": event_format,
            "status": status,
            "date_start": date_start,
            "date_end": date_end,
            "application_deadline": application_deadline,
            "registration_link": "https://campus.example/events",
        }
        if event:
            for field, value in values.items():
                setattr(event, field, value)
            continue
        event = Event(title=title, **values)
        session.add(event)
        events[title] = event

    await session.flush()
    return events


async def _ensure_projects(
    session: AsyncSession,
    cities: dict[str, City],
    events: dict[str, Event],
    users: dict[str, User],
) -> dict[str, Project]:
    titles = [project[0] for project in PROJECTS]
    result = await session.execute(select(Project).where(Project.title.in_(titles)))
    projects = {project.title: project for project in result.scalars().all()}

    for (
        title,
        description,
        owner_email,
        city_name,
        event_title,
        project_type,
        project_format,
        status,
        deadline,
    ) in PROJECTS:
        project = projects.get(title)
        values: dict[str, Any] = {
            "description": description,
            "owner": users[owner_email],
            "city": cities[city_name],
            "event": events[event_title] if event_title else None,
            "type": project_type,
            "format": project_format,
            "status": status,
            "deadline": deadline,
        }
        if project:
            for field, value in values.items():
                setattr(project, field, value)
            continue
        project = Project(title=title, **values)
        session.add(project)
        projects[title] = project

    await session.flush()
    return projects


async def _ensure_vacancies(
    session: AsyncSession,
    projects: dict[str, Project],
    team_roles: dict[str, TeamRole],
    skills: dict[str, Skill],
) -> dict[tuple[str, str], ProjectVacancy]:
    result = await session.execute(
        select(ProjectVacancy).options(
            joinedload(ProjectVacancy.project),
            joinedload(ProjectVacancy.team_role),
            selectinload(ProjectVacancy.skills),
        )
    )
    vacancies = {
        (vacancy.project.title, vacancy.team_role.name): vacancy
        for vacancy in result.scalars().all()
        if vacancy.project.title in projects
    }

    for project_title, role_name, required_count, skill_names, description in VACANCIES:
        key = (project_title, role_name)
        vacancy = vacancies.get(key)
        values: dict[str, Any] = {
            "project": projects[project_title],
            "team_role": team_roles[role_name],
            "required_count": required_count,
            "description": description,
        }
        if vacancy:
            for field, value in values.items():
                setattr(vacancy, field, value)
        else:
            vacancy = ProjectVacancy(**values)
            session.add(vacancy)
            vacancies[key] = vacancy
        vacancy.skills = [skills[name] for name in skill_names]

    await session.flush()
    return vacancies


async def _ensure_applications(
    session: AsyncSession,
    vacancies: dict[tuple[str, str], ProjectVacancy],
    users: dict[str, User],
) -> None:
    result = await session.execute(
        select(Application).options(
            joinedload(Application.vacancy).joinedload(ProjectVacancy.project),
            joinedload(Application.vacancy).joinedload(ProjectVacancy.team_role),
            joinedload(Application.applicant),
        )
    )
    applications = {
        (
            application.vacancy.project.title,
            application.vacancy.team_role.name,
            application.applicant.email,
        ): application
        for application in result.scalars().all()
    }

    for project_title, role_name, applicant_email, status in APPLICATIONS:
        key = (project_title, role_name, applicant_email)
        vacancy = vacancies[(project_title, role_name)]
        applicant = users[applicant_email]
        decided_at = (
            datetime(2026, 5, 20, 12) if status != ApplicationStatus.PENDING else None
        )
        cover_letter = (
            "Хочу присоединиться к команде: уже делал(а) похожие учебные "
            "проекты и могу быстро включиться в демо-версию."
        )
        application = applications.get(key)
        if application:
            application.status = status
            application.cover_letter = cover_letter
            application.decided_at = decided_at
            continue
        session.add(
            Application(
                vacancy=vacancy,
                applicant=applicant,
                cover_letter=cover_letter,
                status=status,
                decided_at=decided_at,
            )
        )

    await session.flush()


async def _ensure_team_members(
    session: AsyncSession,
    projects: dict[str, Project],
    users: dict[str, User],
    team_roles: dict[str, TeamRole],
) -> None:
    result = await session.execute(
        select(TeamMember).options(
            joinedload(TeamMember.project),
            joinedload(TeamMember.user),
        )
    )
    members = {
        (member.project.title, member.user.email): member
        for member in result.scalars().all()
        if member.project.title in projects
    }

    desired_members = [
        (project.title, project.owner.email, "Project Manager")
        for project in projects.values()
        if project.owner
    ]

    for project_title, role_name, applicant_email, status in APPLICATIONS:
        if status == ApplicationStatus.ACCEPTED:
            desired_members.append((project_title, applicant_email, role_name))

    for project_title, user_email, role_name in desired_members:
        key = (project_title, user_email)
        member = members.get(key)
        values: dict[str, Any] = {
            "project": projects[project_title],
            "user": users[user_email],
            "team_role": team_roles.get(role_name),
            "joined_at": datetime(2026, 5, 21, 10),
        }
        if member:
            for field, value in values.items():
                setattr(member, field, value)
            continue
        session.add(TeamMember(**values))

    await session.flush()


async def _ensure_portfolio_items(
    session: AsyncSession,
    users: dict[str, User],
    team_roles: dict[str, TeamRole],
) -> None:
    result = await session.execute(
        select(PortfolioItem).options(joinedload(PortfolioItem.user))
    )
    items = {
        (item.user.email, item.title): item
        for item in result.scalars().all()
        if item.user.email in users
    }

    portfolio_data = [
        (
            "anna.sokolova@campus.demo",
            "API для проектного маркетплейса",
            "Backend-разработчик",
        ),
        (
            "ivan.petrov@campus.demo",
            "Дизайн-система студенческого кабинета",
            "Frontend-разработчик",
        ),
        (
            "daria.volkova@campus.demo",
            "Модель рекомендаций хакатонов",
            "Data Scientist",
        ),
        ("timur.garipov@campus.demo", "CI/CD для учебного сервиса", "DevOps-инженер"),
        (
            "maria.kuznetsova@campus.demo",
            "Исследование потребностей первокурсников",
            "Product Manager",
        ),
        (
            "nikita.orlov@campus.demo",
            "Учебный стенд по безопасности API",
            "Backend-разработчик",
        ),
        ("polina.morozova@campus.demo", "Прототип карты кампуса", "UI/UX дизайнер"),
        (
            "egor.ivanov@campus.demo",
            "CV-модель для сортировки документов",
            "ML-инженер",
        ),
        (
            "alisa.fedorova@campus.demo",
            "План запуска университетского события",
            "Project Manager",
        ),
        ("sergey.nikolaev@campus.demo", "NLP-поиск по научным темам", "ML-инженер"),
    ]

    for email, title, role_name in portfolio_data:
        key = (email, title)
        description = (
            "Демо-кейс для проверки профиля кандидата и карточки участника "
            "в тестовой версии Campus."
        )
        values: dict[str, Any] = {
            "user": users[email],
            "team_role": team_roles[role_name],
            "description": description,
            "project_link": "https://campus.example/portfolio",
        }
        item = items.get(key)
        if item:
            for field, value in values.items():
                setattr(item, field, value)
            continue
        session.add(PortfolioItem(title=title, **values))

    await session.flush()
