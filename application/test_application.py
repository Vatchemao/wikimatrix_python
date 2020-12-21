from application.extracteur import Extracteur


def test_nombreTableaux():
    extracteur = Extracteur("https://en.wikipedia.org/wiki/", "../output/html/test/", "../output/wikitext/")
    assert 8 == len(extracteur.extraire('Comparison_between_Esperanto_and_Ido')[1])


def test_nombreLignes():
    extracteur = Extracteur("https://en.wikipedia.org/wiki/", "../output/html/test/", "../output/wikitext/")
    extracteur.extraire('Comparison_of_World_War_I_tanks')
    assert 6 == len(extracteur.extraire('Comparison_of_World_War_I_tanks')[1][1].select('tr'))


def test_nombreColonnes():
    extracteur = Extracteur("https://en.wikipedia.org/wiki/", "../output/html/test/", "../output/wikitext/")
    extracteur.extraire('Comparison_of_World_War_I_tanks')
    assert 12 == len(
        extracteur.extraire('Comparison_of_World_War_I_tanks')[1][0].select('tr')[1].findChildren(recursive = False))


def test_largeurTableau():
    extracteur = Extracteur("https://en.wikipedia.org/wiki/", "../output/html/test/", "../output/wikitext/")
    assert 12 == extracteur.getLargeurTotaleTableau(extracteur.extraire('Comparison_of_ICBMs')[1][0], 0)


def test_nombreCellules():
    extracteur = Extracteur("https://en.wikipedia.org/wiki/", "../output/html/test/", "../output/wikitext/")
    assert 647 == len(extracteur.extraire('Comparison_of_ICBMs')[1][0].select('td')) + len(
        extracteur.extraire('Comparison_of_ICBMs')[1][0].select('th'))
