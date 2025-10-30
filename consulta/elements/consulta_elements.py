from time import sleep
from selenium.webdriver.common.by import By
from selenium_tools.page_objects import Element
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException, TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium_tools.page_objects import Page

from utils.utils import (
    donwload_htmlPDF,
    formatar_valor_brasileiro,
    resolve_image_captcha_numeric,
    select_element,
    formater_string,
    remove_left_zeros,
    formatar_data,
    formate_float,
    find_element_end_click,
)

from bs4 import BeautifulSoup

import requests


class loginElements(Page, Element):
    def navigate_to_login(self):
        iframe = self.find_element((By.ID, "menuFrame"))
        self.change_frame(iframe)

        self.find_element(
            (By.XPATH, "//div[@id='menuFrame']/descendant::a[position()=1]")
        ).click()

        self.driver.switch_to.default_content()

        iframe = self.find_element((By.ID, "mainFrame"))
        self.change_frame(iframe)

        self.find_element(
            (
                By.XPATH,
                "//div[@id='linkTable']/descendant::div[contains(@class, ' link-opc-Padrao')]/descendant::b[contains(text(), 'Acesso à Área Restrita')]",
            )
        ).click()

        self.driver.switch_to.default_content()

    def logar(self, usuario, senha):
        print("Iniciando login...")
        iframe = self.find_element(
            (By.ID, "mainFrame"), EC.presence_of_element_located, 30
        )
        self.change_frame(iframe)

        for i in range(10):
            try:
                self.find_element_and_clear(
                    (By.ID, "txtMatricula"), EC.presence_of_element_located, 30
                ).send_keys(usuario)
                break
            except Exception:
                print(f"Erro ao encontrar o campo de matrícula:{i}")
                sleep(.5)
        self.find_element(
            (By.ID, "txtSenha"), EC.presence_of_element_located, 30
        ).send_keys(senha)

        print("Iniciando resolucao de captcha...")
        count = 0
        for i in range(20):
            self.find_element(
                (By.ID, "imgCaptcha"), EC.visibility_of_element_located, 30
            )
            self.captcha_breaker(
                element=(By.ID, "imgCaptcha"),
                image_captcha_resolve=resolve_image_captcha_numeric,
                writter_element=(By.ID, "txtCodIma"),
            )
            find_element_end_click(self.driver, (By.ID, "botEntrar"), 30)
            print(f" {i + 1} - Tentativa de login...")

            try:
                alert = self.driver.switch_to.alert
                alert.accept()
                count += 1
            except NoAlertPresentException:
                break

            if count == 20:
                raise Exception("Não foi possível realizar o login.")

        self.driver.switch_to.default_content()
        print("Login concluido...")
