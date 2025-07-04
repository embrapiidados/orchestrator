from core.clickhouse_querys.connection.connect_vpn import connect_vpn, disconnect_vpn
from core.clickhouse_querys.start_clean import start_clean
# from querys.ws_projetos_modelo_embrapii.ws_main import ws_projetos_modelo_embrapii
# from querys.ws_unidades_embrapii.ws_main import ws_unidades_embrapii
# from querys.ws_outros.ws_main import ws_outros
# from querys.ws_empresas.ws_main import ws_empresas
from core.clickhouse_querys.querys.ws_financeiro.ws_financeiro import ws_financeiro
from core.clickhouse_querys.connection.up_sharepoint import up_sharepoint


def clickhouse_querys():

    #Start clean
    start_clean()

    #Ligar VPN
    # connect_vpn()

    #Executar querys
    # ws_projetos_modelo_embrapii()
    # ws_unidades_embrapii()
    # ws_outros()
    # ws_empresas()
    ws_financeiro()

    #Desligar VPN
    # disconnect_vpn()

    #Levar dados para o Sharepoint
    up_sharepoint()


if __name__ == "__main__":
    clickhouse_querys()