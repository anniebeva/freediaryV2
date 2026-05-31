import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:3000';

const TEST_USER = {
  email: 'user1@example.com',
  password: 'password123',
  username: 'testuser1'
};

test.describe('Страница статистики', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL);
  });

  test('Пользователь переходит на страницу статистики, видит цифры (количество тренировок)', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill(TEST_USER.email);
    await page.getByLabel(/пароль/i).fill(TEST_USER.password);
    await page.getByRole('button', { name: /войти/i }).click();
    await expect(page).toHaveURL(/.*trainings/);

    await page.getByRole('link', { name: /статистика/i }).click();
    await expect(page).toHaveURL(/.*stats/);

    await expect(page.getByText(/статистика тренировок/i)).toBeVisible();
    await expect(page.getByText(/общая статистика/i)).toBeVisible();
    await expect(page.getByText(/всего тренировок: \d+/i)).toBeVisible();
    await expect(page.getByText(/средняя сложность: \d+\.\d\/5/i)).toBeVisible();
    await expect(page.getByText(/тренировки по типам/i)).toBeVisible();
  });

  test('Пользователь видит статистику по типам тренировок', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill(TEST_USER.email);
    await page.getByLabel(/пароль/i).fill(TEST_USER.password);
    await page.getByRole('button', { name: /войти/i }).click();
    await expect(page).toHaveURL(/.*trainings/);

    await page.getByRole('link', { name: /статистика/i }).click();
    await expect(page).toHaveURL(/.*stats/);

    // Проверяем, что блок "Тренировки по типам" виден
    await expect(page.getByText(/тренировки по типам/i)).toBeVisible();
    
    // Проверяем, что есть хотя бы одна запись о типе тренировки (Pool, Depth или Gym)
    const hasPool = await page.getByText(/Pool:/i).count();
    const hasDepth = await page.getByText(/Depth:/i).count();
    const hasGym = await page.getByText(/Gym:/i).count();
    
    expect(hasPool + hasDepth + hasGym).toBeGreaterThan(0);
  });

  test('Пользователь без авторизации не может получить доступ к странице статистики', async ({ page }) => {
    await page.goto(`${BASE_URL}/stats`);
    await expect(page).toHaveURL(/.*login/);
  });
});