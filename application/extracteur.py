from bs4 import BeautifulSoup
from urllib.request import urlopen

from application.rowspan import Rowspan

import logging
import csv

# Avant toutes choses, on définit le niveau de log :
logging.basicConfig(level=logging.DEBUG)


class Extracteur:
    """
    Classe représentant l'extracteur de wikitables.
    """

    def __init__(self):
        self.BASE_WIKIPEDIA_URL = ""
        self.outputDirHtml = ""
        self.outputDirWikitext = ""

    def __init__(self, BASE_WIKIPEDIA_URL, outputDirHtml, outputDirWikitext):
        self.BASE_WIKIPEDIA_URL = BASE_WIKIPEDIA_URL
        self.outputDirHtml = outputDirHtml
        self.outputDirWikitext = outputDirWikitext

    def extraire(self, url):
        try:
            listeTableaux = []
            logging.debug("Début de l'extraction des tableaux de l'url suivante : " + url)
            wurl = self.BASE_WIKIPEDIA_URL + url
            page = urlopen(wurl)
            file = page.read()
            document = BeautifulSoup(file, features="html.parser")
            tableaux = document.find_all('table',{'class':'wikitable'})
            logging.debug("Il y a " + str(len(tableaux)) + " tableaux dans cette url.")
            for i in range(len(tableaux)):
                tableau = tableaux[i]
                self.traiterTableau(tableau, url, i)
                listeTableaux.append(tableau)
            logging.debug("Fin de l'extraction des tableaux de l'url suivante : " + url)
            return False, listeTableaux
        except:
            logging.WARN("Cette url n'a pas pu être traitée. Le traitement va se poursuivre.")
            return False, listeTableaux

    def traiterTableau(self, tableau, url, i):
        logging.debug("Début du traitement du tableau n° " + str(i + 1))
        try:
            # On initialise le fichier csv.
            csvFileName = self.mkCSVFileName(url, i + 1)
            logging.debug("Le fichier est créé ici : " + self.outputDirHtml + csvFileName);
            csvFile = open(self.outputDirHtml + csvFileName, 'w', newline = '', encoding = 'utf-8')
            writer = csv.writer(csvFile, delimiter = ';')
            largeurTableau = self.getLargeurTotaleTableau(tableau, 0)
            # On initialise le dictionnaire de rowspans et les lignes.
            dicoRowspans = {}
            lignes = tableau.find_all('tr')
            # On traite les headers
            nbHeaders = self.traiterHeaders(lignes, largeurTableau, writer)
            # On supprime les headers des lignes
            for j in range(nbHeaders):
                del lignes[0]
            for k in range(len(lignes)):
                logging.debug("On traite la ligne " + str(k) + ".")
                dicoRowspans = self.traiterLigne(dicoRowspans, lignes[k], largeurTableau, writer)
            logging.debug("Fin du traitement du tableau n° " + str(i+1))
        except:
            logging.WARN("Ce tableau n'a pas pu être traité. Le traitement va se poursuivre.")

    def traiterHeaders(self, lignes, largeurTableau, writer):
        try:
            headers = []
            nombreHeaders = 0
            while self.isHeader(lignes[nombreHeaders]):
                headers.append(lignes[nombreHeaders])
                nombreHeaders += 1
            if nombreHeaders > 0:
                self.ecrireHeaders(headers, largeurTableau, writer)
            return nombreHeaders
        except:
            logging.WARN("Ce header n'a pas pu être traité. Le traitement va se poursuivre.")
            return nombreHeaders

    def ecrireHeaders(self, headers, largeurTableau, writer):
        try:
            if len(headers) == 1:
                listeHeaders1 = self.traiterUnHeader(headers)[0]
                writer.writerow(listeHeaders1)
            elif len(headers) == 2:
                listeHeaders2 = self.traiterDeuxHeaders(headers)
                writer.writerow(listeHeaders2)
            else:
                dicoRowspans = {}
                for i in range(len(headers)):
                    ligne = headers[i]
                    dicoRowspans = self.traiterLigne(dicoRowspans, ligne, largeurTableau, writer)
        except:
            logging.WARN("Ce header n'a pas pu être écrit. Le traitement va se poursuivre.")

    def traiterUnHeader(self, headers):
        try:
            cellules = headers[0].findChildren(recursive = False)
            listeHeaders = []
            dicoRowspans = {}
            decalageColspans = 0
            for j in range(len(cellules)):
                if not cellules[j].has_attr('colspan'):
                    if not cellules[j].has_attr('rowspan'):
                        # Cas où il n'y a ni colspan ni rowspan.
                        listeHeaders.append(cellules[j].text.strip())
                    else:
                        # Cas où il n'y pas de colspan mais un rowspan
                        dicoRowspans[j + decalageColspans] = Rowspan(int(cellules[j].attrs.get('rowspan')), cellules[j].text.strip())
                        listeHeaders.append(cellules[j].text.strip())
                else:
                    if not cellules[j].has_attr('rowspan'):
                        # Cas où il y un colspan mais pas de rowspan
                        for k in range(int(cellules[j].attrs.get('colspan'))):
                            listeHeaders.append(cellules[j].text.strip())
                        decalageColspans += int(cellules[j].attrs.get('colspan')) - 1
                    else:
                        # Cas où il y a un rowspan et un colspan
                        for l in range(int(cellules[j].attrs.get('colspan'))):
                            listeHeaders.append(cellules[j].text.strip())
                            dicoRowspans[j + l + decalageColspans] = Rowspan(int(cellules[j].attrs.get('colspan')), cellules[j].text.strip())
                        decalageColspans += int(cellules[j].attrs.get('colspan')) - 1
            return listeHeaders, dicoRowspans
        except:
            logging.WARN("Ce header n'a pas pu être traité. Le traitement va se poursuivre.")
            return listeHeaders, dicoRowspans

    def traiterDeuxHeaders(self, headers):
        try:
            retourTraiterUnHeader = self.traiterUnHeader(headers)
            listeHeaders1 = retourTraiterUnHeader[0]
            dicoRowspans = retourTraiterUnHeader[1]
            listeHeaders2 = []
            nouvelleMapRowspans = {}
            idecale = 0
            cellules2 = headers[1].findChildren(recursive = False)
            for i in range(len(listeHeaders1)):
                if i in dicoRowspans.keys():
                    listeHeaders2.append(listeHeaders1[i])
                    idecale -= 1
                else:
                    listeHeaders2.append(listeHeaders1[i].strip() + " " + cellules2[idecale].text.strip())
                idecale += 1
            return listeHeaders2
        except:
            logging.WARN("Ce header n'a pas pu être traité. Le traitement va se poursuivre.")
            return listeHeaders2

    def traiterLigne(self, dicoRowspans, ligne, largeurTableau, writer):
        try:
            cellulesLigneCourante = ligne.findChildren(recursive=False)
            retour = {}
            listeCellulesAEcrire = []
            compteurAnciensRowspansTraites = 0
            decalageColspans = 0
            for i in range(largeurTableau):
                if i + decalageColspans >= largeurTableau:
                    writer.writerow(listeCellulesAEcrire)
                    return dicoRowspans
                if i in dicoRowspans.keys():
                    rowspan = dicoRowspans[i]
                    listeCellulesAEcrire.append(rowspan.texte)
                    rowspan.rowspanResiduel = rowspan.rowspanResiduel - 1
                    if rowspan.rowspanResiduel > 0:
                        retour[i] = rowspan
                    compteurAnciensRowspansTraites += 1
                else:
                    if len(cellulesLigneCourante) > (i - compteurAnciensRowspansTraites):
                        cellule = cellulesLigneCourante[i - compteurAnciensRowspansTraites]
                        if not cellule.has_attr('colspan'):
                            if not cellule.has_attr('rowspan'):
                                listeCellulesAEcrire.append(cellule.text.strip())
                            else:
                                dicoRowspans[i + compteurAnciensRowspansTraites] = Rowspan(int(cellule.attrs.get('rowspan')), cellule.text.strip())
                                listeCellulesAEcrire.append(cellule.text.strip())
                        else:
                            if not cellule.has_attr('rowspan'):
                                for j in range(int(cellule.attrs.get('colspan'))):
                                    listeCellulesAEcrire.append(cellule.text.strip())
                                decalageColspans += int(cellule.attrs.get('colspan')) - 1
                            else:
                                for k in range(int(cellule.attrs.get('colspan'))):
                                    listeCellulesAEcrire.append(cellule.text.strip())
                                    dicoRowspans[i + k + decalageColspans] = Rowspan(int(cellule.attrs.get('rowspan')), cellule.text.strip())
                                decalageColspans += int(cellule.attrs.get('colspan')) - 1
                    else:
                        listeCellulesAEcrire.append("");
            writer.writerow(listeCellulesAEcrire)
            return dicoRowspans
        except:
            logging.WARN("Cette ligne n'a pas pu être traitée. Le traitement va se poursuivre.")

    def isHeader(self, ligne):
        try:
            retour = False
            if len(ligne.findChildren(recursive = False)) == len(ligne.find_all('th')):
                retour = True
            return retour
        except:
            pass

    def mkCSVFileName(self, url, n):
        try:
            return url.strip() + '-' + str(n) + '.csv'
        except:
            pass

    def getLargeurTotaleTableau(self, tableau, rangLigne):
        try:
            resultat = 0
            cellules = tableau.select('tr')[rangLigne].findChildren(recursive = False)
            for cellule in cellules:
                if cellule.has_attr('colspan'):
                    resultat += int(cellule.attrs.get('colspan'))
                else:
                    resultat += 1
            return resultat
        except:
            pass
