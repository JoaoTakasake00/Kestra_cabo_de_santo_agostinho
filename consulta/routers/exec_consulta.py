from consulta.service.consulta_service import executar_consulta_cabo_de_santo_agostinho

resultado = executar_consulta_cabo_de_santo_agostinho(
    usuario="seu_usuario",
    senha="sua_senha",
    cnpj_filial="00.000.000/0000-00",
    mes_competencia="01",
    ano_competencia="2024",
    nome_municipio="Cabo de Santo Agostinho"
)

print(resultado)