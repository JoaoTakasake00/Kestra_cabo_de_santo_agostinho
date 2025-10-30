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

class ConsultaElement(Element):
    def navigate_to_declaracao(self):
        print("Iniciando navegacao para declaracao...")
        iframe = self.find_element((By.XPATH, "//iframe[contains(@id, 'iFrame')]"))
        self.change_frame(iframe)

        iframe = self.find_element(
            (By.XPATH, "//table[@id='tblIndex']/descendant::iframe[position()=1]")
        )
        self.change_frame(iframe)

        find_element_end_click(
            self.driver,
            (
                By.XPATH,
                "//h3[contains(@id, 'foldheaderI') and contains(text(), 'DEMS')]/following-sibling::ul[contains(@class, 'menu-list') and position()=1]/descendant::li[contains(@id, 'foldheader') and position()=1]",
            ),
            30,
        )

        find_element_end_click(
            self.driver,
            (
                By.XPATH,
                "//h3[contains(@id, 'foldheaderI') and contains(text(), 'DEMS')]/following-sibling::ul[contains(@class, 'menu-list') and position()=1]/descendant::ul[contains(@id, 'foldinglist') and position()=1]/descendant::a[contains(text(), 'Declaração') and position()=1]",
            ),
            30,
        )

        self.driver.switch_to.default_content()
        print("Navegacao para declaracao concluida...")

    def select_contribuinte(self, mes_competencia, ano_competencia):
        print("Iniciando selecao de contribuinte...")
        iframe = self.find_element((By.XPATH, "//iframe[contains(@id, 'iFrame')]"))
        self.change_frame(iframe)

        iframe = self.find_element(
            (By.XPATH, "//table[@id='tblIndex']/descendant::iframe[position()=2]")
        )
        self.change_frame(iframe)

        self.find_element((By.ID, "botLimpar")).click()

        mes_competencia = int(mes_competencia)

        mes_competencia = {
            1: "Janeiro",
            2: "Fevereiro",
            3: "Março",
            4: "Abril",
            5: "Maio",
            6: "Junho",
            7: "Julho",
            8: "Agosto",
            9: "Setembro",
            10: "Outubro",
            11: "Novembro",
            12: "Dezembro",
        }[mes_competencia]

        competencia = f"{mes_competencia}/{ano_competencia.strip()}"

        select_element(self.driver, "partial_text", (By.ID, "cboContInsc"), "DEXCO", 10)
        select_element(
            self.driver, "partial_text", (By.ID, "cboContComp"), competencia, 10
        )

        self.find_element(
            (
                By.XPATH,
                "//div[@id='Pagina']/descendant::div[contains(text(), 'DECLARAÇÃO ELETRÔNICA MENSAL DE SERVIÇOS')]/ancestor::div[position()=1]/descendant::td[contains(text(), 'NFS-e do município Recebida')]",
            )
        ).click()

        self.driver.switch_to.default_content()
        print("Selecao de contribuinte concluida...")

    def get_nfs_municipal(self):
        print("Iniciando captura de NFs municipais...")
        iframe = self.find_element((By.XPATH, "//iframe[contains(@id, 'iFrame')]"))
        self.change_frame(iframe)

        iframe = self.find_element(
            (By.XPATH, "//table[@id='tblIndex']/descendant::iframe[position()=2]")
        )
        self.change_frame(iframe)

        # Remover a barra de rolagem
        self.driver.execute_script(
            """let elem = document.getElementById('lblDNGrid'); elem.style.removeProperty('height');"""
        )

        table_element = self.find_element((By.ID, "lblDNGrid"))

        html = table_element.get_attribute("outerHTML")
        soup = BeautifulSoup(html, "html.parser")

        # Encontrar o primeiro <tr> e remover ele do documento
        primeiro_tr = soup.find("tr")
        if primeiro_tr:
            primeiro_tr.decompose()

        trs = soup.find_all("tr")

        # captura os dados da tabela
        dados_NFs_recebidas_do_municipio = []
        for tr in trs:
            tds = tr.find_all("td")
            if tds:
                primeira_td = tds[0]
                label = primeira_td.find("label")
                if label:
                    dado_label = label.get_text(strip=True)

            outros_dados = []
            for td in tds[1:]:
                texto_td = td.get_text(strip=True)
                outros_dados.append(texto_td)

            dados_NFs_recebidas_do_municipio.append((dado_label, *outros_dados))

        self.driver.switch_to.default_content()

        print("Captura de NFs municipais concluida...")
        return dados_NFs_recebidas_do_municipio

    def get_nfs_prefeitura(self):
        print("Iniciando captura de NFs prefeitura...")
        iframe = self.find_element((By.XPATH, "//iframe[contains(@id, 'iFrame')]"))
        self.change_frame(iframe)

        iframe = self.find_element(
            (By.XPATH, "//table[@id='tblIndex']/descendant::iframe[position()=2]")
        )
        self.change_frame(iframe)

        self.find_element(
            (
                By.XPATH,
                "//div[@id='Pagina']/descendant::div[contains(text(), 'DECLARAÇÃO ELETRÔNICA MENSAL DE SERVIÇOS')]/ancestor::div[position()=1]/descendant::td[contains(text(), 'Doc. Recebido')]",
            )
        ).click()

        # Remover a barra de rolagem
        self.driver.execute_script(
            """let elem = document.getElementById('lblDRGrid'); elem.style.removeProperty('height');"""
        )

        table_element = self.find_element((By.ID, "lblDRGrid"))

        html = table_element.get_attribute("outerHTML")
        soup = BeautifulSoup(html, "html.parser")

        # Encontrar o primeiro <tr> e remover ele do documento
        primeiro_tr = soup.find("tr")
        if primeiro_tr:
            primeiro_tr.decompose()

        trs = soup.find_all("tr")

        # captura os dados da tabela
        dados_NFs_prefeitura = []
        for tr in trs:
            tds = tr.find_all("td")
            if tds:
                primeira_td = tds[0]
                label = primeira_td.find("label")
                if label:
                    dado_label = label.get_text(strip=True)

            outros_dados = []
            for td in tds[1:]:
                texto_td = td.get_text(strip=True)
                outros_dados.append(texto_td)

            dados_NFs_prefeitura.append((dado_label, *outros_dados))

        self.driver.switch_to.default_content()

        print("Captura de NFs prefeitura concluida...")
        return dados_NFs_prefeitura

    def mounted_json_nfs_municipal(self, dados_NFs, dados_NFs_prefeitura, cnpj_filial, nome_municipio):
        print("Iniciando formatacao de NFs municipais...")
        tabela_json = {"tabela": []}

        all_dados_NFs = []
        all_dados_NFs.append(dados_NFs)
        all_dados_NFs.append(dados_NFs_prefeitura)

        print(f"NFs municipais: {len(dados_NFs)}")
        print(f"NFs prefeitura: {len(dados_NFs_prefeitura)}")

        for index_nfs, dados_NFs in enumerate(all_dados_NFs):
            for dados in dados_NFs:
                if len(dados) < 11:
                    continue  
                for index, dado in enumerate(dados):
                    if index_nfs == 0:
                        match index:
                            case 0:
                                numero_nota = dado
                                numero_nota_formatado = remove_left_zeros(dado)
                            case 1:
                                competencia = dado
                                competencia_formatada = formatar_data(dado, "d/m/y", "m/y")
                            case 2:
                                split_dado = dado.split(" - ")
                                cnpj_prestador_formatado = formater_string(split_dado[0])
                                prestador = split_dado[2] if len(split_dado) >= 3 else ""
                            case 3:
                                valor_servico = formate_float(dado)
                            case 5:
                                aliquota = formate_float(dado)
                            case 6:
                                valor_ISSQN = formate_float(dado)
                            case 8:
                                retido = "R" if dado.upper() == "SIM" else "N"
                    else:
                        match index:
                            case 3:
                                numero_nota = dado
                                numero_nota_formatado = remove_left_zeros(dado)
                            case 4:
                                competencia = dado
                                competencia_formatada = formatar_data(dado, "d/m/y", "m/y")
                            case 5:
                                split_dado = dado.split(" - ")
                                cnpj_prestador_formatado = formater_string(split_dado[0])
                                prestador = split_dado[2] if len(split_dado) >= 3 else ""
                            case 6:
                                valor_servico = formate_float(dado)
                            case 7:
                                aliquota = formate_float(dado)
                            case 8:
                                valor_ISSQN = formate_float(dado)
                            case 10:
                                retido = "R" if dado.upper() == "SIM" else "N"

                tabela_json["tabela"].append(
                    {
                        "chave": (
                            formater_string(cnpj_filial)
                            + cnpj_prestador_formatado
                            + formater_string(competencia_formatada)
                            + numero_nota_formatado
                        ),
                        "cnpj_filial": formater_string(cnpj_filial),
                        "nome_municipio": nome_municipio,
                        "numero_nota": numero_nota,
                        "numero_debito": numero_nota,
                        "competencia": competencia,
                        "prestador": prestador,
                        "cnpj_prestador": cnpj_prestador_formatado,
                        "aliquota": aliquota,
                        "total": valor_servico + valor_ISSQN,
                        "valor_principal": valor_ISSQN,
                        "situacao": retido,
                        "simples": "S",
                    }
                )

            print(f"Formatacao de NFs concluida... {index_nfs + 1} de 2")

        print(f"Total de NFs: {len(tabela_json['tabela'])}")
        print("Consulta finalizada...")
        return tabela_json