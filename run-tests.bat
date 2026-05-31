@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo =========================================
echo Запуск E2E тестов для FreeDiary
echo =========================================

REM Проверка наличия Node.js
where node >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js не установлен. Установите Node.js 16+
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo ✅ Node.js установлен: !NODE_VERSION!

REM Проверка наличия Python
where python >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не установлен. Установите Python 3.8+
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python установлен: !PYTHON_VERSION!

echo.
echo Установка зависимостей...
call npm install

echo.
echo Установка браузеров Playwright...
call npx playwright install chromium

echo.
echo Запуск серверов...

REM Запуск бэкенда в отдельном окне
start "FreeDiary Backend" cmd /c "cd backend && python -m uvicorn main:app --reload --port 8000"

REM Ждем запуска бэкенда
echo Ожидание запуска бэкенда на порту 8000...
:wait_backend
timeout /t 2 /nobreak >nul
curl -s http://localhost:8000/docs >nul 2>&1
if errorlevel 1 goto wait_backend
echo ✅ Бэкенд запущен

REM Запуск фронтенда в отдельном окне
start "FreeDiary Frontend" cmd /c "cd frontend && npm start"

REM Ждем запуска фронтенда
echo Ожидание запуска фронтенда на порту 3000...
:wait_frontend
timeout /t 2 /nobreak >nul
curl -s http://localhost:3000 >nul 2>&1
if errorlevel 1 goto wait_frontend
echo ✅ Фронтенд запущен

echo.
echo Запуск seed-данных...
cd backend
call python seed.py
cd ..

echo.
echo Выберите режим запуска тестов:
echo 1) Все тесты
echo 2) Только авторизация
echo 3) Только тренировки
echo 4) Только статистика
echo 5) Только Telegram
echo 6) Тесты с UI-отладчиком
echo 7) Тесты в режиме отладки
echo 8) Пропустить тесты Telegram
echo 9) Выход

set /p choice="Введите номер (1-9): "

if "%choice%"=="1" (
    echo Запуск всех тестов...
    call npx playwright test
) else if "%choice%"=="2" (
    echo Запуск тестов авторизации...
    call npx playwright test tests/auth.spec.ts
) else if "%choice%"=="3" (
    echo Запуск тестов тренировок...
    call npx playwright test tests/trainings.spec.ts
) else if "%choice%"=="4" (
    echo Запуск тестов статистики...
    call npx playwright test tests/stats.spec.ts
) else if "%choice%"=="5" (
    echo Запуск тестов Telegram...
    call npx playwright test tests/telegram.spec.ts
) else if "%choice%"=="6" (
    echo Запуск тестов с UI-отладчиком...
    call npx playwright test --ui
) else if "%choice%"=="7" (
    echo Запуск тестов в режиме отладки...
    call npx playwright test --debug
) else if "%choice%"=="8" (
    echo Запуск тестов с пропуском Telegram...
    set SKIP_TELEGRAM_TESTS=true
    call npx playwright test
) else if "%choice%"=="9" (
    echo Выход...
    pause
    exit /b 0
) else (
    echo Неверный выбор. Запуск всех тестов по умолчанию...
    call npx playwright test
)

echo.
echo =========================================
echo Тесты завершены!
echo =========================================
echo.
echo Дополнительные команды:
echo • Просмотр отчета: start playwright-report\index.html
echo • Очистка результатов: rmdir /s /q test-results playwright-report
echo.

REM Спрашиваем, закрыть ли серверы
set /p close_servers="Закрыть окна серверов? (Y/N): "
if /i "%close_servers%"=="Y" (
    taskkill /f /fi "WINDOWTITLE eq FreeDiary Backend" >nul 2>&1
    taskkill /f /fi "WINDOWTITLE eq FreeDiary Frontend" >nul 2>&1
    echo ✅ Серверы закрыты
)

pause