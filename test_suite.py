#!/usr/bin/env python3
"""
GTT Blotzman Code - Vollständige Test-Suite
============================================

Systematische Tests aller Module mit Debugging-Output.

Autor: GTT Theory Group
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))

import numpy as np
from gtt_model import GTTModel, CosmologyParameters, GTTParameters
from gtt_analyzer import GTTAnalyzer
import traceback


class TestSuite:
    """Test-Suite für GTT Blotzman Code"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
        
    def test(self, name, func):
        """Führt einen Test aus"""
        print(f"\n{'='*70}")
        print(f"TEST: {name}")
        print('='*70)
        try:
            func()
            print(f"✅ PASSED: {name}")
            self.passed += 1
            self.tests.append((name, True, None))
        except Exception as e:
            print(f"❌ FAILED: {name}")
            print(f"Error: {e}")
            traceback.print_exc()
            self.failed += 1
            self.tests.append((name, False, str(e)))
    
    def summary(self):
        """Gibt Zusammenfassung aus"""
        print(f"\n{'='*70}")
        print("TEST SUMMARY")
        print('='*70)
        print(f"Total: {self.passed + self.failed}")
        print(f"Passed: {self.passed} ✅")
        print(f"Failed: {self.failed} ❌")
        print(f"Success Rate: {100*self.passed/(self.passed+self.failed):.1f}%")
        
        if self.failed > 0:
            print(f"\n{'='*70}")
            print("FAILED TESTS:")
            print('='*70)
            for name, passed, error in self.tests:
                if not passed:
                    print(f"❌ {name}: {error}")


def test_gtt_parameters():
    """Test 1: GTT-Parameter Initialisierung"""
    gtt = GTTParameters()
    
    assert gtt.theta_max == 30.0, "theta_max falsch"
    assert abs(gtt.D_asymptotic - 2.7916667) < 1e-6, "D_asymptotic falsch"
    assert gtt.xi_G == 0.004, "xi_G falsch"
    assert gtt.beta == 0.1, "beta falsch"
    assert gtt.beta_iso == 0.028, "beta_iso falsch"
    
    print(f"  theta_max: {gtt.theta_max}°")
    print(f"  D_∞: {gtt.D_asymptotic}")
    print(f"  β_iso: {gtt.beta_iso}")


def test_cosmology_parameters():
    """Test 2: Kosmologie-Parameter Initialisierung"""
    cosmo = CosmologyParameters()
    
    assert cosmo.h == 0.674, "h falsch"
    assert cosmo.Omega_b == 0.0493, "Omega_b falsch"
    assert cosmo.Omega_cdm == 0.264, "Omega_cdm falsch"
    assert abs(cosmo.Omega_m - 0.3133) < 0.001, "Omega_m falsch"
    
    print(f"  h: {cosmo.h}")
    print(f"  Ω_b: {cosmo.Omega_b}")
    print(f"  Ω_m: {cosmo.Omega_m}")


def test_fractal_dimension():
    """Test 3: Fraktale Dimension D(χ)"""
    model = GTTModel()
    
    # Bei χ=0 (heute) - D läuft noch
    D_0 = model.fractal_dimension(0.0)
    print(f"  D(χ=0): {D_0:.7f}")
    assert 2.0 <= D_0 <= 3.0, f"D(0) außerhalb Bereich [2,3]: {D_0}"
    
    # Bei χ → -∞ (frühe Zeiten) - sollte gegen 2 gehen
    D_early = model.fractal_dimension(-100.0)
    print(f"  D(χ=-100): {D_early:.7f}")
    assert abs(D_early - 2.0) < 0.1, f"D(-∞) sollte ~2 sein: {D_early}"
    
    # Bei χ → +∞ (späte Zeiten) - sollte gegen D_∞ gehen
    D_late = model.fractal_dimension(100.0)
    print(f"  D(χ=+100): {D_late:.7f}")
    assert abs(D_late - model.gtt.D_asymptotic) < 0.01, "D(+∞) sollte D_∞ sein"
    
    # Bei χ=10 sollte D nahe D_∞ sein (aber noch nicht ganz)
    D_10 = model.fractal_dimension(10.0)
    print(f"  D(χ=10): {D_10:.7f}")
    assert 2.6 < D_10 < 2.8, f"D(10) sollte nahe D_∞ sein: {D_10}"
    
    # Monotonie: D sollte mit χ wachsen
    D_minus = model.fractal_dimension(-5.0)
    D_plus = model.fractal_dimension(5.0)
    print(f"  D(χ=-5): {D_minus:.7f}, D(χ=5): {D_plus:.7f}")
    assert D_plus > D_minus, "D sollte mit χ monoton wachsen"


def test_hubble_parameter():
    """Test 4: Hubble-Parameter H(z)"""
    model = GTTModel()
    
    # H0 (heute)
    H0 = model.hubble_at_z(0.0)
    print(f"  H(z=0): {H0:.2f} km/s/Mpc")
    assert 60 < H0 < 80, f"H0 außerhalb Bereich: {H0}"
    
    # H bei z=1
    H1 = model.hubble_at_z(1.0)
    print(f"  H(z=1): {H1:.2f} km/s/Mpc")
    assert H1 > H0, "H sollte mit z wachsen"
    
    # H bei z=1100 (CMB)
    H_cmb = model.hubble_at_z(1100.0)
    print(f"  H(z=1100): {H_cmb:.2f} km/s/Mpc")
    assert H_cmb > H1, "H sollte bei CMB sehr groß sein"


def test_hubble_tension():
    """Test 5: Hubble-Spannung"""
    model = GTTModel()
    
    H0_early, H0_late = model.resolve_hubble_tension()
    tension = 100.0 * abs(H0_late - H0_early) / H0_early
    
    print(f"  H0 (früh, CMB): {H0_early:.2f} km/s/Mpc")
    print(f"  H0 (spät, SNe): {H0_late:.2f} km/s/Mpc")
    print(f"  Spannung: {tension:.1f}%")
    
    assert 60 < H0_early < 70, f"H0_early außerhalb Bereich: {H0_early}"
    assert 70 < H0_late < 80, f"H0_late außerhalb Bereich: {H0_late}"
    assert tension < 15, f"Spannung zu groß: {tension}%"


def test_primordial_spectrum():
    """Test 6: Primordiales Spektrum P_s(k)"""
    model = GTTModel()
    
    k = np.array([0.001, 0.01, 0.05, 0.1, 1.0])
    P_s = model.primordial_scalar_spectrum(k)
    
    print(f"  P_s(k=0.05): {P_s[2]:.2e}")
    
    assert len(P_s) == len(k), "Länge falsch"
    assert np.all(P_s > 0), "Negative Werte"
    assert np.all(np.isfinite(P_s)), "Nicht-endliche Werte"
    
    # Spektrum sollte mit k leicht fallen
    assert P_s[0] > P_s[-1], "Spektrum sollte mit k fallen"


def test_tensor_to_scalar():
    """Test 7: Tensor-zu-Skalar-Verhältnis r"""
    model = GTTModel()
    
    r = model.tensor_to_scalar_ratio()
    print(f"  r: {r:.6f}")
    
    assert 0 <= r < 0.1, f"r außerhalb Bereich: {r}"
    assert r < 0.01, "GTT-Vorhersage: r sollte klein sein"


def test_neutrino_mass():
    """Test 8: Effektive Neutrino-Masse"""
    model = GTTModel()
    
    m_bb = model.effective_neutrino_mass()
    m_bb_meV = m_bb * 1000.0
    
    print(f"  ⟨m_ββ⟩: {m_bb_meV:.1f} meV")
    
    assert 10 < m_bb_meV < 20, f"m_bb außerhalb Vorhersage: {m_bb_meV} meV"


def test_baryon_asymmetry():
    """Test 9: Baryon-Asymmetrie"""
    model = GTTModel()
    
    eta_B = model.baryon_asymmetry()
    print(f"  η_B: {eta_B:.2e}")
    
    assert 5e-10 < eta_B < 7e-10, f"η_B außerhalb Bereich: {eta_B}"


def test_predictions():
    """Test 10: Vollständige Vorhersagen"""
    model = GTTModel()
    
    pred = model.compute_predictions()
    
    print(f"  H0_early: {pred['H0_early']:.2f}")
    print(f"  H0_late: {pred['H0_late']:.2f}")
    print(f"  r: {pred['r_tensor']:.6f}")
    print(f"  β_iso: {pred['beta_iso']:.3f}")
    print(f"  m_ββ: {pred['m_betabeta_meV']:.1f} meV")
    
    assert 'H0_early' in pred, "H0_early fehlt"
    assert 'H0_late' in pred, "H0_late fehlt"
    assert 'r_tensor' in pred, "r_tensor fehlt"
    assert 'beta_iso' in pred, "beta_iso fehlt"
    assert 'm_betabeta_meV' in pred, "m_betabeta_meV fehlt"


def test_analyzer_planck():
    """Test 11: Vergleich mit Planck 2018"""
    model = GTTModel()
    analyzer = GTTAnalyzer(model)
    
    comp = analyzer.compare_with_planck()
    
    print(f"  H0 (GTT): {comp['H0_gtt']:.2f}")
    print(f"  H0 (Planck): {comp['H0_planck']:.2f}")
    print(f"  Abweichung: {comp['H0_sigma']:.1f}σ")
    
    assert comp['H0_sigma'] < 5.0, f"Zu große Abweichung: {comp['H0_sigma']}σ"


def test_analyzer_cmb_s4():
    """Test 12: CMB-S4 Vorhersagen"""
    model = GTTModel()
    analyzer = GTTAnalyzer(model)
    
    cmb_s4 = analyzer.predict_cmb_s4_detection()
    
    print(f"  β_iso: {cmb_s4['beta_iso']:.3f}")
    print(f"  Nachweisbar: {cmb_s4['beta_iso_detectable']}")
    print(f"  Signifikanz: {cmb_s4['beta_iso_sigma']:.1f}σ")
    
    assert cmb_s4['beta_iso'] > 0, "β_iso sollte positiv sein"


def test_analyzer_legend():
    """Test 13: LEGEND-1000 Vorhersagen"""
    model = GTTModel()
    analyzer = GTTAnalyzer(model)
    
    legend = analyzer.predict_legend_detection()
    
    print(f"  ⟨m_ββ⟩: {legend['m_betabeta_meV']:.1f} meV")
    print(f"  Nachweisbar: {legend['detectable']}")
    
    assert legend['m_betabeta_meV'] > 0, "m_ββ sollte positiv sein"


def test_numerical_stability():
    """Test 14: Numerische Stabilität"""
    model = GTTModel()
    
    # Teste extreme Werte
    z_values = [0.0, 0.1, 1.0, 10.0, 100.0, 1000.0, 1100.0]
    
    for z in z_values:
        H_z = model.hubble_at_z(z)
        assert np.isfinite(H_z), f"H(z={z}) nicht endlich: {H_z}"
        assert H_z > 0, f"H(z={z}) nicht positiv: {H_z}"
        print(f"  H(z={z}): {H_z:.2f} km/s/Mpc ✓")


def test_consistency():
    """Test 15: Konsistenz-Checks"""
    model = GTTModel()
    
    # D sollte zwischen 2 und 3 liegen
    for chi in np.linspace(-50, 50, 10):
        D = model.fractal_dimension(chi)
        assert 2.0 <= D <= 3.0, f"D(χ={chi}) außerhalb [2,3]: {D}"
    
    print("  Fraktale Dimension: 2 ≤ D ≤ 3 ✓")
    
    # G sollte positiv sein
    for chi in np.linspace(-10, 10, 10):
        G = model.G_of_chi(chi)
        assert G > 0, f"G(χ={chi}) nicht positiv: {G}"
    
    print("  Gravitationskonstante: G > 0 ✓")


def main():
    """Hauptfunktion"""
    print("=" * 70)
    print("GTT BLOTZMAN CODE - VOLLSTÄNDIGE TEST-SUITE")
    print("=" * 70)
    print()
    
    suite = TestSuite()
    
    # Führe alle Tests aus
    suite.test("GTT-Parameter Initialisierung", test_gtt_parameters)
    suite.test("Kosmologie-Parameter Initialisierung", test_cosmology_parameters)
    suite.test("Fraktale Dimension D(χ)", test_fractal_dimension)
    suite.test("Hubble-Parameter H(z)", test_hubble_parameter)
    suite.test("Hubble-Spannung", test_hubble_tension)
    suite.test("Primordiales Spektrum P_s(k)", test_primordial_spectrum)
    suite.test("Tensor-zu-Skalar-Verhältnis r", test_tensor_to_scalar)
    suite.test("Effektive Neutrino-Masse", test_neutrino_mass)
    suite.test("Baryon-Asymmetrie", test_baryon_asymmetry)
    suite.test("Vollständige Vorhersagen", test_predictions)
    suite.test("Vergleich mit Planck 2018", test_analyzer_planck)
    suite.test("CMB-S4 Vorhersagen", test_analyzer_cmb_s4)
    suite.test("LEGEND-1000 Vorhersagen", test_analyzer_legend)
    suite.test("Numerische Stabilität", test_numerical_stability)
    suite.test("Konsistenz-Checks", test_consistency)
    
    # Zusammenfassung
    suite.summary()
    
    return 0 if suite.failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
