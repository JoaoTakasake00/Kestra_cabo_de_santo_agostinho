from consulta.service.consulta_service import executar_consulta_cabo_de_santo_agostinho

from os import getenv

usuario = getenv("USUARIO")
senha = getenv("SENHA")
cnpj_filial = getenv("CNPJ_FILIAL")
mes_competencia =  getenv("MES_COMPETENCIA")
ano_competencia = getenv("ANO_COMPETENCIA")
nome_municipio = getenv("NOME_MUNICIPIO")

resultado = executar_consulta_cabo_de_santo_agostinho(
    usuario=usuario,
    senha=senha,
    cnpj_filial=cnpj_filial,
    mes_competencia=mes_competencia,
    ano_competencia=ano_competencia,
    nome_municipio=nome_municipio
)

print(resultado)