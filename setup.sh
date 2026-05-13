#!/usr/bin/env bash

# Остановить выполнение при ошибке
set -e

# Цвета для красоты
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_DIR="/opt/PsinaBot"
echo -e "${BLUE}>>> Запуск процесса установки бота...${NC}"

# 1. Проверка на root
if [ "$EUID" -ne 0 ]; then
  echo "Пожалуйста, запустите скрипт от имени root (через sudo)"
  exit 1
fi

apt update && apt upgrade -y
apt install -y git curl

# 2. Создаем папку, если её нет (нужен root)
if [ ! -d "$PROJECT_DIR" ]; then
    echo "Создаю директорию в $PROJECT_DIR"
    mkdir -p "$PROJECT_DIR"
fi

cd "$PROJECT_DIR"

echo -e "${BLUE}>>> Загрузка проекта...${NC}"
if [ -z "$(ls -A .)" ]; then
    echo "Папка пуста, клонирую репозиторий..."
    git clone https://github.com/Flaimas/PsinaBot.git .
else
    echo "Проект уже на месте, обновляю..."
    git pull
fi

# 2. Установка Docker (если нет)
if ! command -v docker &> /dev/null; then
    echo -e "${BLUE}Установка Docker...${NC}"
    curl -fsSL https://get.docker.com | sh
fi

# 4. Создание .env файла
echo -e "${GREEN}Конфигурация окружения:${NC}"
read -p "Введите API токен бота: " BOT_TOKEN
echo -e "${BLUE}Создание .env файла...${NC}"
if [ ! -f .env ]; then
    cp .env.example .env
    sed -i "s/YOUR_BOT_TOKEN/$BOT_TOKEN/g" .env
fi

# 6. Запуск
echo -e "${GREEN}>>> Установка завершена! Запускаю контейнеры...${NC}"
docker compose up -d

echo -e "${GREEN}Бот успешно развернут в $PROJECT_DIR${NC}"