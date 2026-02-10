/**
 * @file fractal_rg.c
 * @brief Implementation der RG-Fluss-Gleichungen
 */

#include "../include/fractal_rg.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Standard Model β-Funktionen (1-Loop) */
static double beta_g3_SM(double g3) {
    return -7.0 * pow(g3, 3) / (16.0 * M_PI * M_PI);
}

static double beta_g2_SM(double g2) {
    return -19.0 / 6.0 * pow(g2, 3) / (16.0 * M_PI * M_PI);
}

static double beta_g1_SM(double g1) {
    return 41.0 / 10.0 * pow(g1, 3) / (16.0 * M_PI * M_PI);
}

void rg_init_planck(rg_state* state, const gtt_params* p) {
    /* Anfangsbedingungen bei Planck-Skala */
    state->G = 1.0;  /* In Planck-Einheiten */
    state->D = 2.0;  /* Beginnt bei topologischer Dimension */
    state->Lambda = 0.0;  /* Emergent bei niedrigen Energien */
    
    /* GUT-Skala Eichkopplungen */
    state->g_gauge[0] = 0.7;   /* SU(3) */
    state->g_gauge[1] = 0.65;  /* SU(2) */
    state->g_gauge[2] = 0.35;  /* U(1) */
    
    /* Yukawa-Kopplungen */
    state->y_yukawa[0] = 1.0;   /* Top */
    state->y_yukawa[1] = 0.02;  /* Bottom */
    state->y_yukawa[2] = 0.01;  /* Tau */
}

double rg_beta_G(const rg_state* state, const gtt_params* p) {
    /* β_G = (D-3)G + (2/3π)G² + (β/24)G³ */
    double G = state->G;
    double D = state->D;
    
    double term1 = (D - 3.0) * G;
    double term2 = (2.0 / (3.0 * M_PI)) * G * G;
    double term3 = (p->beta / 24.0) * G * G * G;
    
    return term1 + term2 + term3;
}

double rg_beta_D(const rg_state* state, double chi, const gtt_params* p) {
    /* β_D = -(3-D)²/(4π) + (1/24)exp(-χ/χ_P) */
    double D = state->D;
    
    double term1 = -pow(3.0 - D, 2) / (4.0 * M_PI);
    double term2 = (1.0 / 24.0) * exp(-chi / p->chi_P);
    
    return term1 + term2;
}

double rg_beta_Lambda(const rg_state* state, const gtt_params* p) {
    /* β_Λ mit Quantenkorrekturen */
    double D = state->D;
    double G = state->G;
    
    /* Vakuumenergie-Beitrag */
    double vacuum_term = -(3.0 - D) * state->Lambda;
    
    /* Graviton-Loop-Korrektur */
    double graviton_loop = p->xi_G * G * G / (16.0 * M_PI * M_PI);
    
    return vacuum_term + graviton_loop;
}

void rg_beta_gauge(const rg_state* state, double beta_out[3], const gtt_params* p) {
    /* β_g_i = β_i^SM(g_j) + (D-3)g_i + (β/8π²)g_i³ */
    double D = state->D;
    
    for (int i = 0; i < 3; i++) {
        double g_i = state->g_gauge[i];
        
        /* Standard Model Beitrag */
        double beta_SM;
        if (i == 0) beta_SM = beta_g3_SM(g_i);
        else if (i == 1) beta_SM = beta_g2_SM(g_i);
        else beta_SM = beta_g1_SM(g_i);
        
        /* GTT-Korrekturen */
        double gtt_term1 = (D - 3.0) * g_i;
        double gtt_term2 = (p->beta / (8.0 * M_PI * M_PI)) * pow(g_i, 3);
        
        beta_out[i] = beta_SM + gtt_term1 + gtt_term2;
    }
}

/* Runge-Kutta 4. Ordnung Schritt */
static void rk4_step(rg_state* state, double chi, double h, const gtt_params* p) {
    rg_state k1, k2, k3, k4, temp;
    
    /* k1 */
    k1.G = rg_beta_G(state, p);
    k1.D = rg_beta_D(state, chi, p);
    k1.Lambda = rg_beta_Lambda(state, p);
    rg_beta_gauge(state, k1.g_gauge, p);
    
    /* k2 */
    temp = *state;
    temp.G += 0.5 * h * k1.G;
    temp.D += 0.5 * h * k1.D;
    temp.Lambda += 0.5 * h * k1.Lambda;
    for (int i = 0; i < 3; i++) temp.g_gauge[i] += 0.5 * h * k1.g_gauge[i];
    
    k2.G = rg_beta_G(&temp, p);
    k2.D = rg_beta_D(&temp, chi + 0.5*h, p);
    k2.Lambda = rg_beta_Lambda(&temp, p);
    rg_beta_gauge(&temp, k2.g_gauge, p);
    
    /* k3 */
    temp = *state;
    temp.G += 0.5 * h * k2.G;
    temp.D += 0.5 * h * k2.D;
    temp.Lambda += 0.5 * h * k2.Lambda;
    for (int i = 0; i < 3; i++) temp.g_gauge[i] += 0.5 * h * k2.g_gauge[i];
    
    k3.G = rg_beta_G(&temp, p);
    k3.D = rg_beta_D(&temp, chi + 0.5*h, p);
    k3.Lambda = rg_beta_Lambda(&temp, p);
    rg_beta_gauge(&temp, k3.g_gauge, p);
    
    /* k4 */
    temp = *state;
    temp.G += h * k3.G;
    temp.D += h * k3.D;
    temp.Lambda += h * k3.Lambda;
    for (int i = 0; i < 3; i++) temp.g_gauge[i] += h * k3.g_gauge[i];
    
    k4.G = rg_beta_G(&temp, p);
    k4.D = rg_beta_D(&temp, chi + h, p);
    k4.Lambda = rg_beta_Lambda(&temp, p);
    rg_beta_gauge(&temp, k4.g_gauge, p);
    
    /* Update */
    state->G += (h / 6.0) * (k1.G + 2*k2.G + 2*k3.G + k4.G);
    state->D += (h / 6.0) * (k1.D + 2*k2.D + 2*k3.D + k4.D);
    state->Lambda += (h / 6.0) * (k1.Lambda + 2*k2.Lambda + 2*k3.Lambda + k4.Lambda);
    
    for (int i = 0; i < 3; i++) {
        state->g_gauge[i] += (h / 6.0) * (k1.g_gauge[i] + 2*k2.g_gauge[i] + 
                                          2*k3.g_gauge[i] + k4.g_gauge[i]);
    }
}

int rg_integrate(const rg_state* state_in, rg_state* state_out,
                 double chi_start, double chi_end, const gtt_params* p) {
    *state_out = *state_in;
    
    int n_steps = 1000;
    double h = (chi_end - chi_start) / n_steps;
    
    for (int i = 0; i < n_steps; i++) {
        double chi = chi_start + i * h;
        rk4_step(state_out, chi, h, p);
    }
    
    return 0;
}

int rg_flow_full(const double* chi_array, int n_points,
                 rg_state* states_out, const gtt_params* p) {
    rg_state current_state;
    rg_init_planck(&current_state, p);
    
    states_out[0] = current_state;
    
    for (int i = 1; i < n_points; i++) {
        rg_integrate(&current_state, &states_out[i], 
                     chi_array[i-1], chi_array[i], p);
        current_state = states_out[i];
    }
    
    return 0;
}

int rg_find_fixed_points(double* chi_fixed, rg_state* state_fixed,
                         const gtt_params* p) {
    /* Suche nach Fixed Points: β_D = 0 */
    int n_fixed = 0;
    
    /* Analytische Lösung für D = 3 - sqrt(π/6) ≈ 2.28 */
    double D_fixed = 3.0 - sqrt(M_PI / 6.0);
    
    if (fabs(D_fixed - p->D_asymptotic) < 0.5) {
        chi_fixed[n_fixed] = p->chi_P / 2.0;
        state_fixed[n_fixed].D = D_fixed;
        state_fixed[n_fixed].G = 1.0;
        n_fixed++;
    }
    
    return n_fixed;
}
