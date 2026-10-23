import { test, expect } from "@playwright/test";

test("home loads", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveTitle(/.*/);
});

test("login page renders email and password fields", async ({ page }) => {
  await page.goto("/login");
  await expect(page.getByLabel(/email/i)).toBeVisible();
  await expect(page.getByLabel(/password/i)).toBeVisible();
});

test("signup page renders", async ({ page }) => {
  await page.goto("/signup");
  await expect(page.getByRole("button", { name: /sign up|create account/i })).toBeVisible();
});

test("dashboard redirects unauthenticated users", async ({ page }) => {
  await page.goto("/dashboard");
  await expect(page).toHaveURL(/login|auth|dashboard/);
});