import os
import sys
import pandas as pd
from dotenv import load_dotenv
from scripts.query_clickhouse import query_clickhouse

load_dotenv()

ROOT = os.getenv('ROOT_SEBRAE_UFS')

HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
USER = os.getenv('USER')
PASSWORD = os.getenv('CLICKHOUSE_PASSWORD')
STEP1 = os.path.abspath(os.path.join(ROOT, 'step_1_data_raw'))
STEP3 = os.path.abspath(os.path.join(ROOT, 'step_3_data_processed'))


def srinfo_sebrae_sourceamount():
    query = """
        		SELECT
                    ue_negotiation.code codigo_negociacao,
                    main.value valor,
                    source.alias fonte,
                    company.cnpj
                FROM s3(cred_s3, url = s3m_srinfo('partnership_sourceamount', today())) main
                LEFT JOIN (
                    SELECT
                        id,
                        alias
                    FROM s3(cred_s3, url = s3m_srinfo('project_source', today()))
                ) source
                ON main.source_id = source.id
                LEFT JOIN (
                    SELECT
                        id,
                        partnership_info_id
                    FROM s3(cred_s3, url = s3m_srinfo('partnership_fundsapproval', today()))
                ) fundsapproval
                ON main.funds_approval_id = fundsapproval.id
                LEFT JOIN (
                    SELECT
                        id,
                        negotiation_id,
                        partnership_id
                    FROM s3(cred_s3, url = s3m_srinfo('ue_partnershipinfo', today()))
                ) ue_partnership
                ON fundsapproval.partnership_info_id = ue_partnership.id
                LEFT JOIN (
                    SELECT
                        id,
                        model
                    FROM s3(cred_s3, url = s3m_srinfo('partnership_partnership', today()))
                ) partnership
                ON ue_partnership.partnership_id = partnership.id
                LEFT JOIN (
                    SELECT
                        id,
                        code
                    FROM s3(cred_s3, url = s3m_srinfo('ue_negotiation', today())) ue_negotiation
                ) ue_negotiation
                ON ue_partnership.negotiation_id = ue_negotiation.id
                LEFT JOIN (
                    SELECT
                        id,
                        cnpj
                    FROM s3(cred_s3, url = s3m_srinfo('company_company', today()))
                ) company
                ON main.company_id = company.id
                WHERE partnership.model IN (2, 10, 9, 19, 20)
    """
    nome_arquivo = "sebrae_sourceamount"
    query_clickhouse(HOST, PORT, USER, PASSWORD, query, nome_arquivo)

    # Carregar arquivo
    path_file_raw = os.path.abspath(os.path.join(STEP1 ,f"{nome_arquivo}.csv"))
    df_raw = pd.read_csv(path_file_raw)

    # Salvar em formato Excel
    print(f"Salvando arquivo {nome_arquivo} em formato Excel")
    path_file_processed = os.path.abspath(os.path.join(STEP1, f"srinfo_{nome_arquivo}.xlsx"))
    df_raw.to_excel(path_file_processed, index=False)
    path_file_processed = os.path.abspath(os.path.join(STEP3, f"srinfo_{nome_arquivo}.xlsx"))
    df_raw.to_excel(path_file_processed, index=False)