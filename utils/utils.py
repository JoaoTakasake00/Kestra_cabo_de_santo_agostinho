import base64
import time

import requests

import re

import os

from datetime import datetime

from selenium.common.exceptions import TimeoutException, NoAlertPresentException, UnexpectedAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from bs4 import BeautifulSoup

from os import getenv

from typing import Iterable, Iterator, TypeVar

T = TypeVar("T")

def type_selector(typeSelector):
    typeSelector = typeSelector.lower()
    match typeSelector:
        case "id":
            return By.ID
        case "name":
            return By.NAME
        case "class":
            return By.CLASS_NAME
        case "tag":
            return By.TAG_NAME
        case "css":
            return By.CSS_SELECTOR
        case "xpath":
            return By.XPATH
        case _:
            raise ValueError(f"Invalid selector type: {typeSelector}")


def findElement(driver, typeS, timeout=120):
    wait = WebDriverWait(driver, timeout)

    try:
        element = wait.until(EC.presence_of_element_located(typeS))
    except TimeoutException:
        TimeoutException(
            f"Element with {typeS} not found within {timeout} seconds."
        )
        return None

    return element


def select_element(driver, typeSelectList, typeSelector, value, timeout=120):
    selectElement = findElement(driver, typeSelector, timeout)
    select = Select(selectElement)

    typeSelectList = typeSelectList.lower()
    match typeSelectList:
        case "index":
            select.select_by_index(int(value))
        case "value":
            select.select_by_value(value)
        case "visible_text":
            select.select_by_visible_text(value)
        case "partial_text_with_alert":
            for option in select.options:
                try:
                    if value.lower() in option.text.lower():
                        select.select_by_visible_text(option.text)
                        return ""  
                except UnexpectedAlertPresentException:
                    texto = lidar_com_alerta(driver)
                    return texto  
            return "" 
        case "partial_text":
            for option in select.options:
                if value.lower() in option.text.lower():
                    select.select_by_visible_text(option.text)
        case _:
            raise ValueError(f"Invalid selection type: {typeSelectList}")


def lidar_com_alerta(driver, timeout=3):
    try:
        WebDriverWait(driver, timeout).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        texto = alert.text
        alert.accept()
        return texto
    except (TimeoutException, NoAlertPresentException):
        return ""
    

def find_element_end_click(driver, typeSelector, timeout=120):
    element = findElement(driver, typeSelector, timeout)

    driver.execute_script("arguments[0].scrollIntoView();", element)

    WebDriverWait(driver, 10).until(lambda d: d.execute_script(
        "const el = arguments[0];"
        "const r = el.getBoundingClientRect();"
        "const e = document.elementFromPoint(r.left + r.width/2, r.top + r.height/2);"
        "return e === el;", element
    ))

    element.click()


def get_image_captcha(src, output_path="captcha.png"):
    response = requests.get(src)
    with open(output_path, "wb") as f:
        f.write(response.content)


def resolve_image_captcha_numeric(image_path):
    # Lê e codifica a imagem em base64
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
    
    # Cria a task no CapMonster
    create_task_payload = {
        "clientKey": getenv("API_KEY"),
        "task": {
            "type": "ImageToTextTask", 
            "body": encoded_image,
            "phrase": False,         # false se o texto não contém espaços
            "case": False,           # false se não precisa diferenciar maiúsculas/minúsculas
            "numeric": 1,            # 1 se o CAPTCHA só tem números
            "math": False,           # true se for um CAPTCHA de conta matemática
            "minLength": 4,          # comprimento mínimo do texto esperado
            "maxLength": 4           # comprimento máximo do texto esperado
        },
    }

    response = requests.post(
        "https://api.capmonster.cloud/createTask", json=create_task_payload
    ).json()
    task_id = response.get("taskId")

    if not task_id:
        raise Exception(f"Erro ao criar task: {response}")

    # Consulta o resultado da task até ela estar pronta
    result_payload = {"clientKey": getenv("API_KEY"), "taskId": task_id}

    while True:
        result_response = requests.post(
            "https://api.capmonster.cloud/getTaskResult", json=result_payload
        ).json()
        if result_response.get("status") == "ready":
            return result_response["solution"]["text"]
        time.sleep(2)

def resolve_image_captcha_text(image_path):
    # Lê e codifica a imagem em base64
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
    
    # Cria a task no CapMonster
    create_task_payload = {
        "clientKey": getenv("API_KEY"),
        "task": {
            "type": "ImageToTextTask", 
            "body": encoded_image,
            "phrase": False,         # false se o texto não contém espaços
            "case": False,           # false se não precisa diferenciar maiúsculas/minúsculas         # 1 se o CAPTCHA só tem números
            "math": False,           # true se for um CAPTCHA de conta matemática
            "minLength": 4,          # comprimento mínimo do texto esperado
            "maxLength": 4,          # comprimento máximo do texto esperado
            "numeric": 0,            # 0 se o CAPTCHA pode conter letras
        },
    }

    response = requests.post(
        "https://api.capmonster.cloud/createTask", json=create_task_payload
    ).json()
    task_id = response.get("taskId")

    if not task_id:
        raise Exception(f"Erro ao criar task: {response}")

    # Consulta o resultado da task até ela estar pronta
    result_payload = {"clientKey": getenv("API_KEY"), "taskId": task_id}

    while True:
        result_response = requests.post(
            "https://api.capmonster.cloud/getTaskResult", json=result_payload
        ).json()
        if result_response.get("status") == "ready":
            return result_response["solution"]["text"]
        time.sleep(2)

def formater_string(string):
    return re.sub(r'\D', '', string)

def remove_left_zeros(number):
    return re.sub(r'^0+(?=\d)', '', number)

def formatar_data(data: str, formato_atual: str, formato_desejado: str) -> str:
    def get_strptime_format(f):
        match f:
            case "d/m/y":
                return "%d/%m/%Y"
            case "y/m/d":
                return "%Y/%m/%d"
            case "m/y":
                return "%m/%Y"
            case "y/m":
                return "%Y/%m"
            case "d/m":
                return "%d/%m"
            case "m/d":
                return "%m/%d"
            case _:
                raise ValueError(f"Formato desconhecido: {f}")

    # Parse da data com base no formato atual
    strptime_format = get_strptime_format(formato_atual)

    try:
        data_obj = datetime.strptime(data, strptime_format)
    except ValueError:
        raise ValueError(f"Data inválida para o formato {formato_atual}: {data}")

    # Formatar para o novo formato
    strftime_format = get_strptime_format(formato_desejado)
    return data_obj.strftime(strftime_format)

def formate_float(valor: str) -> float:
    """Converte string numérica para float, tratando diferentes formatos."""
    valor = valor.strip()

    # Se tiver vírgula, é provavelmente formato BR
    if ',' in valor:
        valor = valor.replace('.', '')  # remove separador de milhar
        valor = valor.replace(',', '.')  # converte decimal
    # Se tiver só ponto, já deve estar no formato correto

    try:
        return float(valor)
    except ValueError:
        raise ValueError(f"Valor inválido para conversão: {valor}")
    
def batched(iterable: Iterable[T], batch_size: int) -> Iterator[list[T]]:
    """Divide um iterável em lotes (batches) de tamanho batch_size."""
    batch = []
    for item in iterable:
        batch.append(item)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if batch:
        yield batch

def wait_for_element(driver, locator, disappear_timeout=10):

    # Espera o elemento desaparecer
    WebDriverWait(driver, disappear_timeout).until_not(
        EC.visibility_of_element_located(locator)
    )

def arredondar_float(valor: float) -> float:
    return round(valor, 2)

def parse_valor(valor) -> float:
    if isinstance(valor, float) or isinstance(valor, int):
        return float(valor)  # já é número, só garante que é float

    valor = valor.strip()
    if "," in valor and "." in valor:
        valor = valor.replace(".", "").replace(",", ".")
    elif "," in valor:
        valor = valor.replace(",", ".")

    return float(valor)

def formatar_valor_brasileiro(valor) -> str:
    if isinstance(valor, str):
        valor = valor.strip()
        if "," in valor and "." in valor:
            valor = valor.replace(".", "").replace(",", ".")
        elif "," in valor:
            valor = valor.replace(",", ".")
        valor = float(valor)

    elif isinstance(valor, (int, float)):
        valor = float(valor)
    else:
        raise ValueError("Valor deve ser str, int ou float.")

    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def donwload_htmlPDF(driver, original_window, handles_antes, nome_pdf, logging):
        # Aguarda a nova aba aparecer
        for _ in range(10):
            novas_janelas = driver.window_handles
            if len(novas_janelas) > len(handles_antes):
                break
            time.sleep(1)

        # Encontra a nova aba
        nova_aba = [h for h in driver.window_handles if h not in handles_antes][0]

        # Troca para a nova aba
        driver.switch_to.window(nova_aba)

        time.sleep(2)

        html = driver.page_source
        dados = extrair_nosso_numero_e_vencimento(html)

        # Gera o PDF da aba
        pdf = driver.execute_cdp_cmd("Page.printToPDF", {
            "landscape": False,
            "printBackground": True
        })

        logging.info(f"PDF salvo: {nome_pdf}.pdf")

        driver.close()
        driver.switch_to.window(original_window)

        return pdf["data"], dados

def extrair_nosso_numero_e_vencimento(html):
    soup = BeautifulSoup(html, "html.parser")

    nosso_numero = None
    vencimento = None
    valor_total = None

    # Encontra todos os pares label + campo
    for label in soup.find_all("span", class_="label"):
        texto_label = label.get_text(strip=True).upper()

        if texto_label == "NOSSO NÚMERO":
            campo = label.find_next_sibling("span", class_="campo")
            if campo:
                nosso_numero = campo.get_text(strip=True)

        elif texto_label == "DATA VENCIMENTO":
            campo = label.find_next_sibling("span", class_="campo")
            if campo and campo.strong:
                vencimento = campo.strong.get_text(strip=True)

        elif texto_label == "(=)VALOR DO DOCUMENTO":
            campo = label.find_next_sibling("span", class_="campo")
            if campo and campo.strong:
                valor_total = campo.strong.get_text(strip=True)

    return nosso_numero, vencimento, valor_total

def baixar_pdf(pasta_download, timeout=30):
    nome_arquivo = None  # garante que está definida antes do loop

    for _ in range(timeout):
        arquivos = os.listdir(pasta_download)
        arquivos_crdownload = [f for f in arquivos if f.endswith(".pdf.crdownload")]
        if arquivos_crdownload:
            # Pega o mais recente
            arquivo_recente = max(
                (os.path.join(pasta_download, f) for f in arquivos_crdownload),
                key=os.path.getctime
            )
            nome_arquivo = os.path.basename(arquivo_recente)
            break
        time.sleep(1)

    if not nome_arquivo:
        raise TimeoutError("Nenhum arquivo .crdownload foi detectado a tempo.")

    nome_base = nome_arquivo.split(".")[0]
    nome_arquivo_pdf = f"https://tributario.bauru.sp.gov.br/resultados/{nome_base}.pdf"

    # Apaga o arquivo .crdownload
    caminho_crdownload = os.path.join(pasta_download, nome_arquivo)
    if os.path.exists(caminho_crdownload):
        os.remove(caminho_crdownload)

    # Faz o download do PDF e retorna o base64
    pdf_base64 = baixar_pdf_por_url(nome_arquivo_pdf, pasta_destino=pasta_download)

    return pdf_base64

def baixar_pdf_por_url(nome_arquivo_pdf, pasta_destino=os.getcwd()):
    resposta = requests.get(nome_arquivo_pdf)

    if resposta.status_code == 200:
        # Converte o conteúdo binário direto para base64, sem salvar arquivo
        pdf_base64 = base64.b64encode(resposta.content).decode("utf-8")
        return pdf_base64
    else:
        raise Exception(f"Erro ao baixar o PDF. Código HTTP: {resposta.status_code}")

def limpar_cnpj(cnpj: str) -> str:
    """
    Remove a formatação de um CNPJ.
    Exemplos:
        "49.762.844/0001-69" -> "49762844000169"
        "49762844000169" -> "49762844000169"
    """
    return re.sub(r"\D", "", cnpj)
