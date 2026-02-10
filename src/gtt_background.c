/**
 * @file gtt_background.c
 * @brief Modifizierte Hintergrundevolution für SDGFT
 * @author GTT Theory Group
 * 
 * Implementiert die GTT-Weltformel für kosmologische Hintergrunddynamik:
 * G_μν^(D) = 8πG(χ)T_μν + Λ(χ)g_μν + Q_μν
 */

#define _USE_MATH_DEFINES
#include "../include/gtt_geometry.h"
#include "../include/fractal_rg.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define _SUCCESS_ 0
#define _FAILURE_ 1

/**
 * @struct cosmology_params
 * @brief Kosmologische Parameter
 */
typedef struct {
    double h;              /* Hubble-Parameter h = H0/(100 km/s/Mpc) */
    double Omega_b;        /* Baryon-Dichte */
    double Omega_cdm;      /* Kalte Dunkle Materie */
    double Omega_lambda;   /* Dunkle Energie */
    double Omega_k;        /* Krümmung */
    double T_cmb;          /* CMB-Temperatur [K] */
    double N_eff;          /* Effektive Neutrino-Anzahl */
} cosmology_params;

/**
 * @brief Berechnet Energiedichte aller Komponenten
 */
static double rho_total(double a, const cosmology_params* cosmo, const gtt_params* gtt) {
    /* Kritische Dichte heute */
    double H0 = cosmo->h * 100.0 * 1000.0 / 3.08567758e22;  /* s^-1 */
    double rho_crit = 3.0 * H0 * H0 / (8.0 * M_PI * 6.67430e-11);
    
    /* Materie */
    double rho_m = (cosmo->Omega_b + cosmo->Omega_cdm) * rho_crit / (a * a * a);
    
    /* Strahlung */
    double Omega_r = 4.18e-5 / (cosmo->h * cosmo->h);  /* Photonen + Neutrinos */
    double rho_r = Omega_r * rho_crit / (a * a * a * a);
    
    /* Fraktale Dimension-Korrektur */
    double chi = log(a);
    double D = gtt_fractal_dimension(chi, gtt);
    double fractal_corr = pow(a, -(D + 1.0)) / pow(a, -4.0);
    
    return rho_m + rho_r * fractal_corr;
}

/**
 * @brief Modifizierte Friedmann-Gleichung mit GTT-Korrekturen
 * 
 * H² = (8πG(χ)/3)ρ - K/a² + Λ(χ)/3 + Q(a,D)/3
 */
int gtt_friedmann_equation(double a, double* H, void* params) {
    cosmology_params* cosmo = ((void**)params)[0];
    gtt_params* gtt = ((void**)params)[1];
    
    if (a <= 0.0) return _FAILURE_;
    
    /* Renormierungsskala */
    double chi = log(a);
    
    /* Skalenabhängige Kopplungen */
    double G_chi = gtt_G_of_chi(chi, gtt);
    double Lambda_chi = gtt_Lambda_of_chi(chi, gtt);
    double D = gtt_fractal_dimension(chi, gtt);
    
    /* Energiedichte */
    double rho = rho_total(a, cosmo, gtt);
    
    /* Krümmung */
    double K = 0.0;  /* Flaches Universum */
    
    /* Quantengeometrie-Term */
    double Q = gtt_Q_term(a, D, gtt);
    
    /* Friedmann-Gleichung */
    double H_squared = (8.0 * M_PI * G_chi / 3.0) * rho 
                     - K / (a * a) 
                     + Lambda_chi / 3.0 
                     + Q / 3.0;
    
    if (H_squared < 0.0) {
        fprintf(stderr, "Warning: H² < 0 at a = %e\n", a);
        return _FAILURE_;
    }
    
    *H = sqrt(H_squared);
    return _SUCCESS_;
}

/**
 * @brief Beschleunigungsgleichung
 * 
 * ä/a = -(4πG(χ)/3)(ρ + 3p) + Λ(χ)/3 + Q_accel
 */
double gtt_acceleration_equation(double a, const cosmology_params* cosmo, 
                                 const gtt_params* gtt) {
    double chi = log(a);
    double G_chi = gtt_G_of_chi(chi, gtt);
    double Lambda_chi = gtt_Lambda_of_chi(chi, gtt);
    double D = gtt_fractal_dimension(chi, gtt);
    
    /* Energiedichte und Druck */
    double rho = rho_total(a, cosmo, gtt);
    double p = rho / 3.0;  /* Strahlungsdominiert p = ρ/3 */
    
    /* Quantengeometrie-Beschleunigung */
    double Q_accel = gtt_Q_term(a, D, gtt) * (D - 2.0) / 3.0;
    
    double a_ddot_over_a = -(4.0 * M_PI * G_chi / 3.0) * (rho + 3.0 * p)
                          + Lambda_chi / 3.0
                          + Q_accel;
    
    return a_ddot_over_a;
}

/**
 * @brief Berechnet Hubble-Parameter H(z) für Rotverschiebung z
 */
double gtt_hubble_at_z(double z, const cosmology_params* cosmo, 
                       const gtt_params* gtt) {
    double a = 1.0 / (1.0 + z);
    double H;
    void* params[2] = {(void*)cosmo, (void*)gtt};
    
    if (gtt_friedmann_equation(a, &H, params) != _SUCCESS_) {
        return -1.0;
    }
    
    return H;
}

/**
 * @brief Berechnet Entfernungsmodul μ(z)
 */
double gtt_distance_modulus(double z, const cosmology_params* cosmo,
                            const gtt_params* gtt) {
    /* Luminositätsdistanz durch Integration */
    double c = 299792458.0;  /* m/s */
    double H0 = cosmo->h * 100.0 * 1000.0 / 3.08567758e22;  /* s^-1 */
    
    /* Numerische Integration von 0 bis z */
    int n_steps = 100;
    double dz = z / n_steps;
    double integral = 0.0;
    
    for (int i = 0; i < n_steps; i++) {
        double z_i = (i + 0.5) * dz;
        double H_z = gtt_hubble_at_z(z_i, cosmo, gtt);
        if (H_z < 0) return -1.0;
        integral += dz / H_z;
    }
    
    double d_L = c * (1.0 + z) * integral;  /* Luminositätsdistanz [m] */
    double d_L_Mpc = d_L / 3.08567758e22;   /* [Mpc] */
    
    /* Entfernungsmodul */
    double mu = 5.0 * log10(d_L_Mpc) + 25.0;
    
    return mu;
}

/**
 * @brief Löst Hubble-Spannung durch skalenabhängige Gravitation
 * 
 * Extrahiert H0 aus frühen (CMB) und späten (SNe Ia) Zeiten
 */
void gtt_resolve_hubble_tension(const cosmology_params* cosmo,
                                const gtt_params* gtt,
                                double* H0_early, double* H0_late) {
    /* Frühe Zeit (z ~ 1100, CMB) */
    double z_cmb = 1100.0;
    double H_cmb = gtt_hubble_at_z(z_cmb, cosmo, gtt);
    
    /* Extrapolation zu z=0 mit früher Physik */
    double chi_cmb = log(1.0 / (1.0 + z_cmb));
    double G_cmb = gtt_G_of_chi(chi_cmb, gtt);
    
    *H0_early = H_cmb * sqrt(G_cmb / gtt_G_of_chi(0.0, gtt));
    
    /* Späte Zeit (z ~ 0.1, SNe Ia) */
    double z_late = 0.1;
    double H_late = gtt_hubble_at_z(z_late, cosmo, gtt);
    
    /* Extrapolation zu z=0 mit später Physik */
    double chi_late = log(1.0 / (1.0 + z_late));
    double G_late = gtt_G_of_chi(chi_late, gtt);
    
    *H0_late = H_late * sqrt(G_late / gtt_G_of_chi(0.0, gtt));
    
    /* Konversion zu km/s/Mpc */
    *H0_early *= 3.08567758e22 / 1000.0;
    *H0_late *= 3.08567758e22 / 1000.0;
}

/**
 * @brief Berechnet Alter des Universums
 */
double gtt_age_of_universe(const cosmology_params* cosmo, const gtt_params* gtt) {
    /* Integration von t = ∫ da/(a*H(a)) von 0 bis 1 */
    int n_steps = 1000;
    double da = 1.0 / n_steps;
    double age = 0.0;
    
    for (int i = 1; i <= n_steps; i++) {
        double a = i * da;
        double H;
        void* params[2] = {(void*)cosmo, (void*)gtt};
        
        if (gtt_friedmann_equation(a, &H, params) == _SUCCESS_) {
            age += da / (a * H);
        }
    }
    
    /* Konversion zu Jahren */
    double age_seconds = age;
    double age_years = age_seconds / (365.25 * 24.0 * 3600.0);
    
    return age_years;
}

/**
 * @brief Test-Funktion für Hintergrundevolution
 */
void gtt_background_test() {
    printf("=== GTT Background Evolution Test ===\n\n");
    
    /* Parameter initialisieren */
    cosmology_params cosmo = {
        .h = 0.674,
        .Omega_b = 0.0493,
        .Omega_cdm = 0.264,
        .Omega_lambda = 0.6847,
        .Omega_k = 0.0,
        .T_cmb = 2.7255,
        .N_eff = 3.046
    };
    
    gtt_params gtt;
    gtt_params_init(&gtt);
    
    /* Hubble-Parameter bei verschiedenen z */
    printf("Hubble-Parameter H(z):\n");
    double z_values[] = {0.0, 0.5, 1.0, 2.0, 5.0, 10.0, 1100.0};
    for (int i = 0; i < 7; i++) {
        double H_z = gtt_hubble_at_z(z_values[i], &cosmo, &gtt);
        double H_z_kmsMpc = H_z * 3.08567758e22 / 1000.0;
        printf("  z = %.1f: H = %.2f km/s/Mpc\n", z_values[i], H_z_kmsMpc);
    }
    
    /* Hubble-Spannung */
    printf("\nHubble-Spannung:\n");
    double H0_early, H0_late;
    gtt_resolve_hubble_tension(&cosmo, &gtt, &H0_early, &H0_late);
    printf("  H0 (früh, CMB):  %.2f km/s/Mpc\n", H0_early);
    printf("  H0 (spät, SNe):  %.2f km/s/Mpc\n", H0_late);
    printf("  Spannung: %.1f%%\n", 
           100.0 * fabs(H0_late - H0_early) / H0_early);
    
    /* Alter des Universums */
    double age = gtt_age_of_universe(&cosmo, &gtt);
    printf("\nAlter des Universums: %.2f Mrd. Jahre\n", age / 1e9);
    
    printf("\n=== Test abgeschlossen ===\n");
}

/* Main-Funktion für Standalone-Test */
#ifdef GTT_BACKGROUND_MAIN
int main() {
    gtt_background_test();
    return 0;
}
#endif
