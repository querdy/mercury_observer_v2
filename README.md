# mercury_observer_v2

тг-бот для автоматизации отслеживания и приема заявок в ФГИС "Меркурий"

# Стек:
* python 3.11
* aiogram
* beautifulsoup4
* pydantic
* pymongo + motor

# Настройка:
.env-example заполнить и переименовать в .env

# Использование:
`/mercury_auth` - обновление данных для входа в ФГИС "Меркурий"  
`/milk` - сервис обработки заявок на сырое молоко.
Проверка происходит по:
* формат номера прицепа (если он есть)
* термическое состояние
* дате ТТН (timedelta < 2 сут)
* наименованию продукта
* цели
* статусу ВСЭ
* сроку годности (+ дата выработки не из будущего)
