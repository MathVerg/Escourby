#!/usr/bin/python3.6
# -*-coding:utf-8 -*

#Escourby Booking Manager
#Logiciel de gestion de réservations pour camping
#Auteur : Mathéo Vergnolle
#Version 1.3
#Notes de version :
# - réorganisation de la fenêtre d'édition de réservations
# - les réservations ancrées ont maintenant une bordure bleue, et la bordure a été agrandie
# - ajout des numéros des jours en bas du planning

from tkinter import *
import tkinter.messagebox as mb
import tkinter.filedialog as fd
from datetime import date
import sqlite3

#propriétés du tableau

annee = date.today().year
h_case = 21
w_case = 28
l_forte = 4
l_faible = 1
nb_places = 35
rep_jours = ['Lu', 'Ma', 'Me', 'Je', 'Ve', 'Sa', 'Di']
prof_pool = 15
fond_dimanche = 'yellow'
fond_place_pair = '#DCDCDC'
w_cv = 1920
h_cv = 1400
coul_ancre = 'blue'

class EBMMain(Tk):
    def __init__(self):
        """ Constructeur """
        # Tk.__init__(self)
        super().__init__()

        #pour bien fermer la base de données avant de quitter
        self.protocol("WM_DELETE_WINDOW", self.quitter)

        self.title("Escourby Booking Manager")
        self.geometry('1920x1080')
        self.cadre_boutons = Frame(self, height=50, borderwidth=5, relief=GROOVE)
        self.cadre_boutons.pack(fill=X, side=TOP)

        self.bouton_fichier_db = Button(self.cadre_boutons, text="Choisir une base de données", command=self.choisir_db)
        self.bouton_fichier_db.pack(side=LEFT)
        self.bouton_nelle_resa = Button(self.cadre_boutons, text="Nouvelle réservation", state=DISABLED, command=self.nelle_resa)
        self.bouton_nelle_resa.pack(side=LEFT)
        self.bouton_infos_resa = Button(self.cadre_boutons, text="Infos réservation", state=DISABLED, command=self.infos_resa)
        self.bouton_infos_resa.pack(side=LEFT)
        self.bouton_suppr_resa = Button(self.cadre_boutons, text="Supprimer la réservation", state=DISABLED, command=self.suppr_resa)
        self.bouton_suppr_resa.pack(side=LEFT)
        self.bouton_enregistrer = Button(self.cadre_boutons, text="Enregistrer les modifications", state=DISABLED, command=self.enregistrer)
        self.bouton_enregistrer.pack(side=LEFT)
        #self.bouton_export = Button(self.cadre_boutons, text="Exporter le planning", state=DISABLED, command=self.export_planning)
        #self.bouton_export.pack(side=LEFT)
        self.bouton_quitter = Button(self.cadre_boutons, text="Quitter", command=self.quitter)
        self.bouton_quitter.pack(side=LEFT)

        self.cadre_cv = Frame(self)
        self.cadre_cv.pack(fill=BOTH, expand=True, padx=5, pady=5)

        self.cv = Canvas(self.cadre_cv, bg='white', scrollregion=(0, 0, w_cv, h_cv))
        self.cv.focus_set()
        self.cv.bind('<Button-1>', self.clic)
        self.cv.bind('<B1-Motion>', self.drag)
        self.cv.bind('<ButtonRelease-1>', self.release)
        self.cv.bind('<Up>', self.touche_haut)
        self.cv.bind('<Down>', self.touche_bas)

        self.scroll_y = Scrollbar(self.cadre_cv, orient="vertical", command=self.cv.yview)
        self.scroll_y.pack(side=RIGHT, fill=Y)
        self.scroll_x = Scrollbar(self.cadre_cv, orient="horizontal", command=self.cv.xview)
        self.scroll_x.pack(side=BOTTOM, fill=X)
        self.cv.pack(side = LEFT, fill=BOTH, expand=True, padx=5, pady=5)
        self.cv.configure(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)

        self.bind("<MouseWheel>", self.mouse_scroll)
        self.bind("<Button-4>", self.mouse_scroll)
        self.bind("<Button-5>", self.mouse_scroll)

        self.infobulle_texte = None
        self.infobulle_cadre = None

        self.max_resa = 0
        self.selection = 0
        self.secure = True


    def initialise_tableau(self):

        #coloriage des emplacements pairs
        for k in range(2, nb_places+1, 2):
           self.cv.create_rectangle(1 * w_case, (4 + k) * h_case, 66 * w_case, (5 + k) * h_case, fill=fond_place_pair)

        #jours
        for k in range(1, 32):
            jour = date(annee, 7, k).weekday()
            if jour == 6: #coloriage du dimanche
                self.cv.create_rectangle((k+1) * w_case, 3 * h_case, (k+2) * w_case, (6+nb_places) * h_case, fill=fond_dimanche)
                self.cv.create_rectangle((k+1) * w_case, (7+nb_places) * h_case, (k+2) * w_case, (7+nb_places+prof_pool) * h_case, fill=fond_dimanche)
            self.cv.create_text(int((1.5 + k) * w_case), int(3.5 * h_case), text=str(k))
            self.cv.create_text(int((1.5 + k) * w_case), int((5.5 + nb_places) * h_case), text=str(k))
            self.cv.create_text(int((1.5 + k) * w_case), int(4.5 * h_case), text=rep_jours[jour])
            jour = date(annee, 8, k).weekday()
            if jour == 6: #coloriage du dimanche
                self.cv.create_rectangle((k+33) * w_case, 3 * h_case, (k+34) * w_case, (6+nb_places) * h_case, fill=fond_dimanche)
                self.cv.create_rectangle((k+33) * w_case, (7+nb_places) * h_case, (k+34) * w_case, (7+nb_places+prof_pool) * h_case, fill=fond_dimanche)
            self.cv.create_text(int((33.5 + k) * w_case), int(3.5 * h_case), text=str(k))
            self.cv.create_text(int((33.5 + k) * w_case), int((5.5 + nb_places)* h_case), text=str(k))
            self.cv.create_text(int((33.5 + k) * w_case), int(4.5 * h_case), text=rep_jours[jour])

        #lignes maîtresses horizontales
        self.cv.create_line(2 * w_case, h_case, 65 * w_case, h_case, width=l_forte)
        self.cv.create_line(2 * w_case, 2 * h_case, 65 * w_case, 2 * h_case, width=l_forte)
        self.cv.create_line(2 * w_case, 3 * h_case, 33 * w_case, 3 * h_case, width=l_forte)
        self.cv.create_line(34 * w_case,3 * h_case, 65 * w_case, 3 * h_case, width=l_forte)
        self.cv.create_line(2 * w_case, 4 * h_case, 33 * w_case, 4 * h_case, width=l_faible)
        self.cv.create_line(34 * w_case,4 * h_case, 65 * w_case, 4 * h_case, width=l_faible)
        self.cv.create_line(w_case, 5 * h_case, 66 * w_case, 5 * h_case, width=l_forte)
        self.cv.create_line(w_case, (5 + nb_places) * h_case, 66 * w_case, (5 + nb_places) * h_case, width=l_forte)
        self.cv.create_line(2 * w_case, (6 + nb_places) * h_case, 65 * w_case, (6 + nb_places) * h_case, width=l_forte)
        self.cv.create_line(2 * w_case, (7 + nb_places) * h_case, 65 * w_case, (7 + nb_places) * h_case, width=l_forte)
        self.cv.create_line(2 * w_case, (7 + nb_places + prof_pool) * h_case, 65 * w_case, (7 + nb_places + prof_pool) * h_case, width=l_forte)

        #lignes maîtresses verticales
        self.cv.create_line(w_case, 5 * h_case, w_case, (5 + nb_places) * h_case, width=l_forte)
        self.cv.create_line(2 * w_case, h_case, 2 * w_case, (7 + nb_places + prof_pool) * h_case, width=l_forte)
        self.cv.create_line(33 * w_case, 2 * h_case, 33 * w_case, (6 + nb_places) * h_case, width=l_forte)
        self.cv.create_line(33 * w_case, (7 + nb_places) * h_case, 33 * w_case, (7 + nb_places + prof_pool) * h_case, width=l_forte)
        self.cv.create_line(34 * w_case, 2 * h_case, 34 * w_case, (6 + nb_places) * h_case, width=l_forte)
        self.cv.create_line(34 * w_case, (7 + nb_places) * h_case, 34 * w_case, (7 + nb_places + prof_pool) * h_case, width=l_forte)
        self.cv.create_line(65 * w_case, h_case, 65 * w_case, (7 + nb_places + prof_pool) * h_case, width=l_forte)
        self.cv.create_line(66 * w_case, 5 * h_case, 66 * w_case, (5 + nb_places) * h_case, width=l_forte)

        #cadrillage horizontal
        for k in range(1, nb_places):
            self.cv.create_line(w_case, (5 + k) * h_case, 65 * w_case, (5 + k) * h_case, width=l_faible)
        for k in range(1, prof_pool):
            self.cv.create_line(2 * w_case, (7 + nb_places + k) * h_case, 65 * w_case, (7 + nb_places + k) * h_case, width=l_faible)

        #cadrillage vertical
        for k in range(1, 63):
            self.cv.create_line((2 + k) * w_case, 3 * h_case, (2 + k) * w_case, (6 + nb_places) * h_case, width=l_faible)
            self.cv.create_line((2 + k) * w_case, (7 + nb_places) * h_case, (2 + k) * w_case, (7 + nb_places + prof_pool) * h_case, width=l_faible)

        #titres et mois
        self.cv.create_text(int(33.5 * w_case), int(1.5 * h_case), text="P l a n n i n g  " + str(annee) + "  a u  " + str(date.today().day)+" / " + str(date.today().month) + " / " + str(date.today().year))
        self.cv.create_text(int(17.5 * w_case), int(2.5 * h_case), text="J u i l l e t")
        self.cv.create_text(int(49.5 * w_case), int(2.5 * h_case), text="A o u t")
        self.cv.create_text(int(33.5 * w_case), int((6.5 + nb_places) * h_case), text="P i s c i n e")

        #numéros des emplacements
        for k in range(1, nb_places + 1):
            self.cv.create_text(int(1.5 * w_case), int((4.5 + k) * h_case), text=str(k))
            self.cv.create_text(int(33.5 * w_case), int((4.5 + k) * h_case), text=str(k))
            self.cv.create_text(int(65.5 * w_case), int((4.5 + k)  *  h_case), text=str(k))


    def choisir_db(self):
        try:
            self.db.close()
            if self.secure :
                f = open(self.chemin_verrou, 'w')
                f.write("0")
                f.close()
        except AttributeError:
            pass
        except sqlite3.ProgrammingError :
            pass
        filename = fd.askopenfilename(title="Ouvrir une base de données")
        if filename : #vérifier que ce n'est pas ()
            chemin_liste = filename.split(sep='/')
            chemin_liste[-1] = 'verrou.txt'
            self.chemin_verrou = '/'.join(chemin_liste)
            flag = True
        else :
            flag = False
        if flag :
            try :
                f = open(self.chemin_verrou,'r')
                verrou = int(f.readline())
                f.close()
                if verrou :
                    flag = mb.askyesno("Attention", "Un autre utilisateur pourrait être en train de modifier cette base de données. Voulez-vous tout de même continuer ?")
            except FileNotFoundError :
                flag = mb.askyesno("Attention", "Aucun fichier de verrou n'a été trouvé : nous ne pouvons pas garantir que vous êtes en ce moment le/la seule.e à modifier cette base de données. Voulez-vous tout de même continuer ?")
                if flag :
                    self.secure = False
        if flag :
            try :
                self.db = sqlite3.connect(filename)
            except TypeError:
                pass
            else :
                self.cv.delete(ALL)
                self.initialise_tableau()
                self.cur = self.db.cursor()
                try :
                    self.cur.execute("""SELECT MAX(NumeroResa) FROM Reservations""")
                    self.max_resa = self.cur.fetchone()[0]
                    if type(self.max_resa) != int :
                        self.max_resa = 0
                    self.cur.execute("""SELECT NumeroResa, NomAffiche, Arrivee, Depart, Frigo, Ombre, Emplacement, Ancre from Reservations""")
                except sqlite3.DatabaseError :
                    self.db.close()
                    mb.showerror("Erreur", "Le fichier choisi n'est peut-être pas une base de données, ou n'a pas le bon format")
                except sqlite3.OperationalError :
                    self.db.close()
                    mb.showerror("Erreur", "La base de donnée n'a pas le bon format (nom des tables et des attributs)")
                else :
                    with open(self.chemin_verrou, 'w') as f:
                        f.write('1')
                    self.secure = True
                    self.bouton_nelle_resa['state'] = NORMAL
                    self.liste_rectangles = [None for k in range(self.max_resa + 1)]
                    self.liste_noms = [None for k in range(self.max_resa + 1)]
                    self.liste_places = [None for k in range(self.max_resa + 1)]
                    for row in self.cur :
                        self.placer_resa(row)
                    #self.bouton_export['state'] = NORMAL
            self.cv.focus_set()

    def placer_resa(self, row):
        (num_resa, nomAffiche, arrivee, depart, frigo, ombre, emplacement, ancre) = row
        mois_arrivee = int(arrivee[1])
        jour_arrivee = int(arrivee[3:5])
        mois_depart = int(depart[1])
        jour_depart = int(depart[3:5])
        errorflag = False
        if frigo :
            if ombre :
                texte_affiche = "[FO]   " + nomAffiche
            else :
                texte_affiche = "[F]   " + nomAffiche
            couleur = "#32FF64"
        elif ombre :
            texte_affiche = "[O]   " + nomAffiche
            couleur = "#96FF96"
        else :
            texte_affiche = nomAffiche
            couleur = "#96FF96"
        if emplacement > 0 :
            y0 = (4 + emplacement) * h_case + 2
        else :
            y0 = (6 + nb_places + abs(emplacement)) * h_case + 2
        y1 = y0 + h_case - 3
        if mois_arrivee == 7:
            x0 = int((1.5 + jour_arrivee) * w_case)
        elif mois_arrivee == 6 :
            x0 = 2 * w_case
        else :
            x0 = int((33.5 + jour_arrivee) * w_case)
        if mois_depart == 7:
            x1 = int((1.5 + jour_depart) * w_case)
        elif mois_depart == 9:
            x1 = 65 * w_case
        else :
            x1 = int((33.5 + jour_depart) * w_case)
        if ancre :
            bordure = coul_ancre
        else :
            bordure = 'black'
        self.liste_rectangles[num_resa] = self.cv.create_rectangle(x0, y0, x1, y1, fill=couleur, activewidth=3)
        self.cv.itemconfig(self.liste_rectangles[num_resa], outline = bordure, width=2)
        self.liste_noms[num_resa] = self.cv.create_text((x0 + x1)//2, y0 - 1 + int(h_case/2), text=texte_affiche)
        self.liste_places[num_resa] = emplacement

    def nelle_resa(self):
        param = (self.max_resa + 1, "", "", "07/01", "07/02", 0, 0, 0, 2, 0, "", 0, 0)
        edition_resa = EditionResa(self, param)
        self.wait_window(edition_resa)
        valide, valeurs = edition_resa.valide, edition_resa.valeurs
        if valide :
            self.liste_rectangles.append(None)
            self.liste_noms.append(None)
            self.liste_places.append(None)
            self.max_resa += 1
            self.placer_resa((valeurs[0], valeurs[2], valeurs[3], valeurs[4], valeurs[6], valeurs[7], valeurs[-2], valeurs[-1]))
            self.selectionne(self.max_resa)
            self.cur.execute('''INSERT INTO Reservations (NumeroResa, Nom, NomAffiche, Arrivee, Depart, Couchage, Frigo, Ombre, Adultes, Enfants, Divers, Emplacement, Ancre) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', valeurs)
            self.apres_modif()
        self.cv.focus_set()

    def infos_resa(self):
        self.cur.execute('''SELECT * FROM Reservations WHERE NumeroResa = ?''', (self.selection,))
        param = self.cur.fetchone()
        edition_resa = EditionResa(self, param)
        self.wait_window(edition_resa)
        valide, valeurs = edition_resa.valide, edition_resa.valeurs
        if valide :
            self.cv.delete(self.liste_rectangles[self.selection])
            self.liste_rectangles[self.selection] = None
            self.cv.delete(self.liste_noms[self.selection])
            self.liste_noms[self.selection] = None
            self.placer_resa((valeurs[0], valeurs[2], valeurs[3], valeurs[4], valeurs[6], valeurs[7], valeurs[-2], valeurs[-1]))
            self.cur.execute('''UPDATE Reservations SET Nom=?, NomAffiche=?, Arrivee=?, Depart=?, Couchage=?, Frigo=?, Ombre=?, Adultes=?, Enfants=?, Divers=?, Emplacement=?, Ancre=? WHERE NumeroResa = ?''', valeurs[1:] + valeurs[:1])
            self.apres_modif()
            self.selectionne(self.selection)
        self.cv.focus_set()

    def export_planning(self):
        filepath = fd.asksaveasfilename(title = "Enregistrer l'image")
        self.selectionne(0)
        self.cv.postscript(file=filepath + ".ps", colormode='color')
        self.cv.focus_set()

    def suppr_resa(self):
        if mb.askokcancel(title="Confirmation", message="Voulez-vous vraiment supprimer cette réservation ?"):
            self.cv.delete(self.liste_rectangles[self.selection])
            self.cv.delete(self.liste_noms[self.selection])
            self.cur.execute("""DELETE FROM Reservations WHERE NumeroResa = ?""", (self.selection,))
            self.bouton_enregistrer['state'] = NORMAL
            #self.bouton_export['state'] = DISABLED
            self.bouton_fichier_db['state'] = DISABLED
            if self.selection == self.max_resa:
                self.liste_noms.pop()
                self.liste_rectangles.pop()
                self.liste_places.pop()
                self.max_resa -= 1
            else :
                self.liste_noms[self.selection] = None
                self.liste_rectangles[self.selection] = None
                self.liste_places[self.selection] = None
            self.selectionne(0)
            self.cv.focus_set()

    def enregistrer(self):
        self.db.commit()
        self.bouton_enregistrer['state'] = DISABLED
        #self.bouton_export['state'] = NORMAL
        self.bouton_fichier_db['state'] = NORMAL
        self.cv.focus_set()

    def quitter(self):
        quit_flag = True
        try :
            self.cur.execute("""SELECT COUNT(*) FROM Reservations WHERE Emplacement < 0""")
            in_pool = self.cur.fetchone()[0]
            if in_pool > 0 :
                if not mb.askokcancel(title="Attention", message="Il reste {} réservation(s) dans la piscine, voulez-vous tout de même quitter ?".format(in_pool)) :
                    quit_flag = False
        except AttributeError:
            pass
        except sqlite3.ProgrammingError :
            pass
        if quit_flag and self.bouton_enregistrer['state'] == NORMAL :
            action = mb.askyesnocancel(title="Quitter", message="Il y a des modifications non-enregistrées, voulez-vous les enregistrer avant de quitter ?")
            if action == None :
               quit_flag = False
            else :
                if action :
                    self.enregistrer()
        if quit_flag :
            try:
                self.db.close()
                if self.secure :
                    f = open(self.chemin_verrou, 'w')
                    f.write("0")
                    f.close()
            except AttributeError:
                pass
            self.destroy()

    def apres_modif(self):
        '''actions effectuées après chaque modification'''
        self.bouton_enregistrer['state'] = NORMAL
        #self.bouton_export['state'] = DISABLED
        self.bouton_fichier_db['state'] = DISABLED

    def selectionne(self, i):
        if 0 < self.selection <= self.max_resa :
            self.cur.execute('''SELECT Ancre FROM Reservations WHERE NumeroResa = ?''', (self.selection,))
            row = list(self.cur.fetchone())
            if row[0] :
                bordure = coul_ancre
            else :
                bordure = 'black'
            self.cv.itemconfig(self.liste_rectangles[self.selection], outline = bordure)
        self.selection = i
        if i != 0 :
            self.bouton_infos_resa['state'] = NORMAL
            self.bouton_suppr_resa['state'] = NORMAL
            self.cv.itemconfig(self.liste_rectangles[i], outline='red')
            self.cv.focus(self.liste_rectangles[i])
        else :
            self.cv.delete(self.infobulle_cadre)
            self.cv.delete(self.infobulle_texte)
            self.bouton_infos_resa['state'] = DISABLED
            self.bouton_suppr_resa['state'] = DISABLED
            self.cv.focus()

    def check_conflits(self, num, arrivee, depart, place):
        self.cur.execute('''SELECT COUNT(*) FROM Reservations WHERE Emplacement=? AND (Depart > ? OR Arrivee > ? ) AND (Depart < ? OR Arrivee < ?) AND NumeroResa <> ?''', (place, arrivee, arrivee, depart, depart, num))
        conflits = self.cur.fetchone()[0]
        return conflits

    def clic(self, event):
        ''' ce qui se passe lorsqu'on clique quelque part sur le canevas '''
        X, Y = event.x + self.scroll_x.get()[0] * w_cv, event.y + self.scroll_y.get()[0] * h_cv #on compense le scroll
        i = 0
        flag = True
        self.cv.delete(self.infobulle_texte)
        self.cv.delete(self.infobulle_cadre)
        while i < self.max_resa and flag:
            i +=1
            if self.liste_rectangles[i] is not None :
                (x0, y0, x1, y1) = self.cv.coords(self.liste_rectangles[i])
                if x0 <= X <= x1 and y0 <= Y <= y1 :
                    flag = False
                    self.selectionne(i)
        if flag :
            self.selectionne(0)
        if self.selection != 0 :
            self.cur.execute('''SELECT Nom, Couchage, Adultes, Enfants, Divers FROM Reservations WHERE NumeroResa=?''', (self.selection,))
            row = self.cur.fetchone()
            (nom, couchage, adultes, enfants, divers) = row
            texte_info = nom
            if couchage == 2 :
                texte_info += "\nCamping-car"
            elif couchage == 1 :
                texte_info += "\nCaravane"
            texte_info += "\n{}A {}E".format(adultes, enfants)
            if divers : #la chaîne n'est pas vide
                texte_info += "\n" + divers
            offset_bas = (2 + int(bool(couchage)) + int(bool(divers)))*16 + 3
            self.infobulle_cadre = self.cv.create_rectangle(X-3, Y-3, X + max(90, len(nom) * 9, len(divers) * 8), Y + offset_bas, fill='yellow')
            self.infobulle_texte = self.cv.create_text(X, Y, text=texte_info, anchor=NW)

    def drag(self, event):
        Y = event.y + self.scroll_y.get()[0] * h_cv #on compense le scroll
        flag = True
        if self.selection == 0:
            flag = False
        if Y <= 5 * h_case or (5 + nb_places) * h_case <= Y <= (7 + nb_places) * h_case or (7 + nb_places + prof_pool) * h_case <= Y:
            flag = False
        if flag :
            if Y < (5 + nb_places) * h_case :
                new_place = Y//h_case - 4
            else :
                new_place = - (Y//h_case - 6 - nb_places)
        if flag :
            self.cur.execute('''SELECT NumeroResa, NomAffiche, Arrivee, Depart, Frigo, Ombre, Emplacement, Ancre FROM Reservations WHERE NumeroResa = ?''', (self.selection,))
            row = list(self.cur.fetchone())
            if row[-1]:
                flag = False
            row[-2] = new_place
            if self.check_conflits(row[0], row[2], row[3], row[-2]) > 0 :
                flag = False
        if flag :
            self.cv.delete(self.liste_rectangles[self.selection])
            self.cv.delete(self.liste_noms[self.selection])
            self.placer_resa(row)
            self.cv.tag_raise(self.infobulle_cadre)
            self.cv.tag_raise(self.infobulle_texte)
            self.selectionne(self.selection)

    def release(self, event):
        if self.selection != 0 :
            self.cur.execute('''SELECT Emplacement FROM Reservations WHERE NumeroResa = ?''', (self.selection,))
            if self.cur.fetchone()[0] != self.liste_places[self.selection]:
                self.cur.execute('''UPDATE Reservations SET Emplacement = ? WHERE NumeroResa = ?''', (self.liste_places[self.selection], self.selection))
                self.apres_modif()

    def touche_dir(self, dir):
        '''dir = +- 1 indique la direction de déplacement'''
        if self.selection == 0 :
            pass
        else :
            self.cur.execute('''SELECT NumeroResa, NomAffiche, Arrivee, Depart, Frigo, Ombre, Emplacement, Ancre FROM Reservations WHERE NumeroResa = ?''', (self.selection,))
            row = list(self.cur.fetchone())
            if not row[-1]:
                place = row[-2]
                if place == 1 and dir == -1 :
                    new_place = - (prof_pool)
                elif place == nb_places and dir == + 1:
                    new_place = -1
                elif place == -1 and dir == -1 :
                    new_place = nb_places
                elif place == - (prof_pool) and dir == +1 :
                    new_place = 1
                elif place < 0 :
                    new_place = place - dir
                else :
                    new_place = place + dir
                row[-2] = new_place
                while self.check_conflits(row[0], row[2], row[3], row[-2]) > 0:
                    if new_place == 1 and dir == -1 :
                        new_place = - (prof_pool)
                    elif new_place == nb_places and dir == + 1:
                        new_place = -1
                    elif new_place == -1 and dir == -1 :
                        new_place = nb_places
                    elif new_place == - (prof_pool) and dir == +1 :
                        new_place = 1
                    elif new_place < 0 :
                        new_place -= dir
                    else :
                        new_place += dir
                    row[-2] = new_place
                self.cv.delete(self.liste_rectangles[self.selection])
                self.cv.delete(self.liste_noms[self.selection])
                self.placer_resa(row)
                self.cur.execute('''UPDATE Reservations SET Emplacement = ? WHERE NumeroResa = ?''', (new_place, row[0]))
                self.apres_modif()
                self.selectionne(self.selection)

    def touche_haut(self, event):
        self.touche_dir(-1)

    def touche_bas(self, event):
        self.touche_dir(1)

    def mouse_scroll(self, event):
        if event.num == 5 or event.delta < 0:
            dir = 1
        else :
            dir = -1
        self.cv.yview_scroll(dir, "units")

class EditionResa(Toplevel):
    '''fenetre d'édition des réservations'''
    def __init__(self, parent, row):
        '''row (tuple), contient les valeurs par défaut on renverra une liste à la fin'''

        Toplevel.__init__(self, parent)

        self.parent = parent
        self.transient(self.parent)
        self.grab_set()

        #pour révoquer les modifs avant de quitter
        self.protocol("WM_DELETE_WINDOW", self.annuler)

        self.title("Édition de réservation")

        self.valeurs_origine = list(row)
        self.valide = True

        self.grand_cadre = Frame(self, padx=5, pady=5, relief=GROOVE)
        self.grand_cadre.pack()

        self.panneau_gauche = Frame(self.grand_cadre, padx=5, pady=5, relief=SUNKEN)
        self.panneau_gauche.pack(side=LEFT)

        self.cadre_nom = LabelFrame(self.panneau_gauche, text="Nom", padx=5, pady=5, relief=GROOVE)
        self.cadre_nom.pack()
        self.nom = StringVar(self, value=row[1])
        self.champ_nom = Entry(self.cadre_nom, textvariable=self.nom, width=60)
        self.champ_nom.pack()

        self.cadre_nom_affiche = LabelFrame(self.panneau_gauche, text="Nom à afficher", padx=5, pady=5, relief=GROOVE)
        self.cadre_nom_affiche.pack()
        self.nom_affiche = StringVar(self, value=row[2])
        self.champ_nom_affiche = Entry(self.cadre_nom_affiche, textvariable=self.nom_affiche, width=60)
        self.champ_nom_affiche.pack()

        self.cadre_arrivee = LabelFrame(self.panneau_gauche, text="Arrivée", padx=5, pady=5, relief=GROOVE)
        self.cadre_arrivee.pack()
        arrivee = row[3]
        self.jour_arrivee = IntVar(self, value=int(arrivee[3:5]))
        self.mois_arrivee = IntVar(self, value=int(arrivee[0:2]))
        self.choix_jour_a = Scale(self.cadre_arrivee,from_=1,to=31,resolution=1,orient=HORIZONTAL, length=300, width=20, label="Jour", tickinterval=5, variable=self.jour_arrivee)
        self.choix_jour_a.pack(side=LEFT)
        self.choix_mois_a = Scale(self.cadre_arrivee,from_=6,to=8,resolution=1,orient=HORIZONTAL, length=50, width=20, label="Mois", tickinterval=2, variable=self.mois_arrivee)
        self.choix_mois_a.pack(side=LEFT)

        self.cadre_depart = LabelFrame(self.panneau_gauche, text="Départ", padx=5, pady=5, relief=GROOVE)
        self.cadre_depart.pack()
        depart = row[4]
        self.jour_depart = IntVar(self, value=int(depart[3:5]))
        self.mois_depart = IntVar(self, value=int(depart[0:2]))
        self.choix_jour_d = Scale(self.cadre_depart,from_=1,to=31,resolution=1,orient=HORIZONTAL, length=300, width=20, label="Jour", tickinterval=5, variable=self.jour_depart)
        self.choix_jour_d.pack(side=LEFT)
        self.choix_mois_d = Scale(self.cadre_depart,from_=7,to=9,resolution=1,orient=HORIZONTAL, length=50, width=20, label="Mois", tickinterval=2, variable=self.mois_depart)
        self.choix_mois_d.pack(side=LEFT)

        self.cadre_divers = LabelFrame(self.panneau_gauche, text="Divers", padx=5, pady=5, relief=GROOVE)
        self.cadre_divers.pack()
        self.divers = StringVar(self, value=row[10])
        self.champ_divers = Entry(self.cadre_divers, textvariable=self.divers, width=60)
        self.champ_divers.pack()

        self.panneau_droite = Frame(self.grand_cadre, padx=5, pady=5, relief=SUNKEN)
        self.panneau_droite.pack(side=LEFT)

        self.cadre_couchage = LabelFrame(self.panneau_droite, text="Couchage", padx=5, pady=5, relief=GROOVE)
        self.cadre_couchage.pack()
        self.couchage = IntVar(self, value=row[5])
        self.choix_tentes = Radiobutton(self.cadre_couchage, text="Tentes seulement", variable=self.couchage, value=0)
        self.choix_tentes.pack(side=LEFT)
        self.choix_caravane = Radiobutton(self.cadre_couchage, text="Caravane", variable=self.couchage, value=1)
        self.choix_caravane.pack(side=LEFT)
        self.choix_campingcar = Radiobutton(self.cadre_couchage, text="Camping-car", variable=self.couchage, value=2)
        self.choix_campingcar.pack(side=LEFT)

        self.cadre_options = LabelFrame(self.panneau_droite, text="Options", padx=5, pady=5, relief=GROOVE)
        self.cadre_options.pack()
        self.frigo = IntVar(self, value=row[6])
        self.case_frigo = Checkbutton(self.cadre_options, text="Frigo", variable=self.frigo)
        self.case_frigo.pack(side=LEFT)
        self.ombre = IntVar(self, value=row[7])
        self.case_ombre = Checkbutton(self.cadre_options, text="Ombre", variable=self.ombre)
        self.case_ombre.pack(side=LEFT)

        self.cadre_famille = LabelFrame(self.panneau_droite, text="Composition de la famille", padx=5, pady=5, relief=GROOVE)
        self.cadre_famille.pack()
        self.adultes = IntVar(self, value=row[8])
        self.choix_adultes = Scale(self.cadre_famille, from_=0, to=9, resolution=1, orient=HORIZONTAL, length=350, width=20, label="Nombre d'adultes :", tickinterval=1, variable=self.adultes)
        self.choix_adultes.pack()

        self.enfants = IntVar(self, value=row[9])
        self.choix_enfants = Scale(self.cadre_famille, from_=0, to=9, resolution=1, orient=HORIZONTAL, length=350, width=20, label="Nombre d'enfants :", tickinterval=1, variable=self.enfants)
        self.choix_enfants.pack()

        self.cadre_emplacement = LabelFrame(self.panneau_droite, text="Emplacement", padx=5, pady=5, relief=GROOVE)
        self.cadre_emplacement.pack()
        self.emplacement = IntVar(self, value=row[11])
        self.choix_emplacement = Scale(self.cadre_emplacement,from_=0,to=nb_places,resolution=1,orient=HORIZONTAL, length=300, width=20, label="Numéro (0 = Piscine)", tickinterval=5, variable=self.emplacement)
        self.choix_emplacement.pack(side=LEFT)
        self.ancre = IntVar(self, value=row[12])
        self.case_ancre = Checkbutton(self.cadre_emplacement, text="Ancré à l'emplacment", variable=self.ancre)
        self.case_ancre.pack()

        self.cadre_vc = Frame(self, borderwidth=5, relief=GROOVE)
        self.cadre_vc.pack()
        self.bouton_valider = Button(self.cadre_vc, text="Valider", command=self.valider)
        self.bouton_valider.pack(side=LEFT)
        self.bouton_annuler = Button(self.cadre_vc, text="Annuler", command=self.annuler)
        self.bouton_annuler.pack(side=LEFT)

    def annuler(self):
        self.adultes.get()
        self.valeurs = self.valeurs_origine
        self.valide = False
        self.parent.focus_set()
        self.destroy()

    def valider(self):
        arrivee = "0{0}/{1:02}".format(self.mois_arrivee.get(), self.jour_arrivee.get())
        depart = "0{0}/{1:02}".format(self.mois_depart.get(), self.jour_depart.get())
        place = self.emplacement.get()
        ancre = self.ancre.get()
        if place == 0 :
            place = -1
            ancre = 0
        else :
            conflits = self.parent.check_conflits(self.valeurs_origine[0], arrivee, depart, place)
            if conflits != 0 :
                place = -1
                ancre = 0
                mb.showwarning(title="Attention", message="Conflit avec {} autre(s) réservation(s) : la reservation créée est mise dans la piscine.\nAttention, elle pourrait se chevaucher avec une réservation qui serait déjà dans le premier emplacement de la piscine.".format(conflits))
        nom = self.champ_nom.get().upper()
        nom_affiche = self.champ_nom_affiche.get().upper()
        if not nom :
            nom = nom_affiche
        elif not nom_affiche :
            nom_affiche = nom
        if (self.mois_depart.get(), self.jour_depart.get()) <= (self.mois_arrivee.get(), self.jour_arrivee.get()) :
            mb.showerror(title="Erreur", message="Départ antérieur à l'arrivée")
        else :
            self.valeurs = [self.valeurs_origine[0], nom, nom_affiche, arrivee, depart, self.couchage.get(), self.frigo.get(), self.ombre.get(), self.adultes.get(), self.enfants.get(), self.champ_divers.get(), place, ancre]
            self.valide = True
            self.parent.focus_set()
            self.destroy()



if __name__ == "__main__":
    princ = EBMMain()
    princ.mainloop()
