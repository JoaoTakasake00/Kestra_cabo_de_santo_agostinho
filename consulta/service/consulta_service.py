
from consulta.elements.consulta_elements import loginElements, ConsultaElement

from selenium_tools.selenium_driver import SeleniumDriver

def executar_consulta_cabo_de_santo_agostinho(
        usuario: str, 
        senha: str, 
        cnpj_filial: str, 
        mes_competencia: str, 
        ano_competencia: str, 
        nome_municipio: str
        ):

    # Configura o navegador (sem interface gráfica)
    with SeleniumDriver(headless=False) as driver:
        try:
            url = "https://www.tinus.com.br/csp/cabo/portal/index.csp?839mbjj3866hHwET98573FBFW8704uU=TEha09vHm343whw68660kfbGk104ieXuS3294Z6204017CiYg346"
            
            login_page = loginElements(driver, url=url)
            consulta_page = ConsultaElement(driver)
        
            # Login
            login_page.open()
            login_page.navigate_to_login()
            login_page.logar(usuario, senha)

            # Consulta
            consulta_page.navigate_to_declaracao()
            consulta_page.select_contribuinte(mes_competencia, ano_competencia)
            dados_nfs = consulta_page.get_nfs_municipal()
            dados_nfs_prefeitura = consulta_page.get_nfs_prefeitura()
            resultado = consulta_page.mounted_json_nfs_municipal(dados_nfs, dados_nfs_prefeitura, cnpj_filial, nome_municipio)

            return resultado

        finally:
            driver.quit()