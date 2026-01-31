"""
from django.test import TestCase
from django.urls import reverse

class PollsTest(TestCase):
    def test_admin_accessible(self):
        response = self.client.get('/admin/login/')
        self.assertEqual(response.status_code, 200)
"""

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class StaffFullFlowTests(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opts = Options()
        opts.add_argument("--headless")  # activar en CI
        cls.selenium = WebDriver(options=opts)
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        self.admin_user = "isard"
        self.admin_pass = "pirineus789"

        if not User.objects.filter(username=self.admin_user).exists():
            User.objects.create_superuser(
                username=self.admin_user,
                email="isard@test.local",
                password=self.admin_pass
            )

    def test_complete_isard_to_staff_flow(self):
        wait = WebDriverWait(self.selenium, 30)

        staff_user = "staff_tester_eac"
        staff_pass = "DjanGo_2026_Secure!"

        # ───────── FASE 1: LOGIN ADMIN ─────────
        self.selenium.get(f"{self.live_server_url}/admin/login/")
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        wait.until(EC.presence_of_element_located((By.NAME, "username")))

        self.selenium.find_element(By.NAME, "username").send_keys(self.admin_user)
        self.selenium.find_element(By.NAME, "password").send_keys(self.admin_pass)
        self.selenium.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()

        # ───────── FASE 2: CREAR USUARIO STAFF ─────────
        wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'a[href="/admin/auth/user/add/"]'))
        ).click()

        wait.until(EC.presence_of_element_located((By.NAME, "username")))
        self.selenium.find_element(By.NAME, "username").send_keys(staff_user)
        self.selenium.find_element(By.NAME, "password1").send_keys(staff_pass)
        self.selenium.find_element(By.NAME, "password2").send_keys(staff_pass)
        self.selenium.find_element(By.NAME, "_continue").click()

        # ───────── FASE 3: ASIGNAR PERMISOS ─────────
        staff_checkbox = wait.until(
            EC.element_to_be_clickable((By.NAME, "is_staff"))
        )
        if not staff_checkbox.is_selected():
            staff_checkbox.click()

        perm_from = self.selenium.find_element(By.ID, "id_user_permissions_from")

        for option in perm_from.find_elements(By.TAG_NAME, "option"):
            text = option.text.lower()
            if (
                "add user" in text or
                "view user" in text or
                "view question" in text
            ):
                option.click()

        self.selenium.find_element(
            By.ID, "id_user_permissions_add_link"
        ).click()

        self.selenium.find_element(By.NAME, "_save").click()

        # ───────── FASE 4: LOGOUT ADMIN (FORZADO, ESTABLE) ─────────
        self.selenium.delete_all_cookies()
        self.selenium.get(f"{self.live_server_url}/admin/login/")
        wait.until(EC.presence_of_element_located((By.NAME, "username")))

        # ───────── FASE 5: LOGIN STAFF ─────────
        self.selenium.find_element(By.NAME, "username").send_keys(staff_user)
        self.selenium.find_element(By.NAME, "password").send_keys(staff_pass)
        self.selenium.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()

        wait.until(EC.presence_of_element_located((By.ID, "content-main")))

        # ───────── FASE 6: VERIFICACIONES ─────────

        # Puede ver Users
        assert self.selenium.find_elements(By.LINK_TEXT, "Users")

        # Puede añadir Users
        assert self.selenium.find_elements(
            By.CSS_SELECTOR,
            'a[href="/admin/auth/user/add/"]'
        )

        # Puede ver Questions
        assert self.selenium.find_elements(By.LINK_TEXT, "Questions")

        # NO puede añadir Questions
        assert not self.selenium.find_elements(
            By.CSS_SELECTOR,
            'a[href="/admin/polls/question/add/"]'
        )

        print("\n[OK] Test E2E de permisos staff ejecutado correctamente")
