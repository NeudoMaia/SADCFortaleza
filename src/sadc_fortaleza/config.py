"""
Configurações georreferenciadas, malha de pontos críticos, estações meteorológicas,
câmeras do PMPU e protocolos operacionais da Defesa Civil de Fortaleza.
"""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class EstacaoMeteorologica:
    id_estacao: str
    nome: str
    orgao: str  # "DEFESA_CIVIL", "FUNCEME", "CEMADEN"
    bairro: str
    latitude: float
    longitude: float
    bacia_hidrografica: str
    intervalo_leitura_min: int = 10


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
    fator_decaimento_api: float  # k para chuva antecedente (maior em bacias com lagoas/canais)
    influencia_mare: float       # 0.0 (interior) a 1.0 (costeiro/estuarino direto)
    ocorrencias_2021_2024: int   # Histórico DCFor 2021-2024
    anos_recorrencia_consecutivos: int
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


# Rede integrada de estações (11 Estações Automáticas Defesa Civil + Postos Funceme/CEMADEN)
ESTACOES_FORTALEZA: List[EstacaoMeteorologica] = [
    EstacaoMeteorologica(
        id_estacao="DC_01",
        nome="PCD Defesa Civil - Jacarecanga / Moura Brasil",
        orgao="DEFESA_CIVIL",
        bairro="Jacarecanga",
        latitude=-3.7218,
        longitude=-38.5432,
        bacia_hidrografica="Vertente Marítima",
    ),
    EstacaoMeteorologica(
        id_estacao="DC_02",
        nome="PCD Defesa Civil - Padre Andrade / Antônio Bezerra",
        orgao="DEFESA_CIVIL",
        bairro="Padre Andrade",
        latitude=-3.7395,
        longitude=-38.5840,
        bacia_hidrografica="Maranguapinho",
    ),
    EstacaoMeteorologica(
        id_estacao="DC_03",
        nome="PCD Defesa Civil - Aldeota / Parque Bisão",
        orgao="DEFESA_CIVIL",
        bairro="Aldeota",
        latitude=-3.7362,
        longitude=-38.4975,
        bacia_hidrografica="Vertente Marítima",
    ),
    EstacaoMeteorologica(
        id_estacao="DC_04",
        nome="PCD Defesa Civil - Itaoca / Parangaba",
        orgao="DEFESA_CIVIL",
        bairro="Itaoca",
        latitude=-3.7685,
        longitude=-38.5538,
        bacia_hidrografica="Cocó / Tauape",
    ),
    EstacaoMeteorologica(
        id_estacao="DC_05",
        nome="PCD Defesa Civil - Mucuripe / Cais do Porto",
        orgao="DEFESA_CIVIL",
        bairro="Mucuripe",
        latitude=-3.7190,
        longitude=-38.4765,
        bacia_hidrografica="Vertente Marítima",
    ),
    EstacaoMeteorologica(
        id_estacao="DC_06",
        nome="PCD Defesa Civil - Barra do Ceará",
        orgao="DEFESA_CIVIL",
        bairro="Barra do Ceará",
        latitude=-3.7055,
        longitude=-38.5820,
        bacia_hidrografica="Rio Ceará",
    ),
    EstacaoMeteorologica(
        id_estacao="DC_07",
        nome="PCD Defesa Civil - Messejana",
        orgao="DEFESA_CIVIL",
        bairro="Messejana",
        latitude=-3.8310,
        longitude=-38.4930,
        bacia_hidrografica="Cocó",
    ),
    EstacaoMeteorologica(
        id_estacao="DC_08",
        nome="PCD Defesa Civil - Mondubim",
        orgao="DEFESA_CIVIL",
        bairro="Mondubim",
        latitude=-3.8060,
        longitude=-38.5720,
        bacia_hidrografica="Maranguapinho",
    ),
    EstacaoMeteorologica(
        id_estacao="DC_09",
        nome="PCD Defesa Civil - Aerolândia / Lagamar",
        orgao="DEFESA_CIVIL",
        bairro="Aerolândia",
        latitude=-3.7690,
        longitude=-38.5130,
        bacia_hidrografica="Cocó / Tauape",
    ),
    EstacaoMeteorologica(
        id_estacao="DC_10",
        nome="PCD Defesa Civil - Jangurussu",
        orgao="DEFESA_CIVIL",
        bairro="Jangurussu",
        latitude=-3.8365,
        longitude=-38.5325,
        bacia_hidrografica="Cocó",
    ),
    EstacaoMeteorologica(
        id_estacao="DC_11",
        nome="PCD Defesa Civil - Centro / Paço Municipal",
        orgao="DEFESA_CIVIL",
        bairro="Centro",
        latitude=-3.7258,
        longitude=-38.5245,
        bacia_hidrografica="Vertente Marítima",
    ),
    EstacaoMeteorologica(
        id_estacao="FUNCEME_01",
        nome="Posto Pluviométrico Funceme - Pici",
        orgao="FUNCEME",
        bairro="Pici",
        latitude=-3.7460,
        longitude=-38.5740,
        bacia_hidrografica="Maranguapinho",
    ),
    EstacaoMeteorologica(
        id_estacao="CEMADEN_01",
        nome="PCD CEMADEN - Montese / Itaoca",
        orgao="CEMADEN",
        bairro="Montese",
        latitude=-3.7620,
        longitude=-38.5460,
        bacia_hidrografica="Cocó / Tauape",
    ),
]


# Malha de Pontos Críticos e Microbacias (4 Áreas-Piloto + Pontos de Controle para Transferência)
PONTOS_CRITICOS: List[PontoCritico] = [
    # 1. Piloto Jacarecanga: Zona baixa costeira/estuarina, canal São Gerardo/Jacarecanga, forte efeito de maré
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
        cameras_pmpu=["CAM_PMPU_012", "CAM_PMPU_013", "CAM_RISCO_004"],
        populacao_exposta_estimada=4850,
    ),
    # 2. Piloto Padre Andrade: Bacia do Maranguapinho, recorrência crônica e influência de canal/rio urbano
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
        cameras_pmpu=["CAM_RISCO_011", "CAM_PMPU_041"],
        populacao_exposta_estimada=5600,
    ),
    # 3. Piloto Aldeota: Bacia altamente verticalizada e impermeabilizada, alagamento rápido por microdrenagem
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
        cameras_pmpu=["CAM_PMPU_022", "CAM_PMPU_023"],
        populacao_exposta_estimada=3200,
    ),
    # 4. Piloto Itaoca: Depressão topográfica e influência de canal/lagoa urbana, alta sensibilidade a acumulados
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
        cameras_pmpu=["CAM_RISCO_019", "CAM_PMPU_058"],
        populacao_exposta_estimada=4100,
    ),
    # 5. Ponto Crítico Complementar (Alto Risco): Aerolândia / Lagamar (para enriquecer treinamento multi-bacia)
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
        cameras_pmpu=["CAM_RISCO_001", "CAM_RISCO_002", "CAM_PMPU_081"],
        populacao_exposta_estimada=7400,
    ),
    # 6. Ponto de Controle (Baixo/Médio Risco): Messejana Alta (para calibração de especificidade espacial)
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
        cameras_pmpu=["CAM_PMPU_095"],
        populacao_exposta_estimada=950,
    ),
]


PROTOCOLOS_OPERACIONAIS: Dict[str, ProtocoloOperacional] = {
    "NORMAL": ProtocoloOperacional(
        nivel="NORMAL",
        cor_hex="#10B981",
        condicao_resumo="Sem chuva relevante e indicadores hidrometeorológicos abaixo do limiar de vigilância.",
        acao_defesa_civil="Monitoramento de rotina nas estações automáticas e manutenção preventiva de drenagem.",
        orgaos_acionados=["CIOPS_ROTINA"],
        notificar_40199=False,
    ),
    "VIGILANCIA": ProtocoloOperacional(
        nivel="VIGILANCIA",
        cor_hex="#F59E0B",
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
        cor_hex="#7F1D1D",
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

# Metas operacionais definidas no planejamento
METAS_PILOTO = {
    "recall_minimo": 0.80,
    "precisao_minima": 0.50,
    "precisao_alvo_max": 0.75,
    "lead_time_min_minutos": 30.0,
    "lead_time_alvo_minutos": 60.0,
    "cobertura_areas_risco_min": 1.00,
}
