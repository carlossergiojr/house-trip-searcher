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
