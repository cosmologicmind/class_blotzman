"""
GTT Analyzer - Datenanalyse und Vergleich mit Beobachtungen
============================================================

Dieses Modul vergleicht GTT-Vorhersagen mit aktuellen Beobachtungsdaten
(Planck 2018, Pantheon SNe Ia, DESI, etc.)

Autor: GTT Theory Group
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
from gtt_model import GTTModel, CosmologyParameters, GTTParameters


class ObservationalData:
    """Container für Beobachtungsdaten"""
    
    @staticmethod
    def planck_2018() -> Dict:
        """Planck 2018 Ergebnisse"""
        return {
            'H0': 67.4,
            'H0_err': 0.5,
            'Omega_b': 0.0493,
            'Omega_cdm': 0.264,
            'n_s': 0.9649,
            'n_s_err': 0.0042,
            'A_s': 2.1e-9,
            'A_s_err': 0.03e-9,
            'tau_reio': 0.0544,
            'sigma_8': 0.811,
            'sigma_8_err': 0.006,
            'S_8': 0.834,
            'S_8_err': 0.016
        }
    
    @staticmethod
    def sh0es_2022() -> Dict:
        """SH0ES 2022 lokale H0-Messung"""
        return {
            'H0': 73.04,
            'H0_err': 1.04
        }
    
    @staticmethod
    def cmb_s4_sensitivity() -> Dict:
        """CMB-S4 erwartete Sensitivität"""
        return {
            'beta_iso_sensitivity': 0.008,
            'r_sensitivity': 0.001,
            'n_s_err': 0.002
        }
    
    @staticmethod
    def legend_1000_sensitivity() -> Dict:
        """LEGEND-1000 Sensitivität für 0νββ"""
        return {
            'm_bb_sensitivity_meV': 10.0,  # meV
            'half_life_years': 1e28
        }
    
    @staticmethod
    def desi_2024() -> Dict:
        """DESI 2024 BAO-Messungen"""
        return {
            'H0': 68.5,
            'H0_err': 1.2,
            'S_8': 0.76,
            'S_8_err': 0.03
        }


class GTTAnalyzer:
    """
    Analysiert GTT-Vorhersagen und vergleicht mit Beobachtungen
    """
    
    def __init__(self, model: GTTModel):
        """
        Initialisiert Analyzer
        
        Parameters
        ----------
        model : GTTModel
            GTT-Modell für Berechnungen
        """
        self.model = model
        self.obs_data = ObservationalData()
    
    def chi_squared_cmb(self, C_l_theory: np.ndarray, 
                        C_l_obs: np.ndarray,
                        C_l_err: np.ndarray) -> float:
        """
        Berechnet χ² für CMB-Spektrum
        
        Parameters
        ----------
        C_l_theory : np.ndarray
            Theoretisches Spektrum
        C_l_obs : np.ndarray
            Beobachtetes Spektrum
        C_l_err : np.ndarray
            Fehler
            
        Returns
        -------
        float
            χ²/DoF
        """
        chi2 = np.sum(((C_l_theory - C_l_obs) / C_l_err)**2)
        dof = len(C_l_obs)
        return chi2 / dof
    
    def compare_with_planck(self) -> Dict:
        """
        Vergleicht GTT-Vorhersagen mit Planck 2018
        
        Returns
        -------
        Dict
            Vergleichsergebnisse
        """
        planck = self.obs_data.planck_2018()
        pred = self.model.compute_predictions()
        
        # H0-Vergleich
        H0_early = pred['H0_early']
        H0_planck = planck['H0']
        H0_sigma = abs(H0_early - H0_planck) / planck['H0_err']
        
        # n_s-Vergleich
        n_s_gtt = self.model.cosmo.n_s
        n_s_planck = planck['n_s']
        n_s_sigma = abs(n_s_gtt - n_s_planck) / planck['n_s_err']
        
        results = {
            'H0_gtt': H0_early,
            'H0_planck': H0_planck,
            'H0_sigma': H0_sigma,
            'H0_compatible': H0_sigma < 3.0,
            'n_s_gtt': n_s_gtt,
            'n_s_planck': n_s_planck,
            'n_s_sigma': n_s_sigma,
            'n_s_compatible': n_s_sigma < 3.0
        }
        
        return results
    
    def compare_with_sh0es(self) -> Dict:
        """
        Vergleicht mit SH0ES lokaler H0-Messung
        
        Returns
        -------
        Dict
            Vergleichsergebnisse
        """
        sh0es = self.obs_data.sh0es_2022()
        pred = self.model.compute_predictions()
        
        H0_late = pred['H0_late']
        H0_sh0es = sh0es['H0']
        H0_sigma = abs(H0_late - H0_sh0es) / sh0es['H0_err']
        
        results = {
            'H0_gtt_late': H0_late,
            'H0_sh0es': H0_sh0es,
            'H0_sigma': H0_sigma,
            'H0_compatible': H0_sigma < 3.0,
            'tension_resolved': pred['H0_tension_percent'] < 5.0
        }
        
        return results
    
    def predict_cmb_s4_detection(self) -> Dict:
        """
        Vorhersage für CMB-S4 Detektion
        
        Returns
        -------
        Dict
            Detektions-Vorhersagen
        """
        cmb_s4 = self.obs_data.cmb_s4_sensitivity()
        pred = self.model.compute_predictions()
        
        # β_iso Detektion
        beta_iso = pred['beta_iso']
        beta_iso_sens = cmb_s4['beta_iso_sensitivity']
        beta_iso_sigma = beta_iso / beta_iso_sens
        
        # r Detektion
        r = pred['r_tensor']
        r_sens = cmb_s4['r_sensitivity']
        r_sigma = r / r_sens
        
        results = {
            'beta_iso': beta_iso,
            'beta_iso_sensitivity': beta_iso_sens,
            'beta_iso_sigma': beta_iso_sigma,
            'beta_iso_detectable': beta_iso_sigma > 3.0,
            'r_tensor': r,
            'r_sensitivity': r_sens,
            'r_sigma': r_sigma,
            'r_detectable': r_sigma > 3.0
        }
        
        return results
    
    def predict_legend_detection(self) -> Dict:
        """
        Vorhersage für LEGEND-1000 Detektion
        
        Returns
        -------
        Dict
            Detektions-Vorhersagen
        """
        legend = self.obs_data.legend_1000_sensitivity()
        pred = self.model.compute_predictions()
        
        m_bb = pred['m_betabeta_meV']
        m_bb_sens = legend['m_bb_sensitivity_meV']
        m_bb_sigma = m_bb / m_bb_sens
        
        results = {
            'm_betabeta_meV': m_bb,
            'm_bb_sensitivity_meV': m_bb_sens,
            'm_bb_sigma': m_bb_sigma,
            'detectable': m_bb_sigma > 1.0,
            'discovery_probability': min(1.0, m_bb_sigma / 3.0)
        }
        
        return results
    
    def compare_with_desi(self) -> Dict:
        """
        Vergleicht mit DESI 2024 Ergebnissen
        
        Returns
        -------
        Dict
            Vergleichsergebnisse
        """
        desi = self.obs_data.desi_2024()
        
        # S_8 Berechnung (vereinfacht)
        Omega_m = self.model.cosmo.Omega_m
        sigma_8 = 0.811  # Planck-Wert
        
        # GTT-Korrektur: Unterdrückung durch fraktale Dimension
        D = self.model.gtt.D_asymptotic
        suppression = (3.0 - D) / (3.0 - 2.79167)
        sigma_8_gtt = sigma_8 * suppression
        
        S_8_gtt = sigma_8_gtt * np.sqrt(Omega_m / 0.3)
        S_8_desi = desi['S_8']
        S_8_sigma = abs(S_8_gtt - S_8_desi) / desi['S_8_err']
        
        results = {
            'S_8_gtt': S_8_gtt,
            'S_8_desi': S_8_desi,
            'S_8_sigma': S_8_sigma,
            'S_8_compatible': S_8_sigma < 3.0,
            'sigma_8_suppression': suppression
        }
        
        return results
    
    def falsification_criteria(self) -> Dict:
        """
        Definiert Falsifikationskriterien
        
        Returns
        -------
        Dict
            Falsifikationskriterien und Status
        """
        pred = self.model.compute_predictions()
        
        criteria = {
            'beta_iso': {
                'prediction': pred['beta_iso'],
                'falsified_if_below': 0.002,
                'falsified_if_above': 0.050,
                'test': 'CMB-S4',
                'year': 2030
            },
            'm_betabeta': {
                'prediction_meV': pred['m_betabeta_meV'],
                'falsified_if_below_meV': 10.0,
                'falsified_if_above_meV': 20.0,
                'test': 'LEGEND-1000',
                'year': 2030
            },
            'S_8': {
                'prediction': 0.76,
                'falsified_if_above': 0.83,
                'test': 'EUCLID/DESI',
                'year': 2025
            },
            'r_tensor': {
                'prediction': pred['r_tensor'],
                'falsified_if_above': 0.01,
                'test': 'CMB-S4',
                'year': 2030
            }
        }
        
        return criteria
    
    def generate_report(self) -> str:
        """
        Generiert vollständigen Analyse-Report
        
        Returns
        -------
        str
            Formatierter Report
        """
        report = []
        report.append("=" * 70)
        report.append("GTT-WELTFORMEL: Vollständiger Analyse-Report")
        report.append("=" * 70)
        report.append("")
        
        # Planck-Vergleich
        report.append("1. VERGLEICH MIT PLANCK 2018")
        report.append("-" * 70)
        planck_comp = self.compare_with_planck()
        report.append(f"H0 (GTT):     {planck_comp['H0_gtt']:.2f} km/s/Mpc")
        report.append(f"H0 (Planck):  {planck_comp['H0_planck']:.2f} km/s/Mpc")
        report.append(f"Abweichung:   {planck_comp['H0_sigma']:.1f}σ")
        report.append(f"Kompatibel:   {'Ja' if planck_comp['H0_compatible'] else 'Nein'}")
        report.append("")
        
        # SH0ES-Vergleich
        report.append("2. VERGLEICH MIT SH0ES 2022")
        report.append("-" * 70)
        sh0es_comp = self.compare_with_sh0es()
        report.append(f"H0 (GTT spät): {sh0es_comp['H0_gtt_late']:.2f} km/s/Mpc")
        report.append(f"H0 (SH0ES):    {sh0es_comp['H0_sh0es']:.2f} km/s/Mpc")
        report.append(f"Abweichung:    {sh0es_comp['H0_sigma']:.1f}σ")
        report.append(f"Spannung gelöst: {'Ja' if sh0es_comp['tension_resolved'] else 'Nein'}")
        report.append("")
        
        # CMB-S4 Vorhersagen
        report.append("3. CMB-S4 DETEKTIONS-VORHERSAGEN (2030-2035)")
        report.append("-" * 70)
        cmb_s4 = self.predict_cmb_s4_detection()
        report.append(f"β_iso:         {cmb_s4['beta_iso']:.3f}")
        report.append(f"Sensitivität:  {cmb_s4['beta_iso_sensitivity']:.3f}")
        report.append(f"Signifikanz:   {cmb_s4['beta_iso_sigma']:.1f}σ")
        report.append(f"Nachweisbar:   {'Ja' if cmb_s4['beta_iso_detectable'] else 'Nein'}")
        report.append("")
        report.append(f"r (tensor):    {cmb_s4['r_tensor']:.4f}")
        report.append(f"Sensitivität:  {cmb_s4['r_sensitivity']:.4f}")
        report.append(f"Nachweisbar:   {'Ja' if cmb_s4['r_detectable'] else 'Nein'}")
        report.append("")
        
        # LEGEND Vorhersagen
        report.append("4. LEGEND-1000 DETEKTIONS-VORHERSAGEN (2030+)")
        report.append("-" * 70)
        legend = self.predict_legend_detection()
        report.append(f"⟨m_ββ⟩:        {legend['m_betabeta_meV']:.1f} meV")
        report.append(f"Sensitivität:  {legend['m_bb_sensitivity_meV']:.1f} meV")
        report.append(f"Signifikanz:   {legend['m_bb_sigma']:.1f}σ")
        report.append(f"Nachweisbar:   {'Ja' if legend['detectable'] else 'Nein'}")
        report.append(f"Entdeckungs-Wahrscheinlichkeit: {legend['discovery_probability']*100:.0f}%")
        report.append("")
        
        # DESI Vergleich
        report.append("5. VERGLEICH MIT DESI 2024")
        report.append("-" * 70)
        desi_comp = self.compare_with_desi()
        report.append(f"S_8 (GTT):     {desi_comp['S_8_gtt']:.3f}")
        report.append(f"S_8 (DESI):    {desi_comp['S_8_desi']:.3f}")
        report.append(f"Abweichung:    {desi_comp['S_8_sigma']:.1f}σ")
        report.append(f"Kompatibel:    {'Ja' if desi_comp['S_8_compatible'] else 'Nein'}")
        report.append("")
        
        # Falsifikationskriterien
        report.append("6. FALSIFIKATIONSKRITERIEN")
        report.append("-" * 70)
        criteria = self.falsification_criteria()
        for key, crit in criteria.items():
            report.append(f"{key}:")
            report.append(f"  Test: {crit['test']} ({crit['year']})")
            if 'prediction' in crit:
                report.append(f"  Vorhersage: {crit['prediction']:.4f}")
            if 'prediction_meV' in crit:
                report.append(f"  Vorhersage: {crit['prediction_meV']:.1f} meV")
            report.append("")
        
        report.append("=" * 70)
        
        return "\n".join(report)


def main():
    """Hauptfunktion für Analyse"""
    print("Initialisiere GTT-Analyzer...\n")
    
    # Modell erstellen
    model = GTTModel()
    analyzer = GTTAnalyzer(model)
    
    # Report generieren
    report = analyzer.generate_report()
    print(report)
    
    # Speichern
    with open('gtt_analysis_report.txt', 'w') as f:
        f.write(report)
    print("\nReport gespeichert in: gtt_analysis_report.txt")


if __name__ == "__main__":
    main()
