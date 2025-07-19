# Этап 1: Builder - установка зависимостей
FROM python:3.12-bookworm AS builder

# Устанавливаем Poetry
ENV POETRY_HOME="/opt/poetry"
# ИСПРАВЛЕНА ОПЕЧАТКА: POETRY вместо PORY
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV POETRY_NO_INTERACTION=1
RUN curl -sSL https://install.python-poetry.org | python -

# Добавляем Poetry в системный PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем только файлы, необходимые для установки зависимостей
# Это улучшает кэширование Docker. Зависимости не будут переустанавливаться,
# если изменится только исходный код.
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости
# --no-root означает, что Poetry не будет устанавливать сам проект, только зависимости
RUN poetry install --no-root --sync

# Копируем остальной код проекта
COPY . .


# Этап 2: Production - запуск приложения
FROM python:3.12-bookworm AS production

WORKDIR /app

# Копируем созданное виртуальное окружение из этапа builder
COPY --from=builder /app/.venv /app/.venv
# Копируем исходный код приложения из этапа builder
COPY --from=builder /app .

# Добавляем venv в системный PATH, чтобы команды (uvicorn, python)
# выполнялись из него
ENV PATH="/app/.venv/bin:$PATH"

# Создаем пользователя и группу с системными правами и меняем владельца файлов
# Это делается от root перед переключением на appuser
RUN adduser --system --group appuser && \
    chown -R appuser:appuser /app && \
    chmod a+x ./docker/*.sh && \
    chmod a+x ./src/main_bot.py