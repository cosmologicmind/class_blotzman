"""
Plot Predictions - Visualisierung der GTT-Vorhersagen
======================================================

Erstellt Plots für CMB-Spektren, Materieverteilung und Vergleiche
mit Beobachtungsdaten.

Autor: GTT Theory Group
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from gtt_model import GTTModel
from gtt_analyzer import GTTAnalyzer, ObservationalData


class GTTPlotter:
    """Visualisierung von GTT-Vorhersagen"""
    
    def __init__(self, model: GTTModel):
        """
        Initialisiert Plotter
        
        Parameters
        ----------
        model : GTTModel
            GTT-Modell
        """
        self.model = model
        self.analyzer = GTTAnalyzer(model)
        
        # Plot-Stil
        plt.style.use('seaborn-v0_8-darkgrid')
        self.colors = {
            'gtt': '#e74c3c',
            'lcdm': '#3498db',
            'obs': '#2ecc71'
        }
    
    def plot_hubble_evolution(self, save_path: str = None):
        """
        Plottet H(z) Evolution
        
        Parameters
        ----------
        save_path : str, optional
            Pfad zum Speichern
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Rotverschiebungen
        z = np.logspace(-2, 3, 200)
        
        # GTT H(z)
        H_gtt = np.array([self.model.hubble_at_z(zi) for zi in z])
        
        # ΛCDM zum Vergleich (vereinfacht)
        H0_lcdm = 67.4
        Omega_m = 0.315
        Omega_lambda = 0.685
        H_lcdm = H0_lcdm * np.sqrt(Omega_m * (1 + z)**3 + Omega_lambda)
        
        # Plots
        ax.plot(z, H_gtt, color=self.colors['gtt'], linewidth=2.5, 
                label='GTT (SDGFT)', zorder=3)
        ax.plot(z, H_lcdm, color=self.colors['lcdm'], linewidth=2.5, 
                linestyle='--', label='ΛCDM', zorder=2)
        
        # Beobachtungsdaten
        obs = ObservationalData()
        planck = obs.planck_2018()
        sh0es = obs.sh0es_2022()
        
        ax.errorbar([1100], [planck['H0']], yerr=[planck['H0_err']], 
                   fmt='o', color=self.colors['obs'], markersize=8,
                   label='Planck 2018 (CMB)', zorder=4)
        ax.errorbar([0], [sh0es['H0']], yerr=[sh0es['H0_err']], 
                   fmt='s', color='orange', markersize=8,
                   label='SH0ES 2022 (SNe)', zorder=4)
        
        ax.set_xlabel('Rotverschiebung z', fontsize=14)
        ax.set_ylabel('H(z) [km/s/Mpc]', fontsize=14)
        ax.set_xscale('log')
        ax.set_title('Hubble-Parameter Evolution: GTT vs. ΛCDM', 
                    fontsize=16, fontweight='bold')
        ax.legend(fontsize=12, loc='upper left')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot gespeichert: {save_path}")
        else:
            plt.show()
    
    def plot_primordial_spectra(self, save_path: str = None):
        """
        Plottet primordiale Leistungsspektren
        
        Parameters
        ----------
        save_path : str, optional
            Pfad zum Speichern
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Wellenzahlen
        k = np.logspace(-4, 0, 300)
        
        # Skalar-Spektrum
        P_s = self.model.primordial_scalar_spectrum(k)
        
        # ΛCDM zum Vergleich
        k_pivot = 0.05
        n_s_lcdm = 0.9649
        A_s_lcdm = 2.1e-9
        P_s_lcdm = A_s_lcdm * (k / k_pivot)**(n_s_lcdm - 1.0)
        
        # Plot 1: Skalar-Spektrum
        ax1.loglog(k, P_s, color=self.colors['gtt'], linewidth=2.5,
                  label='GTT (mit Isokurvatur)')
        ax1.loglog(k, P_s_lcdm, color=self.colors['lcdm'], linewidth=2.5,
                  linestyle='--', label='ΛCDM')
        
        ax1.axvline(k_pivot, color='gray', linestyle=':', alpha=0.5,
                   label=f'Pivot: k = {k_pivot} Mpc⁻¹')
        
        ax1.set_xlabel('Wellenzahl k [Mpc⁻¹]', fontsize=12)
        ax1.set_ylabel('P_s(k)', fontsize=12)
        ax1.set_title('Primordiales Skalar-Spektrum', fontsize=14, fontweight='bold')
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Isokurvatur-Korrektur
        iso_corr = []
        for ki in k:
            chi_k = np.log(ki / k_pivot)
            D_k = self.model.fractal_dimension(chi_k)
            k_ratio = ki / k_pivot
            iso_amplitude = self.model.gtt.beta_iso * k_ratio**(-0.5)
            phase = 6.0 * np.log(k_ratio)
            oscillation = np.cos(phase)
            iso_corr.append(iso_amplitude * (1.0 + 0.3 * oscillation))
        
        iso_corr = np.array(iso_corr)
        
        ax2.semilogx(k, iso_corr * 100, color=self.colors['gtt'], linewidth=2.5)
        ax2.axhline(0, color='black', linestyle='-', linewidth=0.5)
        ax2.axhline(self.model.gtt.beta_iso * 100, color='red', 
                   linestyle='--', alpha=0.7, 
                   label=f'β_iso = {self.model.gtt.beta_iso:.3f}')
        
        ax2.set_xlabel('Wellenzahl k [Mpc⁻¹]', fontsize=12)
        ax2.set_ylabel('Isokurvatur-Korrektur [%]', fontsize=12)
        ax2.set_title('Isokurvatur-Moden (6-Konus-Topologie)', 
                     fontsize=14, fontweight='bold')
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot gespeichert: {save_path}")
        else:
            plt.show()
    
    def plot_fractal_dimension(self, save_path: str = None):
        """
        Plottet skalenabhängige fraktale Dimension D(χ)
        
        Parameters
        ----------
        save_path : str, optional
            Pfad zum Speichern
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Skalen
        chi = np.linspace(-50, 50, 500)
        
        # Fraktale Dimension
        D = np.array([self.model.fractal_dimension(c) for c in chi])
        
        # Plot 1: D(χ)
        ax1.plot(chi, D, color=self.colors['gtt'], linewidth=2.5)
        ax1.axhline(3.0, color='gray', linestyle='--', alpha=0.5, 
                   label='D = 3 (klassisch)')
        ax1.axhline(2.0, color='gray', linestyle=':', alpha=0.5, 
                   label='D = 2 (topologisch)')
        ax1.axhline(self.model.gtt.D_asymptotic, color='red', 
                   linestyle='--', alpha=0.7,
                   label=f'D_∞ = {self.model.gtt.D_asymptotic:.4f}')
        
        ax1.set_xlabel('Renormierungsskala χ = ln(k/k₀)', fontsize=12)
        ax1.set_ylabel('Fraktale Dimension D(χ)', fontsize=12)
        ax1.set_title('Skalenabhängige Fraktale Dimension', 
                     fontsize=14, fontweight='bold')
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim([1.9, 3.1])
        
        # Plot 2: G(χ) / G_Newton
        G_ratio = np.array([self.model.G_of_chi(c) / self.model.G_N for c in chi])
        
        ax2.semilogy(chi, G_ratio, color=self.colors['gtt'], linewidth=2.5)
        ax2.axhline(1.0, color='gray', linestyle='--', alpha=0.5,
                   label='G_Newton')
        
        ax2.set_xlabel('Renormierungsskala χ = ln(k/k₀)', fontsize=12)
        ax2.set_ylabel('G(χ) / G_Newton', fontsize=12)
        ax2.set_title('Skalenabhängige Gravitationskonstante', 
                     fontsize=14, fontweight='bold')
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot gespeichert: {save_path}")
        else:
            plt.show()
    
    def plot_detection_prospects(self, save_path: str = None):
        """
        Plottet Detektions-Aussichten für zukünftige Experimente
        
        Parameters
        ----------
        save_path : str, optional
            Pfad zum Speichern
        """
        fig = plt.figure(figsize=(12, 8))
        gs = GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3)
        
        # 1. CMB-S4: β_iso
        ax1 = fig.add_subplot(gs[0, 0])
        cmb_s4 = self.analyzer.predict_cmb_s4_detection()
        
        experiments = ['Planck\n2018', 'CMB-S4\n2030']
        sensitivities = [0.05, cmb_s4['beta_iso_sensitivity']]
        prediction = cmb_s4['beta_iso']
        
        ax1.bar(experiments, sensitivities, color=['lightblue', 'lightcoral'], 
               alpha=0.7, edgecolor='black')
        ax1.axhline(prediction, color='red', linewidth=2.5, linestyle='--',
                   label=f'GTT-Vorhersage: {prediction:.3f}')
        ax1.set_ylabel('β_iso Sensitivität', fontsize=11)
        ax1.set_title('Isokurvatur-Nachweis', fontsize=12, fontweight='bold')
        ax1.legend(fontsize=9)
        ax1.grid(True, alpha=0.3, axis='y')
        
        # 2. LEGEND: m_ββ
        ax2 = fig.add_subplot(gs[0, 1])
        legend_pred = self.analyzer.predict_legend_detection()
        
        experiments = ['GERDA\n2020', 'LEGEND-200\n2025', 'LEGEND-1000\n2030']
        sensitivities = [100, 30, legend_pred['m_bb_sensitivity_meV']]
        prediction = legend_pred['m_betabeta_meV']
        
        ax2.bar(experiments, sensitivities, color=['lightblue', 'lightgreen', 'lightcoral'],
               alpha=0.7, edgecolor='black')
        ax2.axhline(prediction, color='red', linewidth=2.5, linestyle='--',
                   label=f'GTT-Vorhersage: {prediction:.1f} meV')
        ax2.set_ylabel('⟨m_ββ⟩ Sensitivität [meV]', fontsize=11)
        ax2.set_title('Neutrinoloser Doppelbeta-Zerfall', fontsize=12, fontweight='bold')
        ax2.set_yscale('log')
        ax2.legend(fontsize=9)
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 3. Tensor-zu-Skalar r
        ax3 = fig.add_subplot(gs[1, 0])
        
        experiments = ['Planck\n2018', 'BICEP3\n2021', 'CMB-S4\n2030']
        sensitivities = [0.06, 0.03, cmb_s4['r_sensitivity']]
        prediction = cmb_s4['r_tensor']
        
        ax3.bar(experiments, sensitivities, 
               color=['lightblue', 'lightgreen', 'lightcoral'],
               alpha=0.7, edgecolor='black')
        ax3.axhline(prediction, color='red', linewidth=2.5, linestyle='--',
                   label=f'GTT-Vorhersage: {prediction:.4f}')
        ax3.set_ylabel('r Sensitivität', fontsize=11)
        ax3.set_title('Primordiale Gravitationswellen', fontsize=12, fontweight='bold')
        ax3.set_yscale('log')
        ax3.legend(fontsize=9)
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 4. S_8 Spannung
        ax4 = fig.add_subplot(gs[1, 1])
        desi_comp = self.analyzer.compare_with_desi()
        
        datasets = ['Planck\n2018', 'DES\n2022', 'DESI\n2024', 'GTT']
        S_8_values = [0.834, 0.773, desi_comp['S_8_desi'], desi_comp['S_8_gtt']]
        S_8_errors = [0.016, 0.026, 0.03, 0.02]
        colors_list = ['lightblue', 'lightgreen', 'lightyellow', 'lightcoral']
        
        ax4.bar(datasets, S_8_values, yerr=S_8_errors, 
               color=colors_list, alpha=0.7, edgecolor='black',
               capsize=5)
        ax4.set_ylabel('S_8 = σ_8 √(Ω_m/0.3)', fontsize=11)
        ax4.set_title('S_8 Spannung', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='y')
        ax4.set_ylim([0.72, 0.88])
        
        plt.suptitle('GTT-Vorhersagen: Detektions-Aussichten bis 2035', 
                    fontsize=16, fontweight='bold', y=0.98)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot gespeichert: {save_path}")
        else:
            plt.show()
    
    def create_summary_plot(self, save_path: str = 'gtt_summary.png'):
        """
        Erstellt zusammenfassenden Plot mit allen Hauptergebnissen
        
        Parameters
        ----------
        save_path : str
            Pfad zum Speichern
        """
        fig = plt.figure(figsize=(16, 10))
        gs = GridSpec(2, 3, figure=fig, hspace=0.3, wspace=0.3)
        
        # 1. H(z)
        ax1 = fig.add_subplot(gs[0, :2])
        z = np.logspace(-2, 3, 200)
        H_gtt = np.array([self.model.hubble_at_z(zi) for zi in z])
        ax1.plot(z, H_gtt, color=self.colors['gtt'], linewidth=2.5, label='GTT')
        ax1.set_xlabel('z', fontsize=11)
        ax1.set_ylabel('H(z) [km/s/Mpc]', fontsize=11)
        ax1.set_xscale('log')
        ax1.set_title('Hubble-Parameter', fontsize=12, fontweight='bold')
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        # 2. Fraktale Dimension
        ax2 = fig.add_subplot(gs[0, 2])
        chi = np.linspace(-30, 30, 200)
        D = np.array([self.model.fractal_dimension(c) for c in chi])
        ax2.plot(chi, D, color=self.colors['gtt'], linewidth=2.5)
        ax2.axhline(self.model.gtt.D_asymptotic, color='red', linestyle='--', alpha=0.5)
        ax2.set_xlabel('χ', fontsize=11)
        ax2.set_ylabel('D(χ)', fontsize=11)
        ax2.set_title('Fraktale Dimension', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        # 3. Primordiales Spektrum
        ax3 = fig.add_subplot(gs[1, :2])
        k = np.logspace(-4, 0, 200)
        P_s = self.model.primordial_scalar_spectrum(k)
        ax3.loglog(k, P_s, color=self.colors['gtt'], linewidth=2.5, label='GTT')
        ax3.set_xlabel('k [Mpc⁻¹]', fontsize=11)
        ax3.set_ylabel('P_s(k)', fontsize=11)
        ax3.set_title('Primordiales Spektrum', fontsize=12, fontweight='bold')
        ax3.legend(fontsize=10)
        ax3.grid(True, alpha=0.3)
        
        # 4. Vorhersagen
        ax4 = fig.add_subplot(gs[1, 2])
        ax4.axis('off')
        
        pred = self.model.compute_predictions()
        text = f"""
GTT-VORHERSAGEN

Hubble-Spannung:
  H₀ (früh): {pred['H0_early']:.1f}
  H₀ (spät): {pred['H0_late']:.1f}
  Spannung: {pred['H0_tension_percent']:.1f}%

Primordial:
  r: {pred['r_tensor']:.4f}
  β_iso: {pred['beta_iso']:.3f}

Neutrinos:
  ⟨m_ββ⟩: {pred['m_betabeta_meV']:.1f} meV

Geometrie:
  D_∞: {pred['D_asymptotic']:.4f}
  θ_max: {pred['theta_max']:.1f}°
        """
        
        ax4.text(0.1, 0.5, text, fontsize=10, family='monospace',
                verticalalignment='center')
        
        plt.suptitle('GTT-WELTFORMEL: Zusammenfassung', 
                    fontsize=18, fontweight='bold', y=0.98)
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Zusammenfassungs-Plot gespeichert: {save_path}")


def main():
    """Hauptfunktion"""
    print("Erstelle GTT-Visualisierungen...\n")
    
    model = GTTModel()
    plotter = GTTPlotter(model)
    
    # Alle Plots erstellen
    print("1. Hubble-Evolution...")
    plotter.plot_hubble_evolution('gtt_hubble_evolution.png')
    
    print("2. Primordiale Spektren...")
    plotter.plot_primordial_spectra('gtt_primordial_spectra.png')
    
    print("3. Fraktale Dimension...")
    plotter.plot_fractal_dimension('gtt_fractal_dimension.png')
    
    print("4. Detektions-Aussichten...")
    plotter.plot_detection_prospects('gtt_detection_prospects.png')
    
    print("5. Zusammenfassung...")
    plotter.create_summary_plot('gtt_summary.png')
    
    print("\nAlle Plots erstellt!")


if __name__ == "__main__":
    main()
