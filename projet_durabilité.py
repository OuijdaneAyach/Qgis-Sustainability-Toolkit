# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ProjetDurabilite
                                 A QGIS plugin
 Ce plugin teste la durabilité
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2025-02-07
        git sha              : $Format:%H$
        email                : ayachouijdanew@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMessageBox, QDialog, QVBoxLayout, QLabel, QPushButton
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QScrollArea
)
from .resources import *

from .resources import *
from .projet_durabilité_dialog import ProjetDurabiliteDialog

class SolutionsDialog(QDialog):
    """
    QDialog pour afficher les solutions.
    """

    def __init__(self, html_text, parent=None):
        super().__init__(parent)

        # 1) Configuration de la fenêtre (title, flags, taille)
        self.setWindowTitle("Solutions de durabilité")
        flags = self.windowFlags()
        flags = flags | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint | Qt.Window
        self.setWindowFlags(flags)
        self.resize(600, 400)
        #style css
        custom_style = """
        QDialog {
            background-color: #f8f9fa; 
            border: 1px solid #ced6e0;
            border-radius: 8px;
        }
        QLabel {
            font-family: "Segoe UI", "Roboto", Arial, sans-serif;
            font-size: 14px;
            color: #2c3e50;
        }
        QPushButton {
            background-color: #3498db;
            color: #ffffff;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 600;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
        QPushButton:pressed {
            background-color: #1f5b77;
            padding-left: 10px; 
            padding-top: 6px;
        }
        QScrollArea {
            border: none;
            background: transparent;
        }
        """
        self.setStyleSheet(custom_style)

        layout = QVBoxLayout(self)
        label_solutions = QLabel()
        label_solutions.setTextFormat(Qt.RichText)  # Interpréter HTML
        label_solutions.setWordWrap(True)
        label_solutions.setText(html_text)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)  # le widget suit la taille
        scroll_area.setWidget(label_solutions)
        layout.addWidget(scroll_area)
        btn_close = QPushButton("Fermer")
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close)

        self.setLayout(layout)


# -------------------------------------------------------------------------
# Fonctions
# -------------------------------------------------------------------------
def read_float(line_edit):
    """
    Convertir le contenu du QLineEdit en float.
    """
    text_value = line_edit.text().strip()
    if not text_value:
        return 0.0
    try:
        return float(text_value)
    except ValueError:
        return 0.0

def valeur(valeur_b, normes, facteur_im):
    """
    Calcule la valeur normalisée et pondérée :
    (valeur_b / normes) * facteur_im, en évitant la division par zéro.
    """
    try:
        return (valeur_b / normes) * facteur_im if normes != 0 else 0.0
    except ZeroDivisionError:
        return 0.0

def decision(valeur_moy):
    """
    Decision 'Durable' ou bien 'Non durable'.
    """
    if valeur_moy >= 5:
        return "Durable"
    else:
        return "Non durable"


class ProjetDurabilite:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """
        iface: L'interface QGIS (QgsInterface).
        """
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)

        # Gestion de la traduction
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'ProjetDurabilite_{}.qm'.format(locale)
        )

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr(u'&PluginDurabilite')
        self.first_start = True

        # Variables pour stocker les décisions
        self.dec_eco_T1 = None
        self.dec_env_T1 = None
        self.dec_soc_T1 = None

        self.dec_eco_T2 = None
        self.dec_env_T2 = None
        self.dec_soc_T2 = None

        self.dec_eco_T3 = None
        self.dec_env_T3 = None
        self.dec_soc_T3 = None

    def tr(self, message):
        return QCoreApplication.translate('ProjetDurabilite', message)

    def add_action(self,
                   icon_path,
                   text,
                   callback,
                   enabled_flag=True,
                   add_to_menu=True,
                   add_to_toolbar=True,
                   status_tip=None,
                   whats_this=None,
                   parent=None):

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)
        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.iface.addToolBarIcon(action)
        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)
        return action

    def initGui(self):
        icon_path = ':/plugins/projet_durabilité/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Plugin Durabilité'),
            callback=self.run,
            parent=self.iface.mainWindow()
        )
        self.first_start = True

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(self.tr(u'&PluginDurabilite'), action)
            self.iface.removeToolBarIcon(action)

    # --------------------------------------------------------------------------
    # Fonctions de calcul : Économie
    # --------------------------------------------------------------------------
    def Economie_T1(self):
        try:
            val_b = read_float(self.dlg.valeur_fc)
            norme = read_float(self.dlg.norme_inf)
            fact_im = read_float(self.dlg.fact_inf)
            infra = valeur(val_b, norme, fact_im)

            val_b2 = read_float(self.dlg.val_br_ca)
            norme2 = read_float(self.dlg.norme_ca)
            fact_im2 = read_float(self.dlg.fac_imp_ca)
            chiffre_affaire = valeur(val_b2, norme2, fact_im2)

            val_b3 = read_float(self.dlg.nt_vb)
            norme3 = read_float(self.dlg.norme_nt)
            fact_im3 = read_float(self.dlg.nt_fi)
            nb_touriste = valeur(val_b3, norme3, fact_im3)

            val_b4 = read_float(self.dlg.ata_vb)
            norme4 = read_float(self.dlg.pta_vb)
            fact_im4 = read_float(self.dlg.pta_fi)
            produits_terroirs = valeur(val_b4, norme4, fact_im4)

            valeur_moy = (infra + chiffre_affaire + nb_touriste + produits_terroirs) / 4.0
            return valeur_moy
        except Exception as e:
            QMessageBox.critical(self.dlg, "Erreur", f"Erreur dans Economie_T1 : {str(e)}")
            return 0

    def Economie_T2(self):
        try:
            val_b = read_float(self.dlg.vb_inf2)
            norme = read_float(self.dlg.norme_inf_2)
            fact_im = read_float(self.dlg.inf_fi2)
            infra = valeur(val_b, norme, fact_im)

            val_b2 = read_float(self.dlg.ca_vb2)
            norme2 = read_float(self.dlg.norme_ca2)
            fact_im2 = read_float(self.dlg.ca_fi2)
            chiffre_affaire = valeur(val_b2, norme2, fact_im2)

            val_b3 = read_float(self.dlg.valeur_b_Inf_T3_15)
            norme3 = read_float(self.dlg.valeur_b_Inf_T3_19)
            fact_im3 = read_float(self.dlg.valeur_b_Inf_T3_14)
            nb_touriste = valeur(val_b3, norme3, fact_im3)

            val_b4 = read_float(self.dlg.valeur_b_Inf_T3_23)
            norme4 = read_float(self.dlg.valeur_b_Inf_T3_20)
            fact_im4 = read_float(self.dlg.valeur_b_Inf_T3_22)
            produits_terroirs = valeur(val_b4, norme4, fact_im4)

            valeur_moy = (infra + chiffre_affaire + nb_touriste + produits_terroirs) / 4.0
            return valeur_moy
        except Exception as e:
            QMessageBox.critical(self.dlg, "Erreur", f"Erreur dans Economie_T2 : {str(e)}")
            return 0

    def Economie_T3(self):
        try:
            val_b = read_float(self.dlg.valeur_b_Inf_T3_36)
            norme = read_float(self.dlg.valeur_b_Inf_T3_30)
            fact_im = read_float(self.dlg.valeur_b_Inf_T3_29)
            infra = valeur(val_b, norme, fact_im)

            val_b2 = read_float(self.dlg.valeur_b_Inf_T3_33)
            norme2 = read_float(self.dlg.valeur_b_Inf_T3_25)
            fact_im2 = read_float(self.dlg.valeur_b_Inf_T3_28)
            chiffre_affaire = valeur(val_b2, norme2, fact_im2)

            val_b3 = read_float(self.dlg.valeur_b_Inf_T3_27)
            norme3 = read_float(self.dlg.valeur_b_Inf_T3_31)
            fact_im3 = read_float(self.dlg.valeur_b_Inf_T3_26)
            nb_touriste = valeur(val_b3, norme3, fact_im3)

            val_b4 = read_float(self.dlg.valeur_b_Inf_T3_35)
            norme4 = read_float(self.dlg.valeur_b_Inf_T3_32)
            fact_im4 = read_float(self.dlg.valeur_b_Inf_T3_34)
            produits_terroirs = valeur(val_b4, norme4, fact_im4)

            valeur_moy = (infra + chiffre_affaire + nb_touriste + produits_terroirs) / 4.0
            return valeur_moy
        except Exception as e:
            QMessageBox.critical(self.dlg, "Erreur", f"Erreur dans Economie_T3 : {str(e)}")
            return 0

    # --------------------------------------------------------------------------
    # Fonctions de calcul : Environnement
    # --------------------------------------------------------------------------
    def Environnement_T1(self):
        try:
            val_b = read_float(self.dlg.valeur_b_Inf_T3_37)
            norme = read_float(self.dlg.valeur_b_Inf_T3_41)
            fact_im = read_float(self.dlg.valeur_b_Inf_T3_42)
            biodiversite = valeur(val_b, norme, fact_im)

            val_b2 = read_float(self.dlg.valeur_b_Inf_T3_38)
            norme2 = read_float(self.dlg.valeur_b_Inf_T3_43)
            fact_im2 = read_float(self.dlg.valeur_b_Inf_T3_44)
            ressources_nat = valeur(val_b2, norme2, fact_im2)

            val_b3 = read_float(self.dlg.valeur_b_Inf_T3_39)
            norme3 = read_float(self.dlg.valeur_b_Inf_T3_45)
            fact_im3 = read_float(self.dlg.valeur_b_Inf_T3_46)
            paysage = valeur(val_b3, norme3, fact_im3)

            val_b4 = read_float(self.dlg.valeur_b_Inf_T3_40)
            norme4 = read_float(self.dlg.valeur_b_Inf_T3_47)
            fact_im4 = read_float(self.dlg.valeur_b_Inf_T3_48)
            climat = valeur(val_b4, norme4, fact_im4)

            return (biodiversite + ressources_nat + paysage + climat) / 4.0
        except Exception as e:
            QMessageBox.critical(self.dlg, "Erreur", f"Erreur dans Environnement_T1 : {str(e)}")
            return 0

    def Environnement_T2(self):
        try:
            val_b = read_float(self.dlg.valeur_b_Inf_T3_60)
            norme = read_float(self.dlg.valeur_b_Inf_T3_54)
            fact_im = read_float(self.dlg.valeur_b_Inf_T3_53)
            biodiversite = valeur(val_b, norme, fact_im)

            val_b2 = read_float(self.dlg.valeur_b_Inf_T3_57)
            norme2 = read_float(self.dlg.valeur_b_Inf_T3_49)
            fact_im2 = read_float(self.dlg.valeur_b_Inf_T3_52)
            ressources_nat = valeur(val_b2, norme2, fact_im2)

            val_b3 = read_float(self.dlg.valeur_b_Inf_T3_51)
            norme3 = read_float(self.dlg.valeur_b_Inf_T3_55)
            fact_im3 = read_float(self.dlg.valeur_b_Inf_T3_50)
            paysage = valeur(val_b3, norme3, fact_im3)

            val_b4 = read_float(self.dlg.valeur_b_Inf_T3_59)
            norme4 = read_float(self.dlg.valeur_b_Inf_T3_56)
            fact_im4 = read_float(self.dlg.valeur_b_Inf_T3_58)
            climat = valeur(val_b4, norme4, fact_im4)

            return (biodiversite + ressources_nat + paysage + climat) / 4.0
        except Exception as e:
            QMessageBox.critical(self.dlg, "Erreur", f"Erreur dans Environnement_T2 : {str(e)}")
            return 0

    def Environnement_T3(self):
        try:
            val_b = read_float(self.dlg.valeur_b_Inf_T3_72)
            norme = read_float(self.dlg.valeur_b_Inf_T3_66)
            fact_im = read_float(self.dlg.valeur_b_Inf_T3_65)
            biodiversite = valeur(val_b, norme, fact_im)

            val_b2 = read_float(self.dlg.valeur_b_Inf_T3_69)
            norme2 = read_float(self.dlg.valeur_b_Inf_T3_61)
            fact_im2 = read_float(self.dlg.valeur_b_Inf_T3_64)
            ressources_nat = valeur(val_b2, norme2, fact_im2)

            val_b3 = read_float(self.dlg.valeur_b_Inf_T3_63)
            norme3 = read_float(self.dlg.valeur_b_Inf_T3_67)
            fact_im3 = read_float(self.dlg.valeur_b_Inf_T3_62)
            paysage = valeur(val_b3, norme3, fact_im3)

            val_b4 = read_float(self.dlg.valeur_b_Inf_T3_71)
            norme4 = read_float(self.dlg.valeur_b_Inf_T3_68)
            fact_im4 = read_float(self.dlg.valeur_b_Inf_T3_70)
            climat = valeur(val_b4, norme4, fact_im4)

            return (biodiversite + ressources_nat + paysage + climat) / 4.0
        except Exception as e:
            QMessageBox.critical(self.dlg, "Erreur", f"Erreur dans Environnement_T3 : {str(e)}")
            return 0

    # --------------------------------------------------------------------------
    # Fonctions de calcul : Société
    # --------------------------------------------------------------------------
    def Societe_T1(self):
        try:
            val_b = read_float(self.dlg.valeur_b_Inf_T3_73)
            norme = read_float(self.dlg.valeur_b_Inf_T3_77)
            fact_im = read_float(self.dlg.valeur_b_Inf_T3_78)
            securite = valeur(val_b, norme, fact_im)

            val_b2 = read_float(self.dlg.valeur_b_Inf_T3_74)
            norme2 = read_float(self.dlg.valeur_b_Inf_T3_79)
            fact_im2 = read_float(self.dlg.valeur_b_Inf_T3_80)
            tradition = valeur(val_b2, norme2, fact_im2)

            val_b3 = read_float(self.dlg.valeur_b_Inf_T3_75)
            norme3 = read_float(self.dlg.valeur_b_Inf_T3_81)
            fact_im3 = read_float(self.dlg.valeur_b_Inf_T3_82)
            hospitalite = valeur(val_b3, norme3, fact_im3)

            val_b4 = read_float(self.dlg.valeur_b_Inf_T3_76)
            norme4 = read_float(self.dlg.valeur_b_Inf_T3_83)
            fact_im4 = read_float(self.dlg.valeur_b_Inf_T3_84)
            chomage = valeur(val_b4, norme4, fact_im4)

            return (securite + tradition + hospitalite + chomage) / 4.0
        except Exception as e:
            QMessageBox.critical(self.dlg, "Erreur", f"Erreur dans Societe_T1 : {str(e)}")
            return 0

    def Societe_T2(self):
        try:
            val_b = read_float(self.dlg.valeur_b_Inf_T3_96)
            norme = read_float(self.dlg.valeur_b_Inf_T3_90)
            fact_im = read_float(self.dlg.valeur_b_Inf_T3_89)
            securite = valeur(val_b, norme, fact_im)

            val_b2 = read_float(self.dlg.valeur_b_Inf_T3_93)
            norme2 = read_float(self.dlg.valeur_b_Inf_T3_85)
            fact_im2 = read_float(self.dlg.valeur_b_Inf_T3_88)
            tradition = valeur(val_b2, norme2, fact_im2)

            val_b3 = read_float(self.dlg.valeur_b_Inf_T3_87)
            norme3 = read_float(self.dlg.valeur_b_Inf_T3_91)
            fact_im3 = read_float(self.dlg.valeur_b_Inf_T3_86)
            hospitalite = valeur(val_b3, norme3, fact_im3)

            val_b4 = read_float(self.dlg.valeur_b_Inf_T3_95)
            norme4 = read_float(self.dlg.valeur_b_Inf_T3_92)
            fact_im4 = read_float(self.dlg.valeur_b_Inf_T3_94)
            chomage = valeur(val_b4, norme4, fact_im4)

            return (securite + tradition + hospitalite + chomage) / 4.0
        except Exception as e:
            QMessageBox.critical(self.dlg, "Erreur", f"Erreur dans Societe_T2 : {str(e)}")
            return 0

    def Societe_T3(self):
        try:
            val_b = read_float(self.dlg.valeur_b_Inf_T3_108)
            norme = read_float(self.dlg.valeur_b_Inf_T3_102)
            fact_im = read_float(self.dlg.valeur_b_Inf_T3_101)
            securite = valeur(val_b, norme, fact_im)

            val_b2 = read_float(self.dlg.valeur_b_Inf_T3_105)
            norme2 = read_float(self.dlg.valeur_b_Inf_T3_97)
            fact_im2 = read_float(self.dlg.valeur_b_Inf_T3_100)
            tradition = valeur(val_b2, norme2, fact_im2)

            val_b3 = read_float(self.dlg.valeur_b_Inf_T3_99)
            norme3 = read_float(self.dlg.valeur_b_Inf_T3_103)
            fact_im3 = read_float(self.dlg.valeur_b_Inf_T3_98)
            hospitalite = valeur(val_b3, norme3, fact_im3)

            val_b4 = read_float(self.dlg.valeur_b_Inf_T3_107)
            norme4 = read_float(self.dlg.valeur_b_Inf_T3_104)
            fact_im4 = read_float(self.dlg.valeur_b_Inf_T3_106)
            chomage = valeur(val_b4, norme4, fact_im4)

            return (securite + tradition + hospitalite + chomage) / 4.0
        except Exception as e:
            QMessageBox.critical(self.dlg, "Erreur", f"Erreur dans Societe_T3 : {str(e)}")
            return 0

    # --------------------------------------------------------------------------
    # Décision finale
    # --------------------------------------------------------------------------
    def decision_final(self, dec_eco, dec_env, dec_soc):
        """
        Combine les décisions (Durable/NonDurable) de 3 composantes.
        """
        if dec_eco == "Durable" and dec_env == "Durable" and dec_soc == "Durable":
            return "Durable"
        else:
            return "Non durable"

    def decision_final_T1(self):
        try:
            eco = self.Economie_T1()
            env = self.Environnement_T1()
            soc = self.Societe_T1()

            dec_eco = decision(eco)
            dec_env = decision(env)
            dec_soc = decision(soc)

            self.dec_eco_T1 = dec_eco
            self.dec_env_T1 = dec_env
            self.dec_soc_T1 = dec_soc

            f_ec = read_float(self.dlg.fact_inf)
            f_env = read_float(self.dlg.valeur_b_Inf_T3_42)
            f_soc = read_float(self.dlg.valeur_b_Inf_T3_78)

            somme_pond = f_ec + f_env + f_soc
            if somme_pond == 0:
                valeur_moy = 0
            else:
                valeur_moy = (eco + env + soc) / somme_pond

            self.dlg.valeur_moy_ec_T1.setText(str(valeur_moy))
            decision_t1 = self.decision_final(dec_eco, dec_env, dec_soc)
            self.dlg.decision_ec_T3.setText(str(decision_t1))
        except Exception as e:
            QMessageBox.critical(self.dlg, "Erreur", f"Erreur dans decision_final_T1 : {str(e)}")

    def decision_final_T2(self):
        try:
            eco = self.Economie_T2()
            env = self.Environnement_T2()
            soc = self.Societe_T2()

            dec_eco = decision(eco)
            dec_env = decision(env)
            dec_soc = decision(soc)

            self.dec_eco_T2 = dec_eco
            self.dec_env_T2 = dec_env
            self.dec_soc_T2 = dec_soc

            f_ec = read_float(self.dlg.inf_fi2)
            f_env = read_float(self.dlg.valeur_b_Inf_T3_53)
            f_soc = read_float(self.dlg.valeur_b_Inf_T3_89)

            somme_pond = f_ec + f_env + f_soc
            if somme_pond == 0:
                valeur_moy = 0
            else:
                valeur_moy = (eco + env + soc) / somme_pond

            self.dlg.valeur_moy_ec_T2.setText(str(valeur_moy))
            decision_t2 = self.decision_final(dec_eco, dec_env, dec_soc)
            self.dlg.valeur_moy_envir_T1.setText(str(decision_t2))
        except Exception as e:
            QMessageBox.critical(self.dlg, "Erreur", f"Erreur dans decision_final_T2 : {str(e)}")

    def decision_final_T3(self):
        try:
            eco = self.Economie_T3()
            env = self.Environnement_T3()
            soc = self.Societe_T3()

            dec_eco = decision(eco)
            dec_env = decision(env)
            dec_soc = decision(soc)

            self.dec_eco_T3 = dec_eco
            self.dec_env_T3 = dec_env
            self.dec_soc_T3 = dec_soc

            f_ec = read_float(self.dlg.valeur_b_Inf_T3_29)
            f_env = read_float(self.dlg.valeur_b_Inf_T3_65)
            f_soc = read_float(self.dlg.valeur_b_Inf_T3_101)

            somme_pond = f_ec + f_env + f_soc
            if somme_pond == 0:
                valeur_moy = 0
            else:
                valeur_moy = (eco + env + soc) / somme_pond

            self.dlg.valeur_moy_ec_T3.setText(str(valeur_moy))
            decision_t3 = self.decision_final(dec_eco, dec_env, dec_soc)
            self.dlg.valeur_moy_envir_T2.setText(str(decision_t3))
        except Exception as e:
            QMessageBox.critical(self.dlg, "Erreur", f"Erreur dans decision_final_T3 : {str(e)}")

    def calculer_decision_finale(self):
        """
        Calcule les décisions pour T1, T2, T3.
        """
        self.decision_final_T1()
        self.decision_final_T2()
        self.decision_final_T3()

    def afficher_solutions_finales(self):
        """
        Affiche la SolutionsDialog.
        """
        solutions_economie = (
            "<ul>"
            "<li>Encourager l'investissement local</li>"
            "<li>Diversifier l'offre touristique</li>"
            "<li>Moderniser les infrastructures</li>"
            "</ul>"
        )
        solutions_environnement = (
            "<ul>"
            "<li>Préserver la biodiversité</li>"
            "<li>Réduire la pollution, gérer les déchets</li>"
            "<li>Économiser l'eau et l'énergie</li>"
            "</ul>"
        )
        solutions_societe = (
            "<ul>"
            "<li>Améliorer la sécurité, la formation</li>"
            "<li>Promouvoir la culture/tradition</li>"
            "<li>Lutter contre le chômage</li>"
            "</ul>"
        )

        txt = (
            "<h3 style='color:#e74c3c; font-weight:bold;'>SOLUTIONS DE DURABILITÉ</h3>"
            "<div style='font-size:14px; color:#2c3e50;'>"
        )

        # T1
        txt += "<h4 style='color:#2980b9;'>Période T1 :</h4>"
        if self.dec_eco_T1 == "Non durable":
            txt += "<b>Économie :</b> " + solutions_economie
        if self.dec_env_T1 == "Non durable":
            txt += "<b>Environnement :</b> " + solutions_environnement
        if self.dec_soc_T1 == "Non durable":
            txt += "<b>Société :</b> " + solutions_societe
        if (self.dec_eco_T1 == "Durable" and
            self.dec_env_T1 == "Durable" and
            self.dec_soc_T1 == "Durable"):
            txt += "<p>Tout est durable ! Bravo.</p>"

        # T2
        txt += "<h4 style='color:#2980b9;'>Période T2 :</h4>"
        if self.dec_eco_T2 == "Non durable":
            txt += "<b>Économie :</b> " + solutions_economie
        if self.dec_env_T2 == "Non durable":
            txt += "<b>Environnement :</b> " + solutions_environnement
        if self.dec_soc_T2 == "Non durable":
            txt += "<b>Société :</b> " + solutions_societe
        if (self.dec_eco_T2 == "Durable" and
            self.dec_env_T2 == "Durable" and
            self.dec_soc_T2 == "Durable"):
            txt += "<p>Tout est durable ! Bravo.</p>"

        # T3
        txt += "<h4 style='color:#2980b9;'>Période T3 :</h4>"
        if self.dec_eco_T3 == "Non durable":
            txt += "<b>Économie :</b> " + solutions_economie
        if self.dec_env_T3 == "Non durable":
            txt += "<b>Environnement :</b> " + solutions_environnement
        if self.dec_soc_T3 == "Non durable":
            txt += "<b>Société :</b> " + solutions_societe
        if (self.dec_eco_T3 == "Durable" and
            self.dec_env_T3 == "Durable" and
            self.dec_soc_T3 == "Durable"):
            txt += "<p>Tout est durable ! Bravo.</p>"

        txt += "</div>"

        sol_dlg = SolutionsDialog(txt, parent=self.dlg)
        sol_dlg.exec_()  # QDialog modal

    def run(self):
        if not hasattr(self, 'dlg'):
            self.dlg = ProjetDurabiliteDialog()
            flags = self.dlg.windowFlags()
            flags = flags | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint | Qt.Window
            self.dlg.setWindowFlags(flags)

            # StyleSheet
            style_sheet = """
            QDialog {
                background-color: #f8f9fa; 
                border: 1px solid #ced6e0;
                border-radius: 8px;
            }
            QWidget {
                font-family: "Segoe UI", "Roboto", Arial, sans-serif;
                font-size: 14px;
                color: #2c3e50;
            }
            QPushButton {
                background-color: #3498db;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f5b77;
                padding-left: 10px; 
                padding-top: 6px;
            }
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #dcdcdc;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
            QLabel {
                font-size: 14px;
                color: #2c3e50;
                background: transparent;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #3498db;
                border-radius: 6px;
                margin-top: 8px;
                background-color: #ecf0f1;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 8px;
                background-color: #3498db;
                color: white;
                border-radius: 4px;
            }
            QTabWidget::pane {
                border: 1px solid #3498db;
                border-radius: 6px;
            }
            QTabBar::tab {
                background: #ffffff;
                border: 1px solid #3498db;
                padding: 6px 12px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #3498db;
                color: #ffffff;
                font-weight: 600;
            }
            """
            self.dlg.setStyleSheet(style_sheet)

            # Connecter les boutons
            self.dlg.DecisionFinal.clicked.connect(self.calculer_decision_finale)
            self.dlg.Solution_button.clicked.connect(self.afficher_solutions_finales)

        self.dlg.show()
        result = self.dlg.exec_()
        if result:
            try:
                pass
            except Exception as e:
                QMessageBox.critical(self.dlg, "Erreur", f"Une erreur est survenue : {str(e)}")
