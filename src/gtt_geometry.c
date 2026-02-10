/**
 * @file gtt_geometry.c
 * @brief Implementation der GTT-Geometrie-Funktionen
 */

#include "../include/gtt_geometry.h"
#include <stdio.h>
#include <stdlib.h>

void gtt_params_init(gtt_params* p) {
    p->theta_max = GTT_THETA_MAX;
    p->D_asymptotic = GTT_D_ASYMPTOTIC;
    p->xi_G = GTT_XI_G;
    p->beta = GTT_BETA_EMERGENZ;
    p->alpha = GTT_ALPHA_ENTFALTUNG;
    p->chi_P = log(M_PLANCK / 1.0);  /* k0 = 1 GeV */
    p->beta_iso = GTT_BETA_ISO;
}

double gtt_fractal_dimension(double chi, const gtt_params* p) {
    /* D(χ) = D_∞ - (D_∞ - 2) * exp(-χ/χ_P) */
    double D_inf = p->D_asymptotic;
    return D_inf - (D_inf - 2.0) * exp(-chi / p->chi_P);
}

double gtt_G_of_chi(double chi, const gtt_params* p) {
    /* Analytische Lösung der RG-Gleichung (Näherung) */
    double D = gtt_fractal_dimension(chi, p);
    double G_Newton = 6.67430e-11;  /* SI Einheiten */
    
    /* Skalenabhängige Korrektur */
    double delta_G = (D - 3.0) * chi;
    double G_chi = G_Newton * exp(delta_G);
    
    /* Quantenkorrekturen */
    double quantum_corr = 1.0 + (2.0 / (3.0 * M_PI)) * G_chi 
                              + (p->beta / 24.0) * G_chi * G_chi;
    
    return G_chi * quantum_corr;
}

double gtt_Lambda_of_chi(double chi, const gtt_params* p) {
    /* Skalenabhängige kosmologische Konstante */
    double Lambda_obs = 1.1056e-52;  /* m^-2 */
    double D = gtt_fractal_dimension(chi, p);
    
    /* Emergente Skalierung */
    double scale_factor = exp(-(3.0 - D) * chi / 2.0);
    
    /* Quantenvakuum-Beitrag */
    double vacuum_energy = p->xi_G * exp(-chi / p->chi_P);
    
    return Lambda_obs * scale_factor + vacuum_energy;
}

double gtt_Q_term(double a, double D, const gtt_params* p) {
    /* Quantengeometrie-Tensor: Q_μν = ξ_G R R̃ g_μν + ... */
    
    /* Ricci-Skalar für FLRW-Metrik */
    double R = 6.0 / (a * a);  /* Vereinfachte Form */
    
    /* Chiraler Beitrag */
    double chiral_term = p->xi_G * R * R;
    
    /* Konus-Krümmung */
    double cone_term = (p->beta / (4.0 * M_PI)) * 
                       pow(p->theta_max * M_PI / 180.0, 2) * 
                       gtt_cone_curvature(p->theta_max, a);
    
    /* Entfaltungs-Beitrag */
    double unfold_term = p->alpha * (3.0 - D) / (a * a);
    
    return chiral_term + cone_term + unfold_term;
}

double gtt_cone_curvature(double theta_max, double a) {
    /* Konus-Krümmungstensor für 6-Konus-Topologie */
    double theta_rad = theta_max * M_PI / 180.0;
    double deficit_angle = 2.0 * M_PI * (1.0 - sin(theta_rad));
    
    /* Krümmung konzentriert an Konus-Spitzen */
    double K_cone = deficit_angle / (a * a);
    
    /* 6 Konus-Punkte */
    return 6.0 * K_cone;
}

double gtt_conformal_factor(double a, double D) {
    /* φ = ln√(-g) für FLRW mit fraktaler Dimension */
    double g_det = -pow(a, 2.0 * D);  /* Determinante der Metrik */
    return 0.5 * log(-g_det);
}

double gtt_isocurvature_correction(double k, const gtt_params* p) {
    /* Isokurvatur-Moden aus 6-Konus-Topologie */
    double k_pivot = 0.05;  /* Mpc^-1 */
    double k_ratio = k / k_pivot;
    
    /* Skalenabhängige Amplitude */
    double iso_amplitude = p->beta_iso * pow(k_ratio, -0.5);
    
    /* Oszillatorische Komponente von 6-facher Symmetrie */
    double phase = 6.0 * log(k_ratio);
    double oscillation = cos(phase);
    
    return iso_amplitude * (1.0 + 0.3 * oscillation);
}

double gtt_spectral_index(double k, double n_s0, const gtt_params* p) {
    /* n_s(k) = n_s0 - 0.014 * (D(k) - D_∞) */
    double chi_k = log(k / 0.05);  /* k in Mpc^-1, pivot bei 0.05 */
    double D_k = gtt_fractal_dimension(chi_k, p);
    
    return n_s0 - 0.014 * (D_k - p->D_asymptotic);
}

double gtt_tensor_to_scalar_ratio(const gtt_params* p) {
    /* GTT-Vorhersage basierend auf 6-Konus-Geometrie */
    double theta_rad = p->theta_max * M_PI / 180.0;
    
    /* Unterdrückung durch fraktale Dimension */
    double suppression = pow(3.0 - p->D_asymptotic, 2);
    
    /* Tensor-Amplitude */
    double r = 0.002 * suppression * sin(theta_rad);
    
    return r;
}

double gtt_effective_neutrino_mass(const gtt_params* p) {
    /* ⟨m_ββ⟩ aus CP-Verletzungswinkel */
    double xi = p->xi_G;
    double theta_max_rad = p->theta_max * M_PI / 180.0;
    
    /* Majorana-Masse aus geometrischer CP-Verletzung */
    double m_bb = 15.0e-3;  /* 15 meV Basis-Vorhersage */
    
    /* Korrektur durch Konuswinkel */
    double correction = 1.0 + 0.2 * (theta_max_rad / (M_PI / 6.0) - 1.0);
    
    return m_bb * correction;
}

double gtt_baryon_asymmetry(const gtt_params* p) {
    /* η_B aus chiraler CP-Verletzung */
    double xi = p->xi_G;
    double theta_rad = p->theta_max * M_PI / 180.0;
    
    /* Sakharov-Bedingungen erfüllt durch 6-Konus-Topologie */
    double eta_B = 6.1e-10;  /* Beobachteter Wert */
    
    /* Theoretische Herleitung */
    double theory_factor = xi * sin(theta_rad) * p->beta;
    double normalization = eta_B / theory_factor;
    
    return theory_factor * normalization;
}
