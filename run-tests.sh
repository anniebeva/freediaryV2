#!/bin/bash

# Скрипт для запуска E2E тестов FreeDiary

echo "========================================="
echo "Запуск E2E тестов для FreeDiary"
echo "========================================="

# Проверка наличия Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js не установлен. Установите Node.js 16+"
    exit 1
fi

echo "✅ Node.js установлен: $(node --version)"

# Проверка наличия Python
if ! command -v python &> /dev/null; then
    echo "❌ Python не установлен. Установите Python 3.8+"
    exit 1
fi

echo "✅ Python установлен: $(python --version)"

# Проверка запущенных серверов
echo ""
echo "Проверка запущенных серверов..."

# Проверка фронтенда (порт 3000)
if ! curl -s http://localhost:3000 > /dev/null; then
    echo "⚠️  Фронтенд не запущен на порту 3000"
    echo "   Запустите: npm start (в отдельном терминале)"
fi

# Проверка бэкенда (порт 8000)
if ! curl -s http://localhost:8000/docs > /dev/null; then
    echo "⚠️  Бэкенд не запущен на порту 8000"
    echo "   Запустите: cd backend && python -m uvicorn main:app --reload --port 8000 (в отдельном терминале)"
fi

echo ""
echo "Установка зависимостей..."
npm install

echo ""
echo "Установка браузеров Playwright..."
npm run playwright:install-chromium

echo ""
echo "Запуск seed-данных..."
cd backend && python seed.py && cd ..

echo ""
echo "Выберите режим запуска тестов:"
echo "1) Все тесты"
echo "2) Только авторизация"
echo "3) Только тренировки"
echo "4) Только статистика"
echo "5) Только Telegram"
echo "6) Тесты с UI-отладчиком"
echo "7) Тесты в режиме отладки"
echo "8) Пропустить тесты Telegram"
echo "9) Выход"

read -p "Введите номер (1-9): " choice

case $choice in
    1)
        echo "Запуск всех тестов..."
        npm run test:e2e
        ;;
    2)
        echo "Запуск тестов авторизации..."
        npx playwright test tests/auth.spec.ts
        ;;
    3)
        echo "Запуск тестов тренировок..."
        npx playwright test tests/trainings.spec.ts
        ;;
    4)
        echo "Запуск тестов статистики..."
        npx playwright test tests/stats.spec.ts
        ;;
    5)
        echo "Запуск тестов Telegram..."
        npx playwright test tests/telegram.spec.ts
        ;;
    6)
        echo "Запуск тестов с UI-отладчиком..."
        npm run test:e2e:ui
        ;;
    7)
        echo "Запуск тестов в режиме отладки..."
        npm run test:e2e:debug
        ;;
    8)
        echo "Запуск тестов с пропуском Telegram..."
        SKIP_TELEGRAM_TESTS=true npm run test:e2e
        ;;
    9)
        echo "Выход..."
        exit 0
        ;;
    *)
        echo "Неверный выбор. Запуск всех тестов по умолчанию..."
        npm run test:e2e
        ;;
esac

echo ""
echo "========================================="
echo "Тесты завершены!"
echo "========================================="
echo ""
echo "Дополнительные команды:"
echo "• Просмотр отчета: open playwright-report/index.html"
echo "• Очистка результатов: rm -rf test-results/ playwright-report/"
echo "• Установка всех браузеров: npm run playwright:install"
echo ""
echo "Для повторного запуска: ./run-tests.sh"