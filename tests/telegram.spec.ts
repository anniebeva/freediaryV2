import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:3000';

const TEST_USER = {
  email: 'user1@example.com',
  password: 'password123',
  username: 'testuser1'
};

test.describe('Интеграция с Telegram', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL);
  });

  test('Пользователь видит секцию Telegram в профиле', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill(TEST_USER.email);
    await page.getByLabel(/пароль/i).fill(TEST_USER.password);
    await page.getByRole('button', { name: /войти/i }).click();
    await expect(page).toHaveURL(/.*trainings/);

    await page.getByRole('link', { name: /профиль/i }).click();
    await expect(page).toHaveURL(/.*profile/);

    await expect(page.getByText(/telegram уведомления/i)).toBeVisible();
  });

  test('Пользователь может нажать кнопку "Привязать Telegram" и увидеть код', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill(TEST_USER.email);
    await page.getByLabel(/пароль/i).fill(TEST_USER.password);
    await page.getByRole('button', { name: /войти/i }).click();
    await expect(page).toHaveURL(/.*trainings/);

    await page.getByRole('link', { name: /профиль/i }).click();
    await expect(page).toHaveURL(/.*profile/);

    const linkBtn = page.getByRole('button', { name: /привязать telegram/i });
    await expect(linkBtn).toBeVisible();
    await linkBtn.click();
    
    // Ждём появления кода в UI (в div с классом bg-blue-50)
    await expect(page.locator('.bg-blue-50')).toBeVisible({ timeout: 10000 });
    
    // Проверяем, что код состоит из 6 символов
    const code = await page.locator('.text-blue-900.font-mono').textContent();
    expect(code).toBeTruthy();
    expect(code?.length).toBe(6);
  });

  test('Пользователь может отвязать Telegram (если он привязан)', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill(TEST_USER.email);
    await page.getByLabel(/пароль/i).fill(TEST_USER.password);
    await page.getByRole('button', { name: /войти/i }).click();
    await expect(page).toHaveURL(/.*trainings/);

    await page.getByRole('link', { name: /профиль/i }).click();
    await expect(page).toHaveURL(/.*profile/);

    const disconnectBtn = page.getByRole('button', { name: /отвязать telegram/i });
    
    if (await disconnectBtn.isVisible()) {
      // Обрабатываем диалог ДО клика
      const dialogPromise = page.waitForEvent('dialog');
      await disconnectBtn.click();
      const dialog = await dialogPromise;
      await dialog.accept();
      
      // Ждём, когда появится кнопка "Привязать Telegram"
      await expect(page.getByRole('button', { name: /привязать telegram/i })).toBeVisible({ timeout: 10000 });
    } else {
      test.skip(true, 'Telegram не привязан, тест пропущен');
    }
  });

  test('Пользователь без авторизации не может зайти в профиль', async ({ page }) => {
    await page.goto('/profile');
    await expect(page).toHaveURL(/.*login/);
  });
});