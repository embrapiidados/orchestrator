import os
import sys
import gc
import psutil
import inspect
import pyshorteners
from dotenv import load_dotenv
from datetime import datetime

# Adicionar o caminho do diretório raiz ao sys.path
load_dotenv()
# Carrega o .env da raiz do projeto para obter ROOT_PIPELINE
load_dotenv(
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
)
ROOT = os.getenv("ROOT_PIPELINE")
USUARIO = os.getenv("USERNAME")
sys.path.append(ROOT)

# Importar o módulo principal de contratos
from scripts_public.buscar_arquivos_sharepoint import buscar_arquivos_sharepoint
from scripts_public.webdriver import configurar_webdriver
from empresa.info_empresas.main_info_empresas import (
    main_info_empresas_baixar,
    main_info_empresas_processar,
)
from analises_relatorios.empresas_contratantes.main_empresas_contratantes import (
    main_empresas_contratantes,
)
from analises_relatorios.projetos_contratados.main_projetos_contratados import (
    main_projetos_contratados,
)
from projeto.contratos.main_contratos import main_contratos
from projeto.projetos.main_projetos import main_projetos
from projeto.projetos_empresas.main_projetos_empresas import main_projetos_empresas
from projeto.estudantes.main_estudantes import main_estudantes
from projeto.pedidos_pi.main_pedidos_pi import main_pedidos_pi
from projeto.macroentregas.main_macroentregas import main_macroentregas
from projeto.sebrae.main_sebrae import main_sebrae
from projeto.classificacao_projeto.main_classificacao_projeto import (
    main_classificacao_projeto,
)
from projeto.portfolio.main_portfolio import main_portfolio
from prospeccao.comunicacao.main_comunicacao import main_comunicacao
from prospeccao.eventos_srinfo.main_eventos_srinfo import main_eventos_srinfo
from prospeccao.prospeccao.main_prospeccao import main_prospeccao
from negociacoes.negociacoes.main_negociacoes import main_negociacoes
from negociacoes.planos_trabalho.main_planos_trabalho import main_planos_trabalho
from negociacoes.propostas_tecnicas.main_propostas_tecnicas import (
    main_propostas_tecnicas,
)
from unidade_embrapii.info_unidades.main_info_unidades import main_info_unidades
from unidade_embrapii.equipe_ue.main_equipe_ue import main_equipe_ue
from unidade_embrapii.termos_cooperacao.main_termos_cooperacao import (
    main_termos_cooperacao,
)
from unidade_embrapii.plano_acao.main_plano_acao import main_plano_acao
from unidade_embrapii.plano_metas.main_plano_metas import main_plano_metas
from scripts_public.registrar_log import registrar_log
from scripts_public.levar_arquivos_sharepoint import levar_arquivos_sharepoint
from scripts_public.comparar_excel import comparar_excel
from scripts_public.whatsapp import enviar_whatsapp
from scripts_public.report_snapshot import gerar_report_snapshot


def verificar_criar_pastas():
    """
    Verifica e cria as pastas necessárias para o funcionamento do pipeline.
    Evita erros de FileNotFoundError ao tentar acessar pastas que não existem.
    """
    print("🟡 " + inspect.currentframe().f_code.co_name)

    # Lista de diretórios base que precisam ter a estrutura padrão
    diretorios_base = [
        # Diretórios de projeto
        os.path.abspath(os.path.join(ROOT, "projeto", "sebrae")),
        os.path.abspath(os.path.join(ROOT, "projeto", "contratos")),
        os.path.abspath(os.path.join(ROOT, "projeto", "projetos")),
        os.path.abspath(os.path.join(ROOT, "projeto", "projetos_empresas")),
        os.path.abspath(os.path.join(ROOT, "projeto", "estudantes")),
        os.path.abspath(os.path.join(ROOT, "projeto", "pedidos_pi")),
        os.path.abspath(os.path.join(ROOT, "projeto", "macroentregas")),
        os.path.abspath(os.path.join(ROOT, "projeto", "portfolio")),
        os.path.abspath(os.path.join(ROOT, "projeto", "classificacao_projeto")),
        # Diretórios de análises e relatórios
        os.path.abspath(
            os.path.join(ROOT, "analises_relatorios", "empresas_contratantes")
        ),
        os.path.abspath(
            os.path.join(ROOT, "analises_relatorios", "projetos_contratados")
        ),
        # Diretórios de unidades
        os.path.abspath(os.path.join(ROOT, "unidade_embrapii", "equipe_ue")),
        os.path.abspath(os.path.join(ROOT, "unidade_embrapii", "info_unidades")),
        os.path.abspath(os.path.join(ROOT, "unidade_embrapii", "plano_acao")),
        os.path.abspath(os.path.join(ROOT, "unidade_embrapii", "termos_cooperacao")),
        os.path.abspath(os.path.join(ROOT, "unidade_embrapii", "plano_metas")),
        # Diretórios de prospecção
        os.path.abspath(os.path.join(ROOT, "prospeccao", "comunicacao")),
        os.path.abspath(os.path.join(ROOT, "prospeccao", "eventos_srinfo")),
        os.path.abspath(os.path.join(ROOT, "prospeccao", "prospeccao")),
        # Diretórios de negociações
        os.path.abspath(os.path.join(ROOT, "negociacoes", "negociacoes")),
        os.path.abspath(os.path.join(ROOT, "negociacoes", "planos_trabalho")),
        os.path.abspath(os.path.join(ROOT, "negociacoes", "propostas_tecnicas")),
        # Diretórios de empresa
        os.path.abspath(os.path.join(ROOT, "empresa", "info_empresas")),
    ]

    # Subpastas padrão que devem existir em cada diretório base
    subpastas = ["step_1_data_raw", "step_2_stage_area", "step_3_data_processed"]

    # Verifica e cria cada diretório base com suas subpastas
    for diretorio in diretorios_base:
        if not os.path.exists(diretorio):
            os.makedirs(diretorio, exist_ok=True)
            print(f"  ✓ Criado diretório base: {diretorio}")

        # Cria as subpastas dentro do diretório base
        for subpasta in subpastas:
            caminho_completo = os.path.join(diretorio, subpasta)
            if not os.path.exists(caminho_completo):
                os.makedirs(caminho_completo, exist_ok=True)
                print(f"  ✓ Criada subpasta: {caminho_completo}")

    print("🟢 " + inspect.currentframe().f_code.co_name)


def main_pipeline_srinfo(plano_metas=False, gerar_snapshot=False, enviar_wpp=False):
    """
    O **pipeline_embrapii_srinfo** tem como objetivo realizar a extração, transformação e carga de dados do SRInfo da Embrapii para o DWPII no sharepoint.
    """
    print("Início: ", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    inicio = datetime.now()

    log = []

    try:
        # Verificar e criar pastas necessárias
        verificar_criar_pastas()

        # SharePoint
        buscar_arquivos_sharepoint()
        
        # Configurar o WebDriver
        driver = configurar_webdriver()

        # Empresas
        print("SEÇÃO 1/5: COLETA DE DADOS")
        print("Subseção: Empresas")
        main_info_empresas_baixar(driver)
        log = logear(log, "info_empresas")

        main_empresas_contratantes(driver)
        log = logear(log, "empresas_contratantes")

        # Unidades Embrapii
        print("Subseção: Unidades Embrapii")
        main_info_unidades(driver)
        log = logear(log, "info_unidades")

        main_equipe_ue(driver)
        log = logear(log, "equipe_ue")

        main_termos_cooperacao(driver)
        log = logear(log, "ue_termos_cooperacao")

        main_plano_acao(driver)
        log = logear(log, "ue_termos_cooperacao")

        if plano_metas:
            main_plano_metas(driver)
            log = logear(log, "ue_plano_metas")

        # Projetos
        print("Subseção: Projetos")

        main_sebrae(driver)
        log = logear(log, "sebrae")

        main_projetos_contratados(driver)
        log = logear(log, "projetos_contratados")

        main_projetos_empresas()
        log = logear(log, "projetos_empresas")

        main_projetos(driver)
        log = logear(log, "projetos")

        main_contratos(driver)
        log = logear(log, "contratos")

        main_estudantes(driver)
        log = logear(log, "estudantes")

        main_pedidos_pi(driver)
        log = logear(log, "pedidos_pi")

        main_macroentregas(driver)
        log = logear(log, "macroentregas")

        main_comunicacao(driver)
        log = logear(log, "comunicacao")

        main_eventos_srinfo(driver)
        log = logear(log, "eventos_srinfo")

        main_prospeccao(driver)
        log = logear(log, "prospeccao")

        main_negociacoes(driver)
        log = logear(log, "negociacoes")

        main_propostas_tecnicas(driver)
        log = logear(log, "propostas_tecnicas")

        main_planos_trabalho(driver)
        log = logear(log, "planos_trabalho")

        encerrar_webdriver(driver)

        # Processamento de dados
        print("SEÇÃO 2/5: PROCESSAMENTO DE DADOS")
        main_classificacao_projeto()
        log = logear(log, "classificacao_projetos")

        main_info_empresas_processar()
        log = logear(log, "info_empresas")

        main_portfolio()
        log = logear(log, "portfolio")
        
        registrar_log(log)

        # SharePoint
        print("SEÇÃO 3/5: LEVAR ARQUIVOS PARA O SHAREPOINT")
        levar_arquivos_sharepoint()

        # Report Snapshot Embrapii
        if gerar_snapshot:
            print("SEÇÃO 4/5: GERAR SNAPSHOT")
            gerar_report_snapshot()

        # Calculando num de novos projetos, empresas e proj sem classificacao
        print("SEÇÃO 5/5: ENCAMINHAR MENSAGEM")
        novos = comparar_excel()

        fim = datetime.now()
        duracao = duracao_tempo(inicio, fim)
        link = "https://embrapii.sharepoint.com/:x:/r/sites/GEPES/Documentos%20Compartilhados/DWPII/srinfo/classificacao_projeto.xlsx?d=wb7a7a439310f4d52a37728b9f1833961&csf=1&web=1&e=qXpfgA"
        link_snapshot = "https://embrapii.sharepoint.com/:f:/r/sites/GEPES/Documentos%20Compartilhados/Reports?csf=1&web=1&e=aVdkyL"
        mensagem = (
            f"*Pipeline SRInfo*\n"
            f'Iniciado em: {inicio.strftime("%d/%m/%Y %H:%M:%S")}\n'
            f'Finalizado em: {fim.strftime("%d/%m/%Y %H:%M:%S")}\n'
            f"_Duração total: {duracao}_\n\n"
            f"Novos projetos: {novos[0]}\n"
            f"Novas empresas: {novos[1]}\n"
            f"Projetos sem classificação: {novos[2]}\n\n"
            f"Relatório Executivo (snapshot): {link_snapshot}\n\n"
            f"Link para classificação dos projetos: {link}"
        )
        print(mensagem)

        if enviar_wpp:
            enviar_whatsapp(mensagem)


    except Exception as e:
        # Registrar erro no log
        # Re-lançar a exceção para manter o comportamento original
        raise

    print("Fim: ", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))


def encerrar_webdriver(driver):
    driver.quit()
    for proc in psutil.process_iter():
        try:
            # Verificar se o processo corresponde ao WebDriver (por exemplo, msedgedriver)
            if proc.name().lower() == "msedgedriver":
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    gc.collect()


def logear(log, entidade):
    log.append([datetime.now().strftime("%d/%m/%Y %H:%M:%S"), USUARIO, entidade])
    return log


def duracao_tempo(inicio, fim):
    duracao = fim - inicio
    horas, resto = divmod(duracao.total_seconds(), 3600)
    minutos, segundos = divmod(resto, 60)

    # Formatá-la como uma string no formato HH:MM:SS
    duracao_formatada = f"{int(horas):02}:{int(minutos):02}:{int(segundos):02}"

    return duracao_formatada


def encurtar_url(url):
    s = pyshorteners.Shortener()
    return s.tinyurl.short(url)


def teste_pipeline():
    # Configurar o WebDriver
    driver = configurar_webdriver()
    main_plano_metas(driver)


if __name__ == "__main__":
    try:
        main_pipeline_srinfo()
    except Exception as e:
        print(f"Erro na execução do pipeline: {str(e)}")
        sys.exit(1)
