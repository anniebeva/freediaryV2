import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:3000';

const TEST_USER = {
  email: 'user1@example.com',
  password: 'password123',
  username: 'testuser1'
};

const NEW_USER = {
  email: `test_${Date.now()}@example.com`,
  password: 'newpassword123',
  username: `testuser_${Date.now()}`
};

test.describe('Авторизация и регистрация', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL);
  });

  test('Пользователь регистрируется с валидными данными и автоматически попадает на страницу списка тренировок', async ({ page }) => {
    await page.getByRole('link', { name: /регистрация/i }).click();
    await expect(page).toHaveURL(/.*register/);

    await page.getByLabel(/имя пользователя/i).fill(NEW_USER.username);
    await page.getByLabel(/email/i).fill(NEW_USER.email);
    await page.getByLabel('Пароль', { exact: true }).fill(NEW_USER.password);
    await page.locator('#confirmPassword').fill(NEW_USER.password);

    await page.getByRole('button', { name: /зарегистрироваться/i }).click();

    await expect(page).toHaveURL(/.*trainings/);
    await expect(page.getByText(/мои тренировки/i)).toBeVisible();
  });

  test('Пользователь входит в систему с существующим email и паролем, переходит на страницу тренировок', async ({ page }) => {
    await page.goto('/login');
    await expect(page).toHaveURL(/.*login/);

    await page.getByLabel(/email/i).fill(TEST_USER.email);
    await page.getByLabel(/пароль/i).fill(TEST_USER.password);
    await page.getByRole('button', { name: /войти/i }).click();

    await expect(page).toHaveURL(/.*trainings/);
    await expect(page.getByText(/мои тренировки/i)).toBeVisible();
  });

  test('Пользователь не может войти с неверными данными', async ({ page }) => {
    await page.goto('/login');
    
    await page.getByLabel(/email/i).fill('wrong@example.com');
    await page.getByLabel(/пароль/i).fill('wrongpassword');
    
    await page.getByRole('button', { name: /войти/i }).click();

    await expect(page).toHaveURL(/.*login/);
    await expect(page.getByText(/неверный email или пароль/i)).toBeVisible();
  });

  test('Пользователь выходит из системы', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill(TEST_USER.email);
    await page.getByLabel(/пароль/i).fill(TEST_USER.password);
    await page.getByRole('button', { name: /войти/i }).click();
    await expect(page).toHaveURL(/.*trainings/);

    await page.getByRole('button', { name: /выйти/i }).click();

    await expect(page).toHaveURL(/.*login/);
    await expect(page.getByRole('heading', { name: /вход/i })).toBeVisible();
  });
});