from application.extracteur import Extracteur

if __name__ == "__main__":
    """
    try:
        extracteur = Extracteur("https://en.wikipedia.org/wiki/","../output/html/","../output/wikitext/")
        nbEchecs = 0
        listeEchecs = []
        listeTableaux = []
        file = open("../input/wikiurls.txt", "r")
        urls = file.readlines()
        for i in range(len(urls)):
            url = urls[i]
            logging.debug("On extrait les tableaux de l'url n° : " + str(i) + " (" + url + ").")
            retour = extracteur.extraire(url)
            if (retour[0]):
                nbEchecs += 1
                listeEchecs.append(url)
            listeTableaux.append(retour[1])
    except:
        print("Le programme a dû s'interrompre, désolé :'(")
    """

    extracteur = Extracteur("https://en.wikipedia.org/wiki/", "../output/html/test/", "../output/wikitext/")
    extracteur.extraire("Comparison_between_Esperanto_and_Ido")
