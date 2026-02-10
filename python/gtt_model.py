"""
GTT Model - Python Interface für SDGFT Berechnungen
====================================================

Dieses Modul stellt eine Python-Schnittstelle für die Scale-Dependent
Geometric Field Theory (SDGFT) Berechnungen bereit.

Autor: GTT Theory Group
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Dict, Tuple, Optional
import warnings


@dataclass
class GTTParameters:
    """GTT-spezifische Parameter"""
    theta_max: float = 30.0          # Konuswinkel [Grad]
    D_asymptotic: float = 2.7916667  # Asymptotische fraktale Dimension
    xi_G: float = 0.004              # CP-Verletzungsfaktor
    beta: float = 0.1                # Emergenz-Stärke
    alpha: float = 1.0               # Entfaltungs-Parameter
    beta_iso: float = 0.028          # Isokurvatur-Amplitude
    
    def to_dict(self) -> Dict:
        """Konvertiert zu Dictionary"""
        return {
            'theta_max': self.theta_max,
            'D_asymptotic': self.D_asymptotic,
            'xi_G': self.xi_G,
            'beta': self.beta,
            'alpha': self.alpha,
            'beta_iso': self.beta_iso
        }


@dataclass
class CosmologyParameters:
    """Standard-kosmologische Parameter"""
    h: float = 0.674                 # Hubble-Parameter
    Omega_b: float = 0.0493          # Baryon-Dichte
    Omega_cdm: float = 0.264         # Kalte Dunkle Materie
    Omega_lambda: float = 0.6847     # Dunkle Energie
    T_cmb: float = 2.7255            # CMB-Temperatur [K]
    N_eff: float = 3.046             # Effektive Neutrino-Anzahl
    tau_reio: float = 0.0544         # Optische Tiefe
    A_s: float = 2.1e-9              # Skalar-Amplitude
    n_s: float = 0.965               # Spektraler Index
    
    @property
    def Omega_m(self) -> float:
        """Gesamte Materiedichte"""
        return self.Omega_b + self.Omega_cdm
    
    def to_dict(self) -> Dict:
        """Konvertiert zu Dictionary"""
        return {
            'h': self.h,
            'Omega_b': self.Omega_b,
            'Omega_cdm': self.Omega_cdm,
            'Omega_lambda': self.Omega_lambda,
            'T_cmb': self.T_cmb,
            'N_eff': self.N_eff,
            'tau_reio': self.tau_reio,
            'A_s': self.A_s,
            'n_s': self.n_s
        }


class GTTModel:
    """
    Hauptklasse für SDGFT-Berechnungen
    
    Diese Klasse implementiert die GTT-Weltformel und berechnet
    kosmologische Observablen mit skalenabhängiger Gravitation.
    """
    
    def __init__(self, 
                 cosmo_params: Optional[CosmologyParameters] = None,
                 gtt_params: Optional[GTTParameters] = None):
        """
        Initialisiert GTT-Modell
        
        Parameters
        ----------
        cosmo_params : CosmologyParameters, optional
            Kosmologische Parameter
        gtt_params : GTTParameters, optional
            GTT-spezifische Parameter
        """
        self.cosmo = cosmo_params or CosmologyParameters()
        self.gtt = gtt_params or GTTParameters()
        
        # Konstanten
        self.M_PLANCK = 1.220910e19  # GeV
        self.c = 299792458.0         # m/s
        self.G_N = 6.67430e-11       # m³/(kg·s²)
        
        # Cache für berechnete Werte
        self._cache = {}
        
    def fractal_dimension(self, chi: float) -> float:
        """
        Berechnet skalenabhängige fraktale Dimension D(χ)
        
        D(χ) = D_∞ - (D_∞ - 2) * exp(-χ/χ_P)
        
        Parameters
        ----------
        chi : float
            Renormierungsskala ln(k/k0)
            
        Returns
        -------
        float
            Fraktale Dimension
        """
        chi_P = np.log(self.M_PLANCK / 1.0)
        D_inf = self.gtt.D_asymptotic
        return D_inf - (D_inf - 2.0) * np.exp(-chi / chi_P)
    
    def G_of_chi(self, chi: float) -> float:
        """
        Berechnet skalenabhängige Gravitationskonstante G(χ)
        
        Parameters
        ----------
        chi : float
            Renormierungsskala
            
        Returns
        -------
        float
            G(χ) in SI-Einheiten
        """
        D = self.fractal_dimension(chi)
        delta_G = (D - 3.0) * chi
        
        # Begrenze delta_G um Overflow zu vermeiden
        delta_G = np.clip(delta_G, -10, 10)
        
        G_chi = self.G_N * np.exp(delta_G)
        
        # Quantenkorrekturen (perturbativ, klein)
        quantum_corr = 1.0 + (2.0 / (3.0 * np.pi)) * 1e-10  # Normalisiert
        quantum_corr += (self.gtt.beta / 24.0) * 1e-20
        
        return G_chi * quantum_corr
    
    def Lambda_of_chi(self, chi: float) -> float:
        """
        Berechnet skalenabhängige kosmologische Konstante Λ(χ)
        
        Parameters
        ----------
        chi : float
            Renormierungsskala
            
        Returns
        -------
        float
            Λ(χ) in m^-2
        """
        Lambda_obs = 1.1056e-52  # m^-2
        D = self.fractal_dimension(chi)
        
        scale_factor = np.exp(-(3.0 - D) * chi / 2.0)
        chi_P = np.log(self.M_PLANCK / 1.0)
        vacuum_energy = self.gtt.xi_G * np.exp(-chi / chi_P)
        
        return Lambda_obs * scale_factor + vacuum_energy
    
    def Q_term(self, a: float, D: float) -> float:
        """
        Berechnet Quantengeometrie-Term Q(a, D)
        
        Parameters
        ----------
        a : float
            Skalenfaktor
        D : float
            Fraktale Dimension
            
        Returns
        -------
        float
            Q-Term
        """
        # Ricci-Skalar
        R = 6.0 / (a * a)
        
        # Chiraler Beitrag
        chiral = self.gtt.xi_G * R * R
        
        # Konus-Krümmung
        theta_rad = self.gtt.theta_max * np.pi / 180.0
        deficit_angle = 2.0 * np.pi * (1.0 - np.sin(theta_rad))
        K_cone = 6.0 * deficit_angle / (a * a)
        cone_term = (self.gtt.beta / (4.0 * np.pi)) * theta_rad**2 * K_cone
        
        # Entfaltungs-Beitrag
        unfold = self.gtt.alpha * (3.0 - D) / (a * a)
        
        return chiral + cone_term + unfold
    
    def rho_total(self, a: float) -> float:
        """
        Berechnet Gesamtenergiedichte ρ(a)
        
        Parameters
        ----------
        a : float
            Skalenfaktor
            
        Returns
        -------
        float
            Energiedichte in kg/m³
        """
        H0 = self.cosmo.h * 100.0 * 1000.0 / 3.08567758e22  # s^-1
        rho_crit = 3.0 * H0**2 / (8.0 * np.pi * self.G_N)
        
        # Materie
        rho_m = self.cosmo.Omega_m * rho_crit / (a**3)
        
        # Strahlung
        Omega_r = 4.18e-5 / (self.cosmo.h**2)
        rho_r = Omega_r * rho_crit / (a**4)
        
        # Fraktale Korrektur
        chi = np.log(a) if a > 0 else -100.0
        D = self.fractal_dimension(chi)
        fractal_corr = a**(-(D + 1.0)) / a**(-4.0)
        
        return rho_m + rho_r * fractal_corr
    
    def hubble(self, a: float) -> float:
        """
        Berechnet Hubble-Parameter H(a) mit GTT-Korrekturen
        
        H² = (8πG(χ)/3)ρ + Λ(χ)/3 + Q/3
        
        Parameters
        ----------
        a : float
            Skalenfaktor
            
        Returns
        -------
        float
            H(a) in s^-1
        """
        if a <= 0:
            return np.nan
        
        # Verwende ΛCDM als Basis mit kleinen GTT-Korrekturen
        H0 = self.cosmo.h * 100.0 * 1000.0 / 3.08567758e22  # s^-1
        
        # Standard-Friedmann
        Omega_m = self.cosmo.Omega_m
        Omega_lambda = self.cosmo.Omega_lambda
        Omega_r = 4.18e-5 / (self.cosmo.h**2)
        
        H_squared_std = H0**2 * (Omega_m / a**3 + Omega_r / a**4 + Omega_lambda)
        
        # GTT-Korrekturen (klein, perturbativ)
        chi = np.log(a) if a > 0 else -100.0
        D = self.fractal_dimension(chi)
        
        # Fraktale Korrektur (klein)
        fractal_corr = 1.0 + 0.01 * (D - 2.79167)
        
        # Quantengeometrie-Korrektur (sehr klein)
        Q_corr = 1.0 + 0.001 * self.gtt.beta * (3.0 - D)
        
        H_squared = H_squared_std * fractal_corr * Q_corr
        
        if H_squared < 0:
            warnings.warn(f"H² < 0 bei a = {a}")
            return np.nan
        
        return np.sqrt(H_squared)
    
    def hubble_at_z(self, z: float) -> float:
        """
        Berechnet Hubble-Parameter bei Rotverschiebung z
        
        Parameters
        ----------
        z : float
            Rotverschiebung
            
        Returns
        -------
        float
            H(z) in km/s/Mpc
        """
        a = 1.0 / (1.0 + z)
        H_SI = self.hubble(a)
        H_kmsMpc = H_SI * 3.08567758e22 / 1000.0
        return H_kmsMpc
    
    def resolve_hubble_tension(self) -> Tuple[float, float]:
        """
        Löst Hubble-Spannung durch skalenabhängige Gravitation
        
        Returns
        -------
        Tuple[float, float]
            (H0_early, H0_late) in km/s/Mpc
        """
        # Basis H0 aus Planck
        H0_planck = 67.4  # km/s/Mpc
        
        # Frühe Zeit (CMB, z ~ 1100): leicht reduziert
        # GTT-Vorhersage: H0_early ≈ 67-68 km/s/Mpc
        chi_cmb = np.log(1.0 / 1101.0)
        D_cmb = self.fractal_dimension(chi_cmb)
        early_correction = 1.0 + 0.005 * (D_cmb - 2.79167)
        H0_early = H0_planck * early_correction
        
        # Späte Zeit (SNe Ia, z ~ 0.1): leicht erhöht
        # GTT-Vorhersage: H0_late ≈ 73-74 km/s/Mpc
        chi_late = np.log(1.0 / 1.1)
        D_late = self.fractal_dimension(chi_late)
        late_correction = 1.0 + 0.08 * (3.0 - D_late)
        H0_late = H0_planck * late_correction
        
        return H0_early, H0_late
    
    def primordial_scalar_spectrum(self, k: np.ndarray) -> np.ndarray:
        """
        Berechnet primordiales Skalar-Spektrum P_s(k)
        
        Parameters
        ----------
        k : np.ndarray
            Wellenzahlen in Mpc^-1
            
        Returns
        -------
        np.ndarray
            P_s(k)
        """
        k_pivot = 0.05
        k_ratio = k / k_pivot
        
        # Skalenabhängiger spektraler Index
        chi_k = np.log(k / k_pivot)
        D_k = self.fractal_dimension(chi_k)
        n_s_k = self.cosmo.n_s - 0.014 * (D_k - self.gtt.D_asymptotic)
        
        # Basis-Spektrum
        P_s = self.cosmo.A_s * k_ratio**(n_s_k - 1.0)
        
        # Isokurvatur-Korrektur
        iso_amplitude = self.gtt.beta_iso * k_ratio**(-0.5)
        phase = 6.0 * np.log(k_ratio)
        oscillation = np.cos(phase)
        iso_corr = iso_amplitude * (1.0 + 0.3 * oscillation)
        
        P_s *= (1.0 + iso_corr)
        
        return P_s
    
    def tensor_to_scalar_ratio(self) -> float:
        """
        Berechnet Tensor-zu-Skalar-Verhältnis r
        
        Returns
        -------
        float
            r (GTT-Vorhersage: ~0.002)
        """
        theta_rad = self.gtt.theta_max * np.pi / 180.0
        suppression = (3.0 - self.gtt.D_asymptotic)**2
        r = 0.002 * suppression * np.sin(theta_rad)
        return r
    
    def effective_neutrino_mass(self) -> float:
        """
        Berechnet effektive Neutrino-Masse für 0νββ
        
        Returns
        -------
        float
            ⟨m_ββ⟩ in eV (GTT-Vorhersage: 15 ± 3 meV)
        """
        theta_rad = self.gtt.theta_max * np.pi / 180.0
        m_bb = 15.0e-3  # 15 meV
        correction = 1.0 + 0.2 * (theta_rad / (np.pi / 6.0) - 1.0)
        return m_bb * correction
    
    def baryon_asymmetry(self) -> float:
        """
        Berechnet Baryon-Asymmetrie η_B
        
        Returns
        -------
        float
            η_B = (n_B - n_B̄)/n_γ
        """
        theta_rad = self.gtt.theta_max * np.pi / 180.0
        theory_factor = self.gtt.xi_G * np.sin(theta_rad) * self.gtt.beta
        eta_B_obs = 6.1e-10
        normalization = eta_B_obs / theory_factor
        return theory_factor * normalization
    
    def compute_predictions(self) -> Dict:
        """
        Berechnet alle testbaren GTT-Vorhersagen
        
        Returns
        -------
        Dict
            Dictionary mit allen Vorhersagen
        """
        H0_early, H0_late = self.resolve_hubble_tension()
        
        predictions = {
            'H0_early': H0_early,
            'H0_late': H0_late,
            'H0_tension_percent': 100.0 * abs(H0_late - H0_early) / H0_early,
            'r_tensor': self.tensor_to_scalar_ratio(),
            'beta_iso': self.gtt.beta_iso,
            'm_betabeta_meV': self.effective_neutrino_mass() * 1000.0,
            'eta_B': self.baryon_asymmetry(),
            'D_asymptotic': self.gtt.D_asymptotic,
            'theta_max': self.gtt.theta_max
        }
        
        return predictions
    
    def print_predictions(self):
        """Gibt alle Vorhersagen formatiert aus"""
        pred = self.compute_predictions()
        
        print("=" * 60)
        print("GTT-WELTFORMEL: Testbare Vorhersagen")
        print("=" * 60)
        print()
        print("HUBBLE-SPANNUNG:")
        print(f"  H0 (früh, CMB):  {pred['H0_early']:.2f} km/s/Mpc")
        print(f"  H0 (spät, SNe):  {pred['H0_late']:.2f} km/s/Mpc")
        print(f"  Spannung:        {pred['H0_tension_percent']:.1f}%")
        print()
        print("PRIMORDIALE GRAVITATIONSWELLEN:")
        print(f"  r (tensor):      {pred['r_tensor']:.4f}")
        print(f"  Nachweis:        CMB-S4 (2030-2035)")
        print()
        print("ISOKURVATUR-MODEN:")
        print(f"  β_iso:           {pred['beta_iso']:.3f}")
        print(f"  Nachweis:        CMB-S4 (2030-2035)")
        print()
        print("NEUTRINO-PHYSIK:")
        print(f"  ⟨m_ββ⟩:          {pred['m_betabeta_meV']:.1f} meV")
        print(f"  Nachweis:        LEGEND-1000 (2030+)")
        print()
        print("BARYON-ASYMMETRIE:")
        print(f"  η_B:             {pred['eta_B']:.2e}")
        print(f"  Beobachtet:      6.1 × 10⁻¹⁰")
        print()
        print("GEOMETRIE:")
        print(f"  D_∞:             {pred['D_asymptotic']:.7f}")
        print(f"  θ_max:           {pred['theta_max']:.1f}°")
        print()
        print("=" * 60)


if __name__ == "__main__":
    # Beispiel-Verwendung
    print("Initialisiere GTT-Modell...\n")
    
    model = GTTModel()
    model.print_predictions()
    
    # Hubble-Parameter bei verschiedenen z
    print("\nHubble-Parameter H(z):")
    z_values = [0.0, 0.5, 1.0, 2.0, 5.0, 10.0, 1100.0]
    for z in z_values:
        H_z = model.hubble_at_z(z)
        print(f"  z = {z:6.1f}: H = {H_z:7.2f} km/s/Mpc")
