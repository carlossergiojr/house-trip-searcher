from radar.imoveis import vivareal, olx
from radar.imoveis.modelo import interessa


def test_vivareal_casa_santa_monica():
    card = {
        "href": "https://www.vivareal.com.br/imovel/casa-de-condominio-3-quartos-santa-monica-"
                "bairros-feira-de-santana-com-garagem-100m2-aluguel-RS2500-id-2916683784/",
        "txt": "",
    }
    i = vivareal.parse_card("vivareal", card)
    assert (i.id, i.bairro, i.tipo, i.quartos, i.area, i.preco) == (
        "2916683784", "Santa Mônica", "casa de condominio", 3, 100, 2500)
    assert interessa(i)


def test_vivareal_ponto_comercial_descartado():
    card = {"href": "https://www.vivareal.com.br/imovel/ponto-comercial-santa-monica-bairros-"
                    "feira-de-santana-com-garagem-80m2-aluguel-RS2000-id-2850403321/", "txt": ""}
    assert not interessa(vivareal.parse_card("vivareal", card))


def test_zap_preco_do_texto_e_bairro_fora():
    dentro = {"href": "https://www.zapimoveis.com.br/imovel/aluguel-apartamento-2-quartos-"
                      "lagoa-salgada-feira-de-santana-ba-60m2-id-2900000001/",
              "txt": "Apartamento para alugar em R$ 1.900 /mês Cond. R$ 200"}
    fora = {"href": "https://www.zapimoveis.com.br/imovel/aluguel-apartamento-2-quartos-"
                    "sim-feira-de-santana-ba-45m2-id-2923226533/", "txt": "R$ 1.500"}
    i = vivareal.parse_card("zap", dentro)
    assert (i.tipo, i.bairro, i.preco, i.quartos) == ("apartamento", "Lagoa Salgada", 1900, 2)
    assert vivareal.parse_card("zap", fora) is None


def test_olx_card():
    card = {"href": "https://ba.olx.com.br/regiao-de-feira-de-santana-e-alagoinhas/imoveis/"
                    "casa-3-4-1555256999",
            "txt": "Casa 3/4 com garagem\n90m²\n3\nDireto com o proprietário\nR$ 1.350\n"
                   "Feira de Santana, Brasília\nHoje, 10:27"}
    i = olx.parse_card("casa", card)
    assert (i.id, i.bairro, i.preco, i.area) == ("1555256999", "Brasília", 1350, 90)


def test_olx_comercial_e_outro_bairro():
    base = "https://ba.olx.com.br/x/imoveis/y-1555256573"
    assert olx.parse_card("casa", {"href": base, "txt":
        "Alugo Ponto Comercial\nR$ 1.350\nFeira de Santana, Brasília"}) is None
    assert olx.parse_card("casa", {"href": base, "txt":
        "Casa\nR$ 900\nFeira de Santana, Conceição"}) is None


def test_luiz_eduardo_variacao():
    card = {"href": "https://www.zapimoveis.com.br/imovel/aluguel-casa-2-quartos-conjunto-"
                    "luis-eduardo-magalhaes-feira-de-santana-ba-70m2-id-2900000002/", "txt": "R$ 1.200"}
    assert vivareal.parse_card("zap", card).bairro == "Conjunto Luiz Eduardo"


def test_bairro_parecido_nao_conta():
    from radar.imoveis.modelo import bairro_alvo
    assert bairro_alvo("Brasília") == "Brasília"
    assert bairro_alvo("Parque Brasília") is None
    assert bairro_alvo("Jardim Brasília") is None
    assert bairro_alvo("Conjunto Luiz Eduardo Magalhães") == "Conjunto Luiz Eduardo"
    assert bairro_alvo("casa-3-quartos-santa-monica-bairros".replace("-", " ")) == "Santa Mônica"


def test_preco_estranho_nao_quebra():
    from radar.comum.texto import extrair_preco
    assert extrair_preco("R$ .") is None
    assert extrair_preco("R$ 1.600,00 /mês") == 1600


def test_olx_preco_com_desconto_e_iptu():
    card = {"href": "https://ba.olx.com.br/x/imoveis/casa-1555000001",
            "txt": "Casa 3/4\nR$ 2.700\nR$ 2.400\nIPTU R$ 50\nCondomínio R$ 300\n"
                   "Feira de Santana, Brasília"}
    i = olx.parse_card("casa", card)
    assert i.preco == 2400 and interessa(i)


def test_olx_titulo_cita_a_cidade():
    card = {"href": "https://ba.olx.com.br/x/imoveis/casa-1555000002",
            "txt": "Casa perto da Av. Feira de Santana, centro\nR$ 1.000\n"
                   "Feira de Santana, Brasília"}
    assert olx.parse_card("casa", card).bairro == "Brasília"


# Texto real de um card do VivaReal (nov/2026).
CARD_VIVAREAL_REAL = {
    "href": "https://www.vivareal.com.br/imovel/casa-4-quartos-brasilia-bairros-feira-de-santana-"
            "com-garagem-137m2-aluguel-RS1600-id-2899130712/",
    "txt": "\n+8 fotos\nGeanne Mota lopes\nCasa para alugar com 137 m², 4 quartos, 2 banheiros, "
           "2 vagas em\n\nR$ 1.600\n/mês\n\nCond. não informado • IPTU não informado\n\n"
           "Tamanho do imóvel\n137 m²\nQuantidade de quartos\n4\nQuantidade de banheiros\n2\n"
           "Quantidade de vagas de garagem\n2\nBrasília, Feira de Santana\n\n"
           "Avenida Adenil Falcão\n\nContatar",
}


def test_vivareal_detalhes_do_card_real():
    i = vivareal.parse_card("vivareal", CARD_VIVAREAL_REAL)
    assert (i.preco, i.quartos, i.banheiros, i.vagas, i.area) == (1600, 4, 2, 2, 137)
    assert (i.condominio, i.iptu, i.endereco) == (None, None, "Avenida Adenil Falcão")
    legenda = i.legenda()
    assert "4 quartos · 2 banheiros · 2 vagas · 137 m²" in legenda
    assert "📍 Avenida Adenil Falcão" in legenda and "Cond. não informado · IPTU não informado" in legenda
    assert "Total" not in legenda and "Acima" not in legenda


def test_vivareal_taxas_e_total_acima_do_teto():
    card = dict(CARD_VIVAREAL_REAL, txt=CARD_VIVAREAL_REAL["txt"]
                .replace("R$ 1.600", "R$ 2.300")
                .replace("Cond. não informado • IPTU não informado", "Cond. R$ 250 • IPTU R$ 40"))
    i = vivareal.parse_card("vivareal", card)
    assert (i.condominio, i.iptu, i.total) == (250, 40, 2590)
    assert interessa(i)  # o aluguel cabe na busca; o total passa do teto e vem marcado
    assert "Total ≈ <b>R$ 2.590</b>" in i.legenda() and "Acima do teto de R$ 2.500" in i.legenda()


def test_condominio_isento():
    card = dict(CARD_VIVAREAL_REAL, txt=CARD_VIVAREAL_REAL["txt"].replace(
        "Cond. não informado", "Cond. isento"))
    i = vivareal.parse_card("vivareal", card)
    assert i.condominio == 0 and "Cond. isento" in i.legenda()


def test_margem_de_busca_acima_do_teto():
    from radar import config
    card = {"href": "https://ba.olx.com.br/x/imoveis/casa-1555000004",
            "txt": "Casa 3/4\nR$ 2.700\nFeira de Santana, Brasília"}
    i = olx.parse_card("casa", card)
    assert interessa(i) and "Acima do teto" in i.legenda()
    i.preco = config.ALUGUEL_BUSCA + 1
    assert not interessa(i)


def test_olx_quartos_taxas_e_rotulos():
    card = {"href": "https://ba.olx.com.br/x/imoveis/apartamento-1555000005",
            "txt": "Apartamento 2/4 no Brasília\n60m²\n2\n1\nR$ 1.400\nCondomínio R$ 180\n"
                   "IPTU R$ 30\nFeira de Santana, Brasília",
            "rotulos": "2 quartos\n60 metros quadrados\n1 vaga de garagem\n1 banheiro"}
    i = olx.parse_card("apartamento", card)
    assert (i.preco, i.quartos, i.vagas, i.banheiros) == (1400, 2, 1, 1)
    assert (i.condominio, i.iptu, i.total) == (180, 30, 1610)
    sem_rotulo = olx.parse_card("apartamento", dict(card, rotulos=""))
    assert sem_rotulo.quartos == 2  # do "2/4" no título
