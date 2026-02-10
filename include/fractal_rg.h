/**
 * @file fractal_rg.h
 * @brief Renormierungsgruppen-Fluss für SDGFT
 * @author GTT Theory Group
 * 
 * Implementiert die RG-Gleichungen für die skalenabhängige
 * Gravitationskonstante, fraktale Dimension und Materie-Kopplungen.
 */

#ifndef FRACTAL_RG_H
#define FRACTAL_RG_H

#include "gtt_geometry.h"

/**
 * @struct rg_state
 * @brief Zustandsvektor für RG-Fluss
 */
typedef struct {
    double G;              /* Gravitationskonstante */
    double D;              /* Fraktale Dimension */
    double Lambda;         /* Kosmologische Konstante */
    double g_gauge[3];     /* Eichkopplungen (SU(3)×SU(2)×U(1)) */
    double y_yukawa[3];    /* Yukawa-Kopplungen (t,b,τ) */
} rg_state;

/**
 * @brief Initialisiert RG-Zustand bei Planck-Skala
 * 
 * @param state RG-Zustandsvektor
 * @param p GTT-Parameter
 */
void rg_init_planck(rg_state* state, const gtt_params* p);

/**
 * @brief Berechnet β-Funktion für Gravitationskonstante
 * 
 * β_G = dG/dχ = (D-3)G + (2/3π)G² + (β/24)G³
 * 
 * @param state Aktueller RG-Zustand
 * @param p GTT-Parameter
 * @return β_G
 */
double rg_beta_G(const rg_state* state, const gtt_params* p);

/**
 * @brief Berechnet β-Funktion für fraktale Dimension
 * 
 * β_D = dD/dχ = -(3-D)²/(4π) + (1/24)exp(-χ/χ_P)
 * 
 * @param state Aktueller RG-Zustand
 * @param chi Renormierungsskala
 * @param p GTT-Parameter
 * @return β_D
 */
double rg_beta_D(const rg_state* state, double chi, const gtt_params* p);

/**
 * @brief Berechnet β-Funktion für kosmologische Konstante
 * 
 * @param state Aktueller RG-Zustand
 * @param p GTT-Parameter
 * @return β_Λ
 */
double rg_beta_Lambda(const rg_state* state, const gtt_params* p);

/**
 * @brief Berechnet β-Funktionen für Eichkopplungen
 * 
 * β_g_i = β_i^SM(g_j) + (D-3)g_i + (β/8π²)g_i³
 * 
 * @param state Aktueller RG-Zustand
 * @param beta_out Array für β-Funktionen [3]
 * @param p GTT-Parameter
 */
void rg_beta_gauge(const rg_state* state, double beta_out[3], const gtt_params* p);

/**
 * @brief Integriert RG-Gleichungen von chi_start zu chi_end
 * 
 * Verwendet Runge-Kutta 4. Ordnung
 * 
 * @param state_in Anfangszustand
 * @param state_out Endzustand
 * @param chi_start Startwert der Skala
 * @param chi_end Endwert der Skala
 * @param p GTT-Parameter
 * @return 0 bei Erfolg, -1 bei Fehler
 */
int rg_integrate(const rg_state* state_in, rg_state* state_out,
                 double chi_start, double chi_end, const gtt_params* p);

/**
 * @brief Berechnet RG-Fluss für gesamten Skalenbereich
 * 
 * Von Planck-Skala bis zu kosmologischen Skalen
 * 
 * @param chi_array Array von Skalen
 * @param n_points Anzahl der Punkte
 * @param states_out Array von RG-Zuständen
 * @param p GTT-Parameter
 * @return 0 bei Erfolg
 */
int rg_flow_full(const double* chi_array, int n_points,
                 rg_state* states_out, const gtt_params* p);

/**
 * @brief Findet Fixed Points des RG-Flusses
 * 
 * @param chi_fixed Fixed-Point-Skala (Output)
 * @param state_fixed Fixed-Point-Zustand (Output)
 * @param p GTT-Parameter
 * @return Anzahl gefundener Fixed Points
 */
int rg_find_fixed_points(double* chi_fixed, rg_state* state_fixed,
                         const gtt_params* p);

#endif /* FRACTAL_RG_H */
