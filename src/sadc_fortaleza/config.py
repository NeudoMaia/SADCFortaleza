"""
Configurações georreferenciadas, malha de pontos críticos, as 11 estações automáticas oficiais
da Defesa Civil de Fortaleza (Plugfield API), postos complementares Funceme/CEMADEN,
câmeras do PMPU e protocolos operacionais.
"""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class EstacaoMeteorologica:
    id_estacao: str
    plugfield_id: int
    nome: str
    nome_curto: str
    orgao: str  # "DEFESA_CIVIL", "FUNCEME", "CEMADEN"
    bairro: str
    bairros_secundarios: List[str]
    latitude: float
    longitude: float
    bacia_hidrografica: str
    endereco_referencia: str = ""
    possui_sensor_nivel_sonico: bool = False
    intervalo_leitura_min: int = 5


CARTO_API_KEY_PUBLICA: str = "cb1_2t7z_1_b4192d625bdc678b8f9125ad"
NASA_API_KEY_PADRAO: str = "WmJbrCnNL6zCBNnLFCgbLJFtjrTpghH7NNWq8mWb"


@dataclass(frozen=True)
class PontoCritico:
    id_ponto: str
    nome: str
    bairro: str
    bacia_hidrografica: str
    tipo_unidade: str  # "AREA_RISCO_DC", "PONTO_ATENCAO_PMPU", "CANAL_MICROBACIA"
    eh_piloto: bool
    latitude: float
    longitude: float
    cota_m: float
    declividade_pct: float
    impermeabilizacao_frac: float
    dist_corpo_hidrico_m: float
    capacidade_drenagem_mm_h: float
    obstrucao_base_frac: float
    fator_decaimento_api: float
    influencia_mare: float
    ocorrencias_2021_2024: int
    anos_recorrencia_consecutivos: int
    estacao_referencia_plugfield: int
    cameras_pmpu: List[str] = field(default_factory=list)
    populacao_exposta_estimada: int = 0


@dataclass(frozen=True)
class ProtocoloOperacional:
    nivel: str
    cor_hex: str
    condicao_resumo: str
    acao_defesa_civil: str
    orgaos_acionados: List[str]
    notificar_40199: bool


# As 11 Estações Automáticas Oficiais da Defesa Civil de Fortaleza (Plugfield) + 2 Postos Parceiros
ESTACOES_FORTALEZA: List[EstacaoMeteorologica] = [
    EstacaoMeteorologica(
        id_estacao="PCD_8642",
        plugfield_id=8642,
        nome="DEFESA CIVIL - CENTRO",
        nome_curto="Centro",
        orgao="DEFESA_CIVIL",
        bairro="Centro",
        bairros_secundarios=["Jacarecanga", "Moura Brasil", "Praia de Iracema", "Aldeota", "Meireles", "Farias Brito"],
        latitude=-3.72313,
        longitude=-38.53782,
        bacia_hidrografica="Vertente Marítima",
        endereco_referencia="Rua Agapito dos Santos, 195 — Centro (Sede CEMON / Defesa Civil)",
    ),
    EstacaoMeteorologica(
        id_estacao="PCD_3318",
        plugfield_id=3318,
        nome="SERVIZI - DEFESA CIVIL - DOM LUSTOSA",
        nome_curto="Dom Lustosa",
        orgao="DEFESA_CIVIL",
        bairro="Dom Lustosa",
        bairros_secundarios=["Padre Andrade", "Pici", "Antônio Bezerra", "Henrique Jorge", "Autran Nunes", "João XXIII"],
        latitude=-3.74880,
        longitude=-38.58800,
        bacia_hidrografica="Maranguapinho",
        endereco_referencia="Rua Pedro Augusto, 213 — Dom Lustosa (Ponte Canal Dom Lustosa)",
        possui_sensor_nivel_sonico=True,
    ),
    EstacaoMeteorologica(
        id_estacao="PCD_9137",
        plugfield_id=9137,
        nome="DEFESA CIVIL - MUCURIPE",
        nome_curto="Mucuripe",
        orgao="DEFESA_CIVIL",
        bairro="Mucuripe",
        bairros_secundarios=["Aldeota", "Varjota", "Meireles", "Cais do Porto", "Vicente Pinzon", "Papicu"],
        latitude=-3.72617,
        longitude=-38.48407,
        bacia_hidrografica="Vertente Marítima",
        endereco_referencia="Rua Umari, s/n — Mucuripe (Escola Municipal Dragão do Mar)",
    ),
    EstacaoMeteorologica(
        id_estacao="PCD_8836",
        plugfield_id=8836,
        nome="DEFESA CIVIL - MONTESE",
        nome_curto="Montese",
        orgao="DEFESA_CIVIL",
        bairro="Montese",
        bairros_secundarios=["Itaoca", "Parangaba", "Vila União", "Bom Futuro", "Jardim América", "Aeroporto", "Serrinha"],
        latitude=-3.77272,
        longitude=-38.55843,
        bacia_hidrografica="Cocó / Tauape",
        endereco_referencia="Rua Mundica Paula, 670 — Montese/Itaoca (EM Carolino Sucupira)",
    ),
    EstacaoMeteorologica(
        id_estacao="PCD_9281",
        plugfield_id=9281,
        nome="DEFESA CIVIL - BENFICA",
        nome_curto="Benfica",
        orgao="DEFESA_CIVIL",
        bairro="Benfica",
        bairros_secundarios=["Farias Brito", "Rodolfo Teófilo", "José Bonifácio", "Gentilândia", "Damas"],
        latitude=-3.74815,
        longitude=-38.53839,
        bacia_hidrografica="Vertente Marítima / Tauape",
        endereco_referencia="Rua Jorge Dumar, 1501 — Benfica (Sede URBFOR)",
    ),
    EstacaoMeteorologica(
        id_estacao="PCD_9242",
        plugfield_id=9242,
        nome="DEFESA CIVIL - GUARARAPES",
        nome_curto="Guararapes",
        orgao="DEFESA_CIVIL",
        bairro="Guararapes",
        bairros_secundarios=["Aerolândia", "Cocó", "Salinas", "Luciano Cavalcante", "Eng. Luciano Cavalcante", "Edson Queiroz"],
        latitude=-3.76010,
        longitude=-38.48366,
        bacia_hidrografica="Cocó",
        endereco_referencia="Av. Washington Soares, 800 — Guararapes (Corredor Cocó / SEUMA)",
    ),
    EstacaoMeteorologica(
        id_estacao="PCD_8869",
        plugfield_id=8869,
        nome="DEFESA CIVIL - VILA VELHA",
        nome_curto="Vila Velha",
        orgao="DEFESA_CIVIL",
        bairro="Vila Velha",
        bairros_secundarios=["Barra do Ceará", "Jardim Guanabara", "Quintino Cunha", "Cristo Redentor", "Pirambu"],
        latitude=-3.71426,
        longitude=-38.59688,
        bacia_hidrografica="Rio Ceará / Vertente Marítima",
        endereco_referencia="Av. Dom Aloísio Lorscheider, 1040 — Vila Velha (EM Dona Hilza Diogo)",
    ),
    EstacaoMeteorologica(
        id_estacao="PCD_9282",
        plugfield_id=9282,
        nome="DEFESA CIVIL - GRANJA LISBOA",
        nome_curto="Granja Lisboa",
        orgao="DEFESA_CIVIL",
        bairro="Granja Lisboa",
        bairros_secundarios=["Granja Portugal", "Bom Jardim", "Siqueira", "Conjunto Ceará"],
        latitude=-3.78997,
        longitude=-38.61905,
        bacia_hidrografica="Maranguapinho",
        endereco_referencia="Rua Xavier da Silveira, s/n — Granja Lisboa (Bacia Maranguapinho)",
    ),
    EstacaoMeteorologica(
        id_estacao="PCD_9134",
        plugfield_id=9134,
        nome="DEFESA CIVIL - CJ ESPERANÇA",
        nome_curto="Conjunto Esperança",
        orgao="DEFESA_CIVIL",
        bairro="Conjunto Esperança",
        bairros_secundarios=["Mondubim", "Parque Prefeito José Walter", "Maraponga", "Planalto Ayrton Senna", "Aracapé"],
        latitude=-3.81477,
        longitude=-38.58990,
        bacia_hidrografica="Maranguapinho",
        endereco_referencia="Av. Penetração Oeste, s/n — Cj. Esperança (EEFM Adalgisa Bonfim)",
    ),
    EstacaoMeteorologica(
        id_estacao="PCD_9249",
        plugfield_id=9249,
        nome="DEFESA CIVIL - JANGURUSSU",
        nome_curto="Jangurussu",
        orgao="DEFESA_CIVIL",
        bairro="Jangurussu",
        bairros_secundarios=["Conjunto Palmeiras", "Barroso", "Passaré", "Ancuri", "Pedras"],
        latitude=-3.83890,
        longitude=-38.52268,
        bacia_hidrografica="Cocó",
        endereco_referencia="Av. Contorno Sul, s/n — Jangurussu (UPA Dr. Fábio Landim)",
    ),
    EstacaoMeteorologica(
        id_estacao="PCD_9169",
        plugfield_id=9169,
        nome="DEFESA CIVIL - MESSEJANA",
        nome_curto="Messejana",
        orgao="DEFESA_CIVIL",
        bairro="Messejana",
        bairros_secundarios=["Cambeba", "Paupina", "Lagoa Redonda", "Curió", "Guajeru", "José de Alencar", "Coaçu"],
        latitude=-3.82547,
        longitude=-38.48527,
        bacia_hidrografica="Cocó",
        endereco_referencia="Av. Mem de Sá, 384 — Messejana (ETP Profª Raimunda Félix)",
    ),
    EstacaoMeteorologica(
        id_estacao="FUNCEME_01",
        plugfield_id=10001,
        nome="Posto Pluviométrico Funceme - Pici",
        nome_curto="Funceme Pici",
        orgao="FUNCEME",
        bairro="Pici",
        bairros_secundarios=["Padre Andrade", "Bela Vista", "Parquelândia"],
        latitude=-3.74600,
        longitude=-38.57400,
        bacia_hidrografica="Maranguapinho",
        endereco_referencia="Av. Mister Hull, s/n — Campus do Pici",
    ),
    EstacaoMeteorologica(
        id_estacao="CEMADEN_01",
        plugfield_id=10002,
        nome="PCD CEMADEN - Itaoca / Parangaba",
        nome_curto="CEMADEN Itaoca",
        orgao="CEMADEN",
        bairro="Itaoca",
        bairros_secundarios=["Montese", "Parangaba"],
        latitude=-3.76200,
        longitude=-38.54600,
        bacia_hidrografica="Cocó / Tauape",
        endereco_referencia="Rua Governador João Carlos, s/n — Itaoca",
    ),
]


# Malha de Pontos Críticos e Microbacias (4 Áreas-Piloto + Pontos de Controle)
PONTOS_CRITICOS: List[PontoCritico] = [
    PontoCritico(
        id_ponto="PC_JAC_01",
        nome="Jacarecanga - Canal do Jacarecanga / Av. Filomeno Gomes",
        bairro="Jacarecanga",
        bacia_hidrografica="Vertente Marítima",
        tipo_unidade="AREA_RISCO_DC",
        eh_piloto=True,
        latitude=-3.7212,
        longitude=-38.5448,
        cota_m=3.2,
        declividade_pct=0.45,
        impermeabilizacao_frac=0.84,
        dist_corpo_hidrico_m=35.0,
        capacidade_drenagem_mm_h=24.0,
        obstrucao_base_frac=0.32,
        fator_decaimento_api=0.90,
        influencia_mare=0.92,
        ocorrencias_2021_2024=142,
        anos_recorrencia_consecutivos=4,
        estacao_referencia_plugfield=8642,
        cameras_pmpu=["CAM_PMPU_012", "CAM_PMPU_013", "CAM_RISCO_004"],
        populacao_exposta_estimada=4850,
    ),
    PontoCritico(
        id_ponto="PC_PAD_01",
        nome="Padre Andrade - Margem Rio Maranguapinho / Rua Demétrio Menezes",
        bairro="Padre Andrade",
        bacia_hidrografica="Maranguapinho",
        tipo_unidade="AREA_RISCO_DC",
        eh_piloto=True,
        latitude=-3.7388,
        longitude=-38.5855,
        cota_m=9.5,
        declividade_pct=0.65,
        impermeabilizacao_frac=0.79,
        dist_corpo_hidrico_m=28.0,
        capacidade_drenagem_mm_h=26.0,
        obstrucao_base_frac=0.29,
        fator_decaimento_api=0.93,
        influencia_mare=0.22,
        ocorrencias_2021_2024=128,
        anos_recorrencia_consecutivos=4,
        estacao_referencia_plugfield=3318,
        cameras_pmpu=["CAM_RISCO_011", "CAM_PMPU_041"],
        populacao_exposta_estimada=5600,
    ),
    PontoCritico(
        id_ponto="PC_ALD_01",
        nome="Aldeota - Bacia Riacho Pajeú / Av. Heráclito Graça x Barão de Studart",
        bairro="Aldeota",
        bacia_hidrografica="Vertente Marítima",
        tipo_unidade="PONTO_ATENCAO_PMPU",
        eh_piloto=True,
        latitude=-3.7345,
        longitude=-38.5042,
        cota_m=14.8,
        declividade_pct=0.80,
        impermeabilizacao_frac=0.93,
        dist_corpo_hidrico_m=85.0,
        capacidade_drenagem_mm_h=30.0,
        obstrucao_base_frac=0.25,
        fator_decaimento_api=0.84,
        influencia_mare=0.35,
        ocorrencias_2021_2024=96,
        anos_recorrencia_consecutivos=4,
        estacao_referencia_plugfield=9137,
        cameras_pmpu=["CAM_PMPU_022", "CAM_PMPU_023"],
        populacao_exposta_estimada=3200,
    ),
    PontoCritico(
        id_ponto="PC_ITA_01",
        nome="Itaoca - Canal do Tauape / Entorno Lagoa da Parangaba",
        bairro="Itaoca",
        bacia_hidrografica="Cocó / Tauape",
        tipo_unidade="AREA_RISCO_DC",
        eh_piloto=True,
        latitude=-3.7662,
        longitude=-38.5515,
        cota_m=16.2,
        declividade_pct=0.55,
        impermeabilizacao_frac=0.82,
        dist_corpo_hidrico_m=45.0,
        capacidade_drenagem_mm_h=27.0,
        obstrucao_base_frac=0.30,
        fator_decaimento_api=0.94,
        influencia_mare=0.05,
        ocorrencias_2021_2024=115,
        anos_recorrencia_consecutivos=4,
        estacao_referencia_plugfield=8836,
        cameras_pmpu=["CAM_RISCO_019", "CAM_PMPU_058"],
        populacao_exposta_estimada=4100,
    ),
    PontoCritico(
        id_ponto="PC_LAG_01",
        nome="Aerolândia - Canal do Lagamar / Comunidade do Lagamar",
        bairro="Aerolândia",
        bacia_hidrografica="Cocó / Tauape",
        tipo_unidade="AREA_RISCO_DC",
        eh_piloto=False,
        latitude=-3.7675,
        longitude=-38.5115,
        cota_m=7.4,
        declividade_pct=0.40,
        impermeabilizacao_frac=0.81,
        dist_corpo_hidrico_m=20.0,
        capacidade_drenagem_mm_h=23.0,
        obstrucao_base_frac=0.34,
        fator_decaimento_api=0.95,
        influencia_mare=0.48,
        ocorrencias_2021_2024=154,
        anos_recorrencia_consecutivos=4,
        estacao_referencia_plugfield=9242,
        cameras_pmpu=["CAM_RISCO_001", "CAM_RISCO_002", "CAM_PMPU_081"],
        populacao_exposta_estimada=7400,
    ),
    PontoCritico(
        id_ponto="PC_MES_01",
        nome="Messejana - Trecho Alto / Coaçu",
        bairro="Messejana",
        bacia_hidrografica="Cocó",
        tipo_unidade="PONTO_ATENCAO_PMPU",
        eh_piloto=False,
        latitude=-3.8330,
        longitude=-38.4890,
        cota_m=34.0,
        declividade_pct=2.10,
        impermeabilizacao_frac=0.58,
        dist_corpo_hidrico_m=420.0,
        capacidade_drenagem_mm_h=42.0,
        obstrucao_base_frac=0.12,
        fator_decaimento_api=0.82,
        influencia_mare=0.0,
        ocorrencias_2021_2024=14,
        anos_recorrencia_consecutivos=1,
        estacao_referencia_plugfield=9169,
        cameras_pmpu=["CAM_PMPU_095"],
        populacao_exposta_estimada=950,
    ),
]


PROTOCOLOS_OPERACIONAIS: Dict[str, ProtocoloOperacional] = {
    "NORMAL": ProtocoloOperacional(
        nivel="NORMAL",
        cor_hex="#10B981",
        condicao_resumo="Sem chuva relevante e indicadores hidrometeorológicos abaixo do limiar de vigilância.",
        acao_defesa_civil="Monitoramento de rotina nas 11 estações automáticas e manutenção preventiva de drenagem.",
        orgaos_acionados=["CIOPS_ROTINA"],
        notificar_40199=False,
    ),
    "VIGILANCIA": ProtocoloOperacional(
        nivel="VIGILANCIA",
        cor_hex="#EAB308",
        condicao_resumo="Previsão de chuva significativa (Nowcast 1-3h) em área de suscetibilidade Alta/Muito Alta.",
        acao_defesa_civil="Monitoramento reforçado a cada 10 min, comunicação interna e checagem preventiva de maré.",
        orgaos_acionados=["DEFESA_CIVIL_COMDEC", "OBSERVATORIO_CLIMA"],
        notificar_40199=False,
    ),
    "ATENCAO": ProtocoloOperacional(
        nivel="ATENCAO",
        cor_hex="#F97316",
        condicao_resumo="Chuva acumulada aproximando-se do limiar histórico do ponto crítico ou sobrecarga inicial de drenagem.",
        acao_defesa_civil="Equipes em prontidão, inspeção ativa das câmeras PMPU do ponto e acionamento de limpeza de bocas de lobo.",
        orgaos_acionados=["DEFESA_CIVIL_COMDEC", "PMPU_VIDEOMONITORAMENTO", "EMLURB_DRENAGEM"],
        notificar_40199=False,
    ),
    "ALERTA": ProtocoloOperacional(
        nivel="ALERTA",
        cor_hex="#EF4444",
        condicao_resumo="Chuva intensa em andamento + probabilidade calibrada moderada/alta de alagamento ou Lead Time <= 60 min.",
        acao_defesa_civil="Notificação imediata a equipes de campo, AMC (bloqueio preventivo de vias), Guarda Municipal e alerta geolocalizado 40199.",
        orgaos_acionados=[
            "DEFESA_CIVIL_COMDEC",
            "AMC_TRANSITO",
            "GUARDA_MUNICIPAL",
            "EMLURB_DRENAGEM",
            "CANAL_40199_SMS",
        ],
        notificar_40199=True,
    ),
    "ALARME": ProtocoloOperacional(
        nivel="ALARME",
        cor_hex="#991B1B",
        condicao_resumo="Limiar crítico atingido com alta probabilidade + confirmação visual por câmera PMPU (lâmina >= 15cm) ou múltiplos relatos 40199.",
        acao_defesa_civil="Acionamento operacional máximo, interdição viária imediata, envio de equipes de resgate/apoio social e comunicação pública de emergência.",
        orgaos_acionados=[
            "DEFESA_CIVIL_COMDEC",
            "CORPO_DE_BOMBEIROS_CIOPS",
            "AMC_TRANSITO",
            "GUARDA_MUNICIPAL",
            "SDHDS_ASSISTENCIA",
            "CANAL_40199_SMS",
            "IMPRENSA_OFICIAL",
        ],
        notificar_40199=True,
    ),
}

METAS_PILOTO = {
    "recall_minimo": 0.80,
    "precisao_minima": 0.50,
    "precisao_alvo_max": 0.75,
    "lead_time_min_minutos": 30.0,
    "lead_time_alvo_minutos": 60.0,
    "cobertura_areas_risco_min": 1.00,
}
