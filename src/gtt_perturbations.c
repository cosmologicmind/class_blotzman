/**
 * @file gtt_perturbations.c
 * @brief Störungsgleichungen für SDGFT
 * @author GTT Theory Group
 * 
 * Implementiert primordiale Spektren mit Isokurvatur-Moden
 * und skalenabhängigen Korrekturen aus der 6-Konus-Topologie.
 */

#include "../include/gtt_geometry.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/**
 * @struct primordial_spectra
 * @brief Primordiale Leistungsspektren
 */
typedef struct {
    double A_s;           /* Skalar-Amplitude */
    double n_s;           /* Spektraler Index */
    double r;             /* Tensor-zu-Skalar-Verhältnis */
    double n_t;           /* Tensor-spektraler Index */
    double k_pivot;       /* Pivot-Skala [Mpc^-1] */
    double beta_iso;      /* Isokurvatur-Amplitude */
    double alpha_s;       /* Running des spektralen Index */
} primordial_spectra;

/**
 * @brief Initialisiert primordiale Spektren mit GTT-Vorhersagen
 */
void gtt_primordial_init(primordial_spectra* ps, const gtt_params* gtt) {
    ps->A_s = 2.1e-9;           /* Planck 2018 */
    ps->n_s = 0.965;            /* Leicht reduziert durch GTT */
    ps->r = gtt_tensor_to_scalar_ratio(gtt);  /* ~0.002 */
    ps->n_t = -ps->r / 8.0;     /* Konsistenzbedingung */
    ps->k_pivot = 0.05;         /* Mpc^-1 */
    ps->beta_iso = gtt->beta_iso;  /* 0.028 */
    ps->alpha_s = -0.0003;      /* Running */
}

/**
 * @brief Berechnet primordiales Skalar-Spektrum P_s(k)
 * 
 * P_s(k) = A_s * (k/k_pivot)^(n_s-1) * [1 + β_iso * f_iso(k)]
 */
double gtt_primordial_scalar_spectrum(double k, const primordial_spectra* ps,
                                      const gtt_params* gtt) {
    double k_ratio = k / ps->k_pivot;
    
    /* Basis-Spektrum */
    double n_s_k = gtt_spectral_index(k, ps->n_s, gtt);
    double P_s = ps->A_s * pow(k_ratio, n_s_k - 1.0);
    
    /* Isokurvatur-Korrektur */
    double iso_corr = gtt_isocurvature_correction(k, gtt);
    P_s *= (1.0 + ps->beta_iso * iso_corr);
    
    /* Running */
    double ln_k = log(k_ratio);
    P_s *= exp(0.5 * ps->alpha_s * ln_k * ln_k);
    
    return P_s;
}

/**
 * @brief Berechnet primordiales Tensor-Spektrum P_t(k)
 */
double gtt_primordial_tensor_spectrum(double k, const primordial_spectra* ps,
                                      const gtt_params* gtt) {
    double k_ratio = k / ps->k_pivot;
    
    /* Tensor-Spektrum */
    double P_t = ps->r * ps->A_s * pow(k_ratio, ps->n_t);
    
    /* GTT-Unterdrückung durch fraktale Dimension */
    double chi_k = log(k / ps->k_pivot);
    double D = gtt_fractal_dimension(chi_k, gtt);
    double suppression = pow(3.0 - D, 2);
    
    P_t *= suppression;
    
    return P_t;
}

/**
 * @brief Berechnet Transfer-Funktion T(k) für Materie
 * 
 * Vereinfachte Eisenstein-Hu Formel mit GTT-Korrekturen
 */
double gtt_transfer_function(double k, double Omega_m, double Omega_b, double h,
                             const gtt_params* gtt) {
    /* Charakteristische Skalen */
    double k_eq = 0.073 * Omega_m * h * h;  /* Materie-Strahlung-Gleichheit */
    double k_silk = 1.6 * pow(Omega_b * h * h, 0.52) * 
                    pow(Omega_m * h * h, 0.73);  /* Silk-Dämpfung */
    
    /* Eisenstein-Hu Formel */
    double q = k / (13.41 * k_eq);
    double C = 14.2 + 731.0 / (1.0 + 62.5 * q);
    double L = log(2.0 * M_E + 1.8 * q);
    double T_EH = L / (L + C * q * q);
    
    /* GTT-Korrektur: Unterdrückung bei kleinen Skalen */
    double chi_k = log(k / 0.05);
    double D = gtt_fractal_dimension(chi_k, gtt);
    double gtt_suppression = exp(-(3.0 - D) * pow(k / k_silk, 2));
    
    return T_EH * gtt_suppression;
}

/**
 * @brief Berechnet Materie-Leistungsspektrum P_m(k,z)
 */
double gtt_matter_power_spectrum(double k, double z, double Omega_m, double Omega_b,
                                 double h, const primordial_spectra* ps,
                                 const gtt_params* gtt) {
    /* Primordiales Spektrum */
    double P_prim = gtt_primordial_scalar_spectrum(k, ps, gtt);
    
    /* Transfer-Funktion */
    double T_k = gtt_transfer_function(k, Omega_m, Omega_b, h, gtt);
    
    /* Wachstumsfaktor D(z) */
    double a = 1.0 / (1.0 + z);
    double growth = a;  /* Vereinfachte Form für Materie-Dominanz */
    
    /* Materie-Spektrum */
    double P_m = P_prim * T_k * T_k * growth * growth;
    
    /* Normierung */
    double sigma_8_norm = 0.811;  /* Planck 2018 */
    P_m *= sigma_8_norm * sigma_8_norm;
    
    return P_m;
}

/**
 * @brief Berechnet σ_8 Parameter (RMS-Fluktuation bei 8 Mpc/h)
 */
double gtt_compute_sigma8(double Omega_m, double Omega_b, double h,
                          const primordial_spectra* ps, const gtt_params* gtt) {
    /* Integration über k mit Top-Hat-Filter bei R = 8 Mpc/h */
    double R = 8.0 / h;  /* Mpc */
    
    int n_k = 1000;
    double k_min = 1e-4;
    double k_max = 10.0;
    double log_k_min = log(k_min);
    double log_k_max = log(k_max);
    double d_log_k = (log_k_max - log_k_min) / n_k;
    
    double integral = 0.0;
    
    for (int i = 0; i < n_k; i++) {
        double log_k = log_k_min + (i + 0.5) * d_log_k;
        double k = exp(log_k);
        
        /* Top-Hat-Fenster im Fourier-Raum */
        double x = k * R;
        double W = 3.0 * (sin(x) - x * cos(x)) / (x * x * x);
        
        /* Leistungsspektrum bei z=0 */
        double P_k = gtt_matter_power_spectrum(k, 0.0, Omega_m, Omega_b, h, ps, gtt);
        
        /* Integrand */
        integral += k * k * k * P_k * W * W * d_log_k;
    }
    
    double sigma8_squared = integral / (2.0 * M_PI * M_PI);
    return sqrt(sigma8_squared);
}

/**
 * @brief Berechnet S_8 = σ_8 * sqrt(Ω_m/0.3) Parameter
 * 
 * GTT-Vorhersage: S_8 ≈ 0.76 (reduziert gegenüber Planck)
 */
double gtt_compute_S8(double Omega_m, double Omega_b, double h,
                      const primordial_spectra* ps, const gtt_params* gtt) {
    double sigma8 = gtt_compute_sigma8(Omega_m, Omega_b, h, ps, gtt);
    double S8 = sigma8 * sqrt(Omega_m / 0.3);
    return S8;
}

/**
 * @brief Berechnet CMB-Temperatur-Leistungsspektrum C_ℓ^TT
 * 
 * Vereinfachte Berechnung für akustische Peaks
 */
void gtt_cmb_temperature_spectrum(int l_max, double* C_l_TT,
                                  double Omega_m, double Omega_b, double h,
                                  const primordial_spectra* ps,
                                  const gtt_params* gtt) {
    /* Charakteristische Skalen */
    double theta_s = 0.0104;  /* Schallhorizont-Winkel [rad] */
    double k_s = 1.0 / theta_s;  /* Schallhorizont-Wellenzahl */
    
    for (int l = 2; l <= l_max; l++) {
        /* Multipol zu Wellenzahl */
        double k = l * k_s / 14000.0;  /* Approximation */
        
        /* Primordiales Spektrum */
        double P_prim = gtt_primordial_scalar_spectrum(k, ps, gtt);
        
        /* Transfer-Funktion für CMB */
        double T_cmb = gtt_transfer_function(k, Omega_m, Omega_b, h, gtt);
        
        /* Akustische Oszillationen */
        double k_peak = M_PI * (l / 220.0);  /* Peak-Positionen */
        double oscillation = 1.0 + 0.3 * cos(k_peak);
        
        /* Silk-Dämpfung */
        double damping = exp(-pow(l / 1400.0, 2));
        
        /* C_ℓ^TT */
        C_l_TT[l] = P_prim * T_cmb * T_cmb * oscillation * damping;
        
        /* Normierung */
        C_l_TT[l] *= 5000.0 / (l * (l + 1.0));
        
        /* GTT-Korrektur bei hohen ℓ */
        if (l > 1000) {
            double chi_l = log((double)l / 1000.0);
            double D = gtt_fractal_dimension(chi_l, gtt);
            double enhancement = 1.0 + 0.05 * (3.0 - D);
            C_l_TT[l] *= enhancement;
        }
    }
}

/**
 * @brief Test-Funktion für Störungstheorie
 */
void gtt_perturbations_test() {
    printf("=== GTT Perturbations Test ===\n\n");
    
    gtt_params gtt;
    gtt_params_init(&gtt);
    
    primordial_spectra ps;
    gtt_primordial_init(&ps, &gtt);
    
    /* Primordiale Spektren */
    printf("Primordiale Spektren:\n");
    printf("  A_s = %.2e\n", ps.A_s);
    printf("  n_s = %.4f\n", ps.n_s);
    printf("  r = %.4f\n", ps.r);
    printf("  β_iso = %.3f\n", ps.beta_iso);
    
    /* Leistungsspektren bei verschiedenen k */
    printf("\nSkalar-Spektrum P_s(k):\n");
    double k_values[] = {0.001, 0.01, 0.05, 0.1, 0.5, 1.0};
    for (int i = 0; i < 6; i++) {
        double P_s = gtt_primordial_scalar_spectrum(k_values[i], &ps, &gtt);
        printf("  k = %.3f Mpc^-1: P_s = %.2e\n", k_values[i], P_s);
    }
    
    /* σ_8 und S_8 */
    printf("\nStrukturbildungs-Parameter:\n");
    double Omega_m = 0.3153;
    double Omega_b = 0.0493;
    double h = 0.674;
    
    double sigma8 = gtt_compute_sigma8(Omega_m, Omega_b, h, &ps, &gtt);
    double S8 = gtt_compute_S8(Omega_m, Omega_b, h, &ps, &gtt);
    
    printf("  σ_8 = %.3f\n", sigma8);
    printf("  S_8 = %.3f (GTT-Vorhersage: 0.76)\n", S8);
    
    printf("\n=== Test abgeschlossen ===\n");
}

#ifdef GTT_PERTURBATIONS_MAIN
int main() {
    gtt_perturbations_test();
    return 0;
}
#endif
