/**
 * @file gtt_geometry.h
 * @brief GTT 6-Konus-Geometrie und fraktale Dimension
 * @author GTT Theory Group
 * 
 * Implementiert die geometrischen Korrekturen der Scale-Dependent
 * Geometric Field Theory basierend auf der 6-Konus-Topologie.
 */

#ifndef GTT_GEOMETRY_H
#define GTT_GEOMETRY_H

#include <math.h>
#include <complex.h>

/* Fundamentale Konstanten */
#define GTT_THETA_MAX 30.0          /* Maximaler Konuswinkel in Grad */
#define GTT_D_ASYMPTOTIC 2.7916667  /* Asymptotische fraktale Dimension */
#define GTT_XI_G 0.004              /* Chiraler CP-Verletzungsfaktor */
#define GTT_BETA_EMERGENZ 0.1       /* Emergenz-Stärke */
#define GTT_ALPHA_ENTFALTUNG 1.0    /* Entfaltungs-Parameter */
#define GTT_BETA_ISO 0.028          /* Isokurvatur-Amplitude */

/* Planck-Skala */
#define M_PLANCK 1.220910e19        /* GeV */
#define L_PLANCK 1.616255e-35       /* m */
#define T_PLANCK 5.391247e-44       /* s */

/**
 * @struct gtt_params
 * @brief Parameter-Struktur für GTT-Berechnungen
 */
typedef struct {
    double theta_max;      /* Konuswinkel [Grad] */
    double D_asymptotic;   /* Asymptotische Dimension */
    double xi_G;           /* CP-Verletzung */
    double beta;           /* Emergenz-Stärke */
    double alpha;          /* Entfaltungs-Parameter */
    double chi;            /* Renormierungsskala ln(k/k0) */
    double chi_P;          /* Planck-Skala */
    double beta_iso;       /* Isokurvatur-Amplitude */
} gtt_params;

/**
 * @brief Initialisiert GTT-Parameter mit Standardwerten
 */
void gtt_params_init(gtt_params* p);

/**
 * @brief Berechnet skalenabhängige fraktale Dimension D(χ)
 * 
 * D(χ) = D_∞ - (D_∞ - 2) * exp(-χ/χ_P)
 * 
 * @param chi Renormierungsskala ln(k/k0)
 * @param p GTT-Parameter
 * @return Fraktale Dimension
 */
double gtt_fractal_dimension(double chi, const gtt_params* p);

/**
 * @brief Berechnet skalenabhängige Gravitationskonstante G(χ)
 * 
 * Löst die RG-Gleichung:
 * dG/dχ = (D-3)G + (2/3π)G² + (β/24)G³
 * 
 * @param chi Renormierungsskala
 * @param p GTT-Parameter
 * @return G(χ) in natürlichen Einheiten
 */
double gtt_G_of_chi(double chi, const gtt_params* p);

/**
 * @brief Berechnet skalenabhängige kosmologische Konstante Λ(χ)
 * 
 * @param chi Renormierungsskala
 * @param p GTT-Parameter
 * @return Λ(χ) in natürlichen Einheiten
 */
double gtt_Lambda_of_chi(double chi, const gtt_params* p);

/**
 * @brief Berechnet Quantengeometrie-Tensor Q_μν
 * 
 * Q_μν = ξ_G R R̃ g_μν + (β/4π)θ_max² C_μν + α F_μν
 * 
 * @param a Skalenfaktor
 * @param D Fraktale Dimension
 * @param p GTT-Parameter
 * @return Spur von Q_μν
 */
double gtt_Q_term(double a, double D, const gtt_params* p);

/**
 * @brief Berechnet Konus-Krümmungstensor-Beitrag
 * 
 * @param theta_max Maximaler Konuswinkel
 * @param a Skalenfaktor
 * @return C_μν Beitrag
 */
double gtt_cone_curvature(double theta_max, double a);

/**
 * @brief Berechnet konforme Faktor-Korrektur φ = ln√(-g)
 * 
 * @param a Skalenfaktor
 * @param D Fraktale Dimension
 * @return Konformer Faktor
 */
double gtt_conformal_factor(double a, double D);

/**
 * @brief Berechnet Isokurvatur-Korrektur für primordiale Spektren
 * 
 * @param k Wellenzahl [Mpc^-1]
 * @param p GTT-Parameter
 * @return Isokurvatur-Korrekturfaktor
 */
double gtt_isocurvature_correction(double k, const gtt_params* p);

/**
 * @brief Berechnet spektralen Index n_s(k) mit skalenabhängiger Korrektur
 * 
 * n_s(k) = n_s0 - 0.014 * (D(k) - D_∞)
 * 
 * @param k Wellenzahl
 * @param n_s0 Basis-spektraler Index
 * @param p GTT-Parameter
 * @return Skalenabhängiger spektraler Index
 */
double gtt_spectral_index(double k, double n_s0, const gtt_params* p);

/**
 * @brief Berechnet Tensor-zu-Skalar-Verhältnis r
 * 
 * GTT-Vorhersage: r ≈ 0.001 - 0.003
 * 
 * @param p GTT-Parameter
 * @return Tensor-zu-Skalar-Verhältnis
 */
double gtt_tensor_to_scalar_ratio(const gtt_params* p);

/**
 * @brief Berechnet effektive Neutrino-Masse für 0νββ
 * 
 * GTT-Vorhersage: ⟨m_ββ⟩ = 15 ± 3 meV
 * 
 * @param p GTT-Parameter
 * @return Effektive Majorana-Masse [eV]
 */
double gtt_effective_neutrino_mass(const gtt_params* p);

/**
 * @brief Berechnet Baryon-Asymmetrie aus CP-Verletzung
 * 
 * η_B = (n_B - n_B̄)/n_γ ≈ 6.1 × 10^-10
 * 
 * @param p GTT-Parameter
 * @return Baryon-zu-Photon-Verhältnis
 */
double gtt_baryon_asymmetry(const gtt_params* p);

#endif /* GTT_GEOMETRY_H */
