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

# Configurações Oficiais do Radar Meteorológico da FUNCEME (Fortaleza / RMF - GMWR1000SST)
FUNCEME_RADAR_PORTAL_URL: str = (
    "https://radar.funceme.br/radar/GMWR1000SST/prsf/RADAR_FORTALEZARMF/20/true/2/0"
)
FUNCEME_RADAR_API_URL: str = "https://api1.funceme.br/rpc/v1/produto-gerado"
FUNCEME_RADAR_ID: str = "GMWR1000SST"
FUNCEME_RADAR_NOME: str = "Radar Meteorológico Banda X FUNCEME — Fortaleza / RMF (Eusébio)"
FUNCEME_RADAR_CENTER: List[float] = [-3.89299, -38.45739]  # [lat, lon]
FUNCEME_RADAR_BOUNDS: List[float] = [-39.5916, -5.0230, -37.3235, -2.7608]  # [west_lon, south_lat, east_lon, north_lat]
FUNCEME_RADAR_LEGENDA_PRSF: str = "https://radar.funceme.br/assets/img/legenda_chuva_agora.png"
FUNCEME_RADAR_LEGENDA_ACUM: str = "https://radar.funceme.br/assets/img/legenda_acumulados.png"
FUNCEME_RADAR_KML_ALCANCE: str = "https://cdn.funceme.br/assets/kml/rangeGMWR1000SST.kml"


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


@dataclass(frozen=True)
class AbrigoTemporario:
    id_abrigo: str
    nome_escola: str
    tipo_estrutura: str
    bairro: str
    bairros_atendidos: List[str]
    regional: str
    endereco: str
    latitude: float
    longitude: float
    estacao_referencia_plugfield: int
    bacia_hidrografica: str
    capacidade_familias: int
    capacidade_pessoas: int
    salas_apoio: int
    recursos_disponiveis: List[str]
    contato_acionamento: str


# Rede de Escolas e Abrigos Temporários de Referência por Bairro (Extraídos da Relação Oficial SME / ASSEPLAN)
ABRIGOS_ESCOLAS_FORTALEZA: List[AbrigoTemporario] = [
    AbrigoTemporario(
        id_abrigo="SME_7402",
        nome_escola="ESCOLA MUNICIPAL MOURA BRASIL - EI / EF (COD 7402 • INEP 23074876)",
        tipo_estrutura="PAT - Escola Patrimonial (Distrito I)",
        bairro="Jacarecanga",
        bairros_atendidos=["Jacarecanga", "Moura Brasil", "Carlito Pamplona", "Pirambu"],
        regional="Distrito Educacional I (SER I)",
        endereco="RUA PADRE MORORÓ, 189 — JACARECANGA (CEP 60010-100)",
        latitude=-3.7222,
        longitude=-38.5435,
        estacao_referencia_plugfield=8642,
        bacia_hidrografica="Vertente Marítima",
        capacidade_familias=65,
        capacidade_pessoas=260,
        salas_apoio=12,
        recursos_disponiveis=["Quadra/Pátio Coberto", "Refeitório/Cozinha", "Banheiros M/F", "Apoio SDHDS"],
        contato_acionamento="OI: 3459-6802 | VoIP: 3459-5302 / 6802 • mourab@escola.sme.fortaleza.ce.gov.br",
    ),
    AbrigoTemporario(
        id_abrigo="SME_6982",
        nome_escola="ESCOLA MUNICIPAL ALBA FROTA - EI / EF (COD 6982 • INEP 23064870)",
        tipo_estrutura="PAT - Escola Patrimonial (Distrito II)",
        bairro="Centro",
        bairros_atendidos=["Centro", "Praia de Iracema", "Moura Brasil", "Farias Brito"],
        regional="Distrito Educacional II (SER Centro)",
        endereco="AV. DOM MANUEL, 914 — CENTRO (CEP 60060-090)",
        latitude=-3.7275,
        longitude=-38.5268,
        estacao_referencia_plugfield=8642,
        bacia_hidrografica="Vertente Marítima",
        capacidade_familias=65,
        capacidade_pessoas=260,
        salas_apoio=10,
        recursos_disponiveis=["Pátio Coberto", "Cozinha/Refeitório", "Vestiários", "Acessibilidade PCD"],
        contato_acionamento="OI: 3452-5892 / 3452-2426 | VoIP: 3459-5189 / 5298 / 6801 • infantilaf@escola.sme.fortaleza.ce.gov.br",
    ),
    AbrigoTemporario(
        id_abrigo="SME_6987",
        nome_escola="ESCOLA MUNICIPAL PROFESSOR CLODOALDO PINTO - EI / EF (COD 6987 • INEP 23188375)",
        tipo_estrutura="PAT - Escola Patrimonial (Distrito III)",
        bairro="Padre Andrade",
        bairros_atendidos=["Padre Andrade", "Antônio Bezerra", "Quintino Cunha", "Presidente Kennedy"],
        regional="Distrito Educacional III (SER III)",
        endereco="RUA BANVARTH BEZERRA, 100 — PADRE ANDRADE (CEP 60356-400)",
        latitude=-3.7392,
        longitude=-38.5812,
        estacao_referencia_plugfield=3318,
        bacia_hidrografica="Maranguapinho",
        capacidade_familias=65,
        capacidade_pessoas=260,
        salas_apoio=12,
        recursos_disponiveis=["Quadra Coberta", "Cozinha/Refeitório", "Vestiários", "Kits Colchões SDHDS"],
        contato_acionamento="OI: 3433-9744 / 3478-4008 | VoIP: 3459-5323 / 5480 / 6829 • clodoaldop@escola.sme.fortaleza.ce.gov.br",
    ),
    AbrigoTemporario(
        id_abrigo="SME_7081",
        nome_escola="ESCOLA MUNICIPAL MURILO SERPA - EF (COD 7081 • INEP 23257237)",
        tipo_estrutura="PAT - Escola Patrimonial (Distrito III)",
        bairro="Dom Lustosa",
        bairros_atendidos=["Dom Lustosa", "Autran Nunes", "Henrique Jorge", "João XXIII", "Pici"],
        regional="Distrito Educacional III (SER III)",
        endereco="RUA MONSENHOR HIPÓLITO BRASIL, 1400 — DOM LUSTOSA (CEP 60526-055)",
        latitude=-3.7518,
        longitude=-38.5915,
        estacao_referencia_plugfield=3318,
        bacia_hidrografica="Maranguapinho",
        capacidade_familias=70,
        capacidade_pessoas=280,
        salas_apoio=14,
        recursos_disponiveis=["Quadra Poliesportiva", "Refeitório Amplo", "Vestiários", "Acessibilidade PCD"],
        contato_acionamento="OI: 3290-7327 | VoIP: 3459-5325 / 6725 • murilos@escola.sme.fortaleza.ce.gov.br",
    ),
    AbrigoTemporario(
        id_abrigo="SME_7083",
        nome_escola="ESCOLA MUNICIPAL HERONDINA LIMA CAVALCANTE - EF (COD 7083 • INEP 23234318)",
        tipo_estrutura="PAT - Escola Patrimonial (Distrito I)",
        bairro="Vila Velha",
        bairros_atendidos=["Vila Velha", "Barra do Ceará", "Jardim Guanabara", "Cristo Redentor"],
        regional="Distrito Educacional I (SER I)",
        endereco="AV. D, 310, CONJUNTO BEIRA RIO — VILA VELHA (CEP 60348-100)",
        latitude=-3.7145,
        longitude=-38.5965,
        estacao_referencia_plugfield=8869,
        bacia_hidrografica="Rio Ceará / Vertente Marítima",
        capacidade_familias=65,
        capacidade_pessoas=260,
        salas_apoio=11,
        recursos_disponiveis=["Quadra Coberta", "Cozinha/Refeitório", "Vestiários", "Acessibilidade PCD"],
        contato_acionamento="OI: 3452-6674 / 3452-6673 | VoIP: 3459-5160 / 5288 / 6714 • herondinalc@escola.sme.fortaleza.ce.gov.br",
    ),
    AbrigoTemporario(
        id_abrigo="SME_6924",
        nome_escola="ESCOLA MUNICIPAL DOM ANTONIO DE ALMEIDA LUSTOSA - EI / EF (COD 6924 • INEP 23065265)",
        tipo_estrutura="PAT - Escola Patrimonial (Distrito V)",
        bairro="Granja Lisboa",
        bairros_atendidos=["Granja Lisboa", "Granja Portugal", "Bom Jardim", "Siqueira", "Conjunto Ceará I e II"],
        regional="Distrito Educacional V (SER V)",
        endereco="RUA GERALDO BARBOSA, 3901 — GRANJA LISBOA (CEP 60540-344)",
        latitude=-3.7882,
        longitude=-38.6154,
        estacao_referencia_plugfield=9282,
        bacia_hidrografica="Maranguapinho",
        capacidade_familias=75,
        capacidade_pessoas=300,
        salas_apoio=14,
        recursos_disponiveis=["Ginásio Coberto", "Cozinha Industrial", "Vestiários M/F", "Apoio Psicossocial SDHDS"],
        contato_acionamento="OI: 3452-2460 / 3497-1863 | VoIP: 3459-5234 / 6985 • domaal@escola.sme.fortaleza.ce.gov.br",
    ),
    AbrigoTemporario(
        id_abrigo="SME_7167",
        nome_escola="ESCOLA MUNICIPAL ROSA AMARO CAVALCANTE - EI / EF (COD 7167 • INEP 23256990)",
        tipo_estrutura="PAT - Escola Patrimonial (Distrito IV)",
        bairro="Conjunto Esperança",
        bairros_atendidos=["Conjunto Esperança", "Mondubim", "Canindezinho", "Planalto Ayrton Senna", "Manoel Sátiro"],
        regional="Distrito Educacional IV / V",
        endereco="RUA ALFREDO MAMEDE, 1064 — CONJUNTO ESPERANÇA (CEP 60763-425)",
        latitude=-3.8142,
        longitude=-38.5885,
        estacao_referencia_plugfield=9134,
        bacia_hidrografica="Maranguapinho",
        capacidade_familias=65,
        capacidade_pessoas=260,
        salas_apoio=11,
        recursos_disponiveis=["Quadra Coberta", "Refeitório", "Banheiros Coletivos", "Acessibilidade PCD"],
        contato_acionamento="OI: 3296-7353 | VoIP: 3459-5367 / 5575 / 6854 • rosaac@escola.sme.fortaleza.ce.gov.br",
    ),
    AbrigoTemporario(
        id_abrigo="SME_7411",
        nome_escola="ESCOLA MUNICIPAL CAROLINO SUCUPIRA - EI / EF (COD 7411 • INEP 23324244)",
        tipo_estrutura="PAT - Escola Patrimonial (Distrito IV)",
        bairro="Itaoca",
        bairros_atendidos=["Itaoca", "Montese", "Parangaba", "Vila União", "Jardim América", "Serrinha"],
        regional="Distrito Educacional IV (SER IV)",
        endereco="RUA MUNDICA PAULA, S/N — ITAOCA / MONTESE (CEP 60421-410)",
        latitude=-3.7725,
        longitude=-38.5580,
        estacao_referencia_plugfield=8836,
        bacia_hidrografica="Cocó / Tauape",
        capacidade_familias=65,
        capacidade_pessoas=260,
        salas_apoio=11,
        recursos_disponiveis=["Quadra Coberta", "Cozinha/Refeitório", "Vestiários", "Estação Pluviométrica Local"],
        contato_acionamento="OI: 3433-8520 / 3232-3936 | VoIP: 3459-5346 / 6705 • carolinos@escola.sme.fortaleza.ce.gov.br",
    ),
    AbrigoTemporario(
        id_abrigo="SME_6990",
        nome_escola="ESCOLA MUNICIPAL ANTONIO SALES - EI / EF (COD 6990 • INEP 23065397)",
        tipo_estrutura="PAT - Escola Patrimonial (Distrito III)",
        bairro="Rodolfo Teófilo / Benfica",
        bairros_atendidos=["Benfica", "Rodolfo Teófilo", "Farias Brito", "Amadeu Furtado", "Bela Vista"],
        regional="Distrito Educacional III / IV",
        endereco="RUA TAVARES IRACEMA, 675 — RODOLFO TEÓFILO / BENFICA (CEP 60430-070)",
        latitude=-3.7452,
        longitude=-38.5485,
        estacao_referencia_plugfield=9281,
        bacia_hidrografica="Vertente Marítima / Tauape",
        capacidade_familias=60,
        capacidade_pessoas=240,
        salas_apoio=10,
        recursos_disponiveis=["Pátio Coberto", "Cozinha/Refeitório", "Banheiros Adaptados", "Acessibilidade PCD"],
        contato_acionamento="OI: 3281-8815 / 3105-3423 | VoIP: 3459-5311 / 5415 / 6809 • antonios@escola.sme.fortaleza.ce.gov.br",
    ),
    AbrigoTemporario(
        id_abrigo="SME_6961",
        nome_escola="ESCOLA MUNICIPAL PROFESSORA EDITH BRAGA - EI / EF (COD 6961 • INEP 23068175)",
        tipo_estrutura="PAT - Escola Patrimonial (Distrito II)",
        bairro="Aerolândia",
        bairros_atendidos=["Aerolândia", "Comunidade do Lagamar", "Alto da Balança", "São João do Tauape", "Dias Macedo"],
        regional="Distrito Educacional II",
        endereco="RUA CAPITÃO VASCONCELOS, 1061 — AEROLÂNDIA (CEP 60850-680)",
        latitude=-3.7652,
        longitude=-38.5138,
        estacao_referencia_plugfield=9242,
        bacia_hidrografica="Cocó / Tauape",
        capacidade_familias=75,
        capacidade_pessoas=300,
        salas_apoio=14,
        recursos_disponiveis=["Ginásio Coberto", "Cozinha Industrial", "Vestiários M/F", "Kits Emergência SDHDS"],
        contato_acionamento="OI: 3433-5297 | VoIP: 3459-5396 / 5492 • professoraeb@escola.sme.fortaleza.ce.gov.br",
    ),
    AbrigoTemporario(
        id_abrigo="SME_6981",
        nome_escola="ESCOLA MUNICIPAL JOSE RAMOS TORRES DE MELO - EI / EF (COD 6981 • INEP 23072512)",
        tipo_estrutura="PAT - Escola Patrimonial (Distrito II)",
        bairro="Mucuripe",
        bairros_atendidos=["Mucuripe", "Aldeota", "Meireles", "Vicente Pinzon", "Cais do Porto", "Papicu"],
        regional="Distrito Educacional II (SER II)",
        endereco="AV. DA ABOLIÇÃO, 3984 — MUCURIPE (CEP 60165-085)",
        latitude=-3.7260,
        longitude=-38.4838,
        estacao_referencia_plugfield=9137,
        bacia_hidrografica="Vertente Marítima",
        capacidade_familias=65,
        capacidade_pessoas=260,
        salas_apoio=12,
        recursos_disponiveis=["Quadra Coberta", "Refeitório", "Vestiários", "Acessibilidade PCD"],
        contato_acionamento="OI: 3263-1360 / 3452-7344 | VoIP: 3459-5196 / 5227 / 6887 • josertm@escola.sme.fortaleza.ce.gov.br",
    ),
    AbrigoTemporario(
        id_abrigo="SME_7188",
        nome_escola="ESCOLA MUNICIPAL JOSE RAMOS TORRES DE MELO - UND II (COD 7188 • INEP 23072512)",
        tipo_estrutura="ANE - Anexo Escolar (Distrito II)",
        bairro="Aldeota",
        bairros_atendidos=["Aldeota", "Meireles", "Joaquim Távora", "Vicente Pinzon", "Praia do Futuro I e II"],
        regional="Distrito Educacional II (SER II)",
        endereco="AV. DESEMBARGADOR MOREIRA, 2121 — ALDEOTA (CEP 60170-002)",
        latitude=-3.7385,
        longitude=-38.5015,
        estacao_referencia_plugfield=9137,
        bacia_hidrografica="Vertente Marítima / Riacho Pajeú",
        capacidade_familias=55,
        capacidade_pessoas=220,
        salas_apoio=10,
        recursos_disponiveis=["Pátio Coberto", "Refeitório", "Vestiários", "Acessibilidade PCD"],
        contato_acionamento="OI: 3452-7354 / 3261-0633 • comunsvp@escola.sme.fortaleza.ce.gov.br",
    ),
    AbrigoTemporario(
        id_abrigo="SME_6972",
        nome_escola="ESCOLA MUNICIPAL PROF. FRANCISCO DE MELO JABORANDI - EI / EF (COD 6972 • INEP 23070013)",
        tipo_estrutura="PAT - Escola Patrimonial (Distrito VI)",
        bairro="Jangurussu",
        bairros_atendidos=["Jangurussu", "Conjunto Palmeiras", "Barroso", "Passaré", "Ancuri"],
        regional="Distrito Educacional VI (SER VI)",
        endereco="AV. GOVERNADOR LEONEL BRIZOLA, 198 — JANGURUSSU (CEP 60866-190)",
        latitude=-3.8385,
        longitude=-38.5215,
        estacao_referencia_plugfield=9249,
        bacia_hidrografica="Cocó",
        capacidade_familias=75,
        capacidade_pessoas=300,
        salas_apoio=14,
        recursos_disponiveis=["Ginásio Poliesportivo", "Refeitório Completo", "Vestiários", "Kits Colchões SDHDS"],
        contato_acionamento="OI: 3269-4030 / 3452-6763 | VoIP: 3459-5399 / 5450 / 6984 • franciscomj@escola.sme.fortaleza.ce.gov.br",
    ),
    AbrigoTemporario(
        id_abrigo="SME_7222",
        nome_escola="ESCOLA MUNICIPAL PROFESSORA RAIMUNDA FELIX DE ALCANTARA - EF (COD 7222 • INEP 23323469)",
        tipo_estrutura="PAT - Escola Patrimonial (Distrito VI)",
        bairro="Messejana",
        bairros_atendidos=["Messejana", "Paupina", "Lagoa Redonda", "Curió", "Guajiru", "Coaçu", "Pedras"],
        regional="Distrito Educacional VI (SER VI)",
        endereco="AV. MEM DE SÁ, 384 — MESSEJANA (CEP 60841-130 • Sede Estação PCD 9169)",
        latitude=-3.8256,
        longitude=-38.4850,
        estacao_referencia_plugfield=9169,
        bacia_hidrografica="Cocó",
        capacidade_familias=65,
        capacidade_pessoas=260,
        salas_apoio=11,
        recursos_disponiveis=["Quadra Coberta", "Cozinha/Refeitório", "Vestiários", "Estação Pluviométrica Local"],
        contato_acionamento="OI: 3274-1054 | VoIP: 3459-5116 / 5134 / 7131 • praimundafa@escola.sme.fortaleza.ce.gov.br",
    ),
]

