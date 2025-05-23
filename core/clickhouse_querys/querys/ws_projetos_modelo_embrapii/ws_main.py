import inspect
from querys.ws_projetos_modelo_embrapii.srinfo_project import srinfo_project
from querys.ws_projetos_modelo_embrapii.srinfo_prospect import srinfo_prospect
from querys.ws_projetos_modelo_embrapii.srinfo_negotiation import srinfo_negotiation
from querys.ws_projetos_modelo_embrapii.srinfo_partnership_fundsapproval import srinfo_partnership_fundsapproval

def ws_projetos_modelo_embrapii():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    try:
        #Querys
        srinfo_prospect()
        srinfo_negotiation()
        srinfo_project()
        srinfo_partnership_fundsapproval()

        print("🟢 " + inspect.currentframe().f_code.co_name)
    except Exception as e:
        print(f"🔴 Erro: {e}")