# 🎵 WaveFlow — MusicAI

<div align="center">

![WaveFlow](https://img.shields.io/badge/WaveFlow-MusicAI-ff3d5a?style=for-the-badge&logo=music&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)
![Status](https://img.shields.io/badge/Status-MVP-orange?style=for-the-badge)

**Слушай музыку прямо в браузере. ИИ-агент собирает плейлисты по твоему описанию. Данные — только из YouTube Music.**

[🐛 Сообщить о баге](../../issues) · [💡 Предложить идею](../../issues)

</div>

---

## 📌 О проекте

**WaveFlow / MusicAI** — это веб-сервис с тёмным premium-интерфейсом, встроенным аудиоплеером и ИИ-агентом для создания плейлистов. Не нужно переходить на YouTube Music — слушай прямо здесь, пиши агенту что хочешь услышать, выбирай модель ИИ под свой запрос.

> ⚠️ Все треки и метаданные поступают исключительно из **YouTube Music**. Проект создан в образовательных целях.

---

## ✨ Что умеет

| Функция | Описание |
|---|---|
| 🎧 Встроенный плеер | Слушай музыку прямо в браузере — без переходов на YouTube |
| 🤖 ИИ-агент плейлистов | Пишешь описание → агент собирает плейлист из базы YT Music |
| 🧠 Выбор модели ИИ | GPT-4o, GPT-4o-mini, Claude, Ollama — переключаешь прямо в интерфейсе |
| 📊 Рекомендации | ML-подборки на основе истории прослушиваний и лайков |
| 🔍 Каталог | Поиск и фильтрация по всей базе YouTube Music |
| ❤️ Моя музыка | Лайки, история, сохранённые плейлисты |

---

## 🎨 Дизайн — WaveFlow

Интерфейс построен по концепции **"Midnight recording studio meets Tokyo club"**:

- Глубокий тёмный фон `#07070d` с mesh-градиентами и film grain текстурой
- Акцент: коралловый `#ff3d5a` · холодный синий `#00d4ff` · фиолетовый `#7b2fff`
- Шрифты: **Syne** (заголовки) · **Cabinet Grotesk** (текст) · **DM Mono** (метаданные)
- Glassmorphism панели, анимированные waveform-бары, вращающийся vinyl-диск в плеере
- Карточки треков с hover-эффектами и плавными переходами

---

## 🗂️ Структура проекта

```
MusicAi/
├── main.py              # Точка входа — Flask сервер
├── requirements.txt     # Python-зависимости
├── templates/
│   └── index.html       # Весь интерфейс WaveFlow (HTML + CSS + JS)
├── .env.example         # Шаблон переменных окружения
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🚀 Установка и запуск

### Требования

- Python **3.10** или новее
- pip

### Шаг 1 — Клонировать репозиторий

```bash
git clone https://github.com/broimdead89-spec/MusicAi.git
cd MusicAi
```

### Шаг 2 — Создать виртуальное окружение

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### Шаг 3 — Установить зависимости

```bash
pip install -r requirements.txt
```

### Шаг 4 — Настроить переменные окружения

Скопируй `.env.example` в `.env` и заполни:

```bash
cp .env.example .env
```

```env
# YouTube Music (куки из браузера)
# Инструкция: https://ytmusicapi.readthedocs.io/en/stable/setup/browser.html
YTM_COOKIE=

# Выбор провайдера ИИ: openai / anthropic / ollama
AI_PROVIDER=openai

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Anthropic Claude (опционально)
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-haiku-20241022

# Ollama — локальная модель (опционально)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1

# JWT
SECRET_KEY=замени-на-случайную-строку
```

### Шаг 5 — Запустить

```bash
python main.py
```

Открой браузер: **http://localhost:5000**

---

## 🔑 Как получить куки YouTube Music

1. Открой [music.youtube.com](https://music.youtube.com) и войди в аккаунт
2. Нажми **F12** → вкладка **Network**
3. Обнови страницу, найди любой запрос к `music.youtube.com`
4. В заголовках запроса скопируй значение `Cookie:`
5. Вставь в `.env` → `YTM_COOKIE=...`

---

## 🧠 Доступные модели ИИ

В правом верхнем углу интерфейса есть выпадающий список — переключай модели на лету:

| Модель | Провайдер | Когда использовать |
|---|---|---|
| `gpt-4o-mini` | OpenAI | Быстро и дёшево, для большинства запросов |
| `gpt-4o` | OpenAI | Сложные описания, точный подбор |
| `claude-3-5-haiku` | Anthropic | Хорошо понимает контекст и настроение |
| `llama3.1` | Ollama | Без интернета, полностью приватно |

Заполни нужные ключи в `.env` — модели появятся в списке автоматически.

---

## 🎧 Встроенный плеер

Музыка играет **прямо в браузере** — никаких редиректов:

- Фиксированная нижняя панель: обложка, название трека, прогресс-бар, управление
- Обложка вращается пока играет (vinyl-анимация)
- Waveform-визуализатор с анимированными барами
- Управление: ⏮ предыдущий · ⏯ пауза · ⏭ следующий · 🔊 громкость · ❤️ лайк

---

## 🤖 Примеры запросов к ИИ-агенту

```
"Подбери плейлист для утренней пробежки, энергичный, без слов, ~30 минут"
"Хочу что-то меланхоличное в стиле инди для осеннего вечера"
"Лоуфай для работы или учёбы, не больше 40 минут"
"Ретро 80-х, что-то танцевальное"
```

Агент анализирует описание, подбирает треки из базы YouTube Music и показывает плейлист справа — карточка за карточкой, в реальном времени. Можно уточнять: *«добавь больше женских вокалов»*, *«убери медленные треки»*.

---

## 🛣️ Что планируется

- [ ] Полноценный React-фронтенд
- [ ] PostgreSQL вместо SQLite
- [ ] Docker для быстрого деплоя
- [ ] Экспорт плейлиста обратно в YouTube Music
- [ ] Ambient color mode — интерфейс меняет цвет под обложку
- [ ] Мобильная версия

---

## 🤝 Участие в разработке

```bash
git checkout -b feature/название-фичи
git commit -m "feat: описание изменения"
git push origin feature/название-фичи
# → создать Pull Request на GitHub
```

---

## 📄 Лицензия

MIT — смотрите файл [LICENSE](LICENSE).

---

<div align="center">
Сделано с ❤️ и помощью Claude (Anthropic)
</div>
