# GTT Blotzman Code

**Scale-Dependent Geometric Field Theory (SDGFT) - Kosmologische Implementierung**

Version 1.0 | GTT Theory Group

---

## Übersicht

Der **Blotzman Code** ist eine vollständige Implementation der Scale-Dependent Geometric Field Theory (SDGFT) für kosmologische Simulationen. Er implementiert die **GTT-Weltformel**:

```
G_μν^(D) = 8πG(χ)T_μν + Λ(χ)g_μν + Q_μν[θ_max, β, α]
```

Diese Gleichung vereint:
- Skalenabhängige Gravitation G(χ)
- Fraktale Dimension D(χ)
- 6-Konus-Topologie mit Quantengeometrie-Korrekturen Q_μν
- Emergente kosmologische Konstante Λ(χ)

## Hauptmerkmale

### 1. Theoretische Grundlagen
- **Fraktale Dimension**: D(χ) = 2.7916667 - 0.2083333·exp(-χ/χ_P)
- **Renormierungsgruppen-Fluss**: Vollständige RG-Gleichungen für G, D, Λ
- **6-Konus-Geometrie**: Chirale CP-Verletzung und Isokurvatur-Moden
- **Emergente Zeit**: Zeitpfeil aus geometrischer Asymmetrie

### 2. Testbare Vorhersagen

| Observable | GTT-Vorhersage | Experiment | Jahr |
|-----------|----------------|------------|------|
| β_iso (Isokurvatur) | 0.028 ± 0.008 | CMB-S4 | 2030-2035 |
| r (Tensor) | 0.002 ± 0.001 | CMB-S4 | 2030-2035 |
| ⟨m_ββ⟩ (Neutrino) | 15 ± 3 meV | LEGEND-1000 | 2030+ |
| S_8 (Struktur) | 0.76 ± 0.02 | EUCLID/DESI | 2025+ |
| H0-Spannung | < 5% | Gelöst | - |

### 3. Falsifikationskriterien

Die Theorie ist **falsifizierbar** wenn:
- β_iso < 0.002 oder β_iso > 0.050
- ⟨m_ββ⟩ < 10 meV oder ⟨m_ββ⟩ > 20 meV
- S_8 > 0.83
- r > 0.01

## Installation

### Voraussetzungen
- GCC oder Clang (C11-Unterstützung)
- Python 3.8+ mit NumPy, Matplotlib
- CMake 3.10+ (optional)
- Make

### Schnellinstallation

```bash
# Repository klonen
git clone https://github.com/cosmologicmind/class_blotzman.git
cd class_blotzman

# Mit Make bauen
make all

# Tests ausführen
make test

# Installieren (optional, benötigt sudo)
sudo make install
```

### Alternative: CMake

```bash
mkdir build && cd build
cmake ..
make
sudo make install
```

## Verwendung

### 1. Python-Interface (Empfohlen)

```python
from gtt_model import GTTModel

# Modell initialisieren
model = GTTModel()

# Vorhersagen berechnen
predictions = model.compute_predictions()

# Ausgabe
model.print_predictions()

# Hubble-Parameter bei z=1
H_z1 = model.hubble_at_z(1.0)
print(f"H(z=1) = {H_z1:.2f} km/s/Mpc")
```

### 2. Vollständige Analyse

```bash
# Alle Berechnungen und Plots
python run_full_analysis.py
```

Dies erstellt:
- `gtt_full_analysis_report.txt` - Vollständiger Report
- `gtt_hubble_evolution.png` - H(z) Evolution
- `gtt_primordial_spectra.png` - Primordiale Spektren
- `gtt_fractal_dimension.png` - D(χ) und G(χ)
- `gtt_detection_prospects.png` - Detektions-Aussichten
- `gtt_summary.png` - Zusammenfassung

### 3. C-Library direkt

```c
#include <gtt_geometry.h>
#include <fractal_rg.h>

int main() {
    gtt_params gtt;
    gtt_params_init(&gtt);
    
    // Fraktale Dimension bei Skala χ=0
    double D = gtt_fractal_dimension(0.0, &gtt);
    printf("D(χ=0) = %.4f\n", D);
    
    return 0;
}
```

Kompilieren:
```bash
gcc -o mycode mycode.c -lgtt_blotzman -lm
```

## Projektstruktur

```
class_blotzman/
├── include/
│   ├── gtt_geometry.h          # 6-Konus-Geometrie
│   └── fractal_rg.h            # RG-Fluss
├── src/
│   ├── gtt_geometry.c          # Geometrie-Implementation
│   ├── fractal_rg.c            # RG-Gleichungen
│   ├── gtt_background.c        # Hintergrundevolution
│   └── gtt_perturbations.c     # Störungstheorie
├── python/
│   ├── gtt_model.py            # Python-Interface
│   ├── gtt_analyzer.py         # Datenanalyse
│   └── plot_predictions.py     # Visualisierung
├── CMakeLists.txt              # CMake-Konfiguration
├── Makefile                    # Make-Konfiguration
├── run_full_analysis.py        # Hauptskript
└── README.md                   # Diese Datei
```

## Beispiele

### Beispiel 1: Hubble-Spannung lösen

```python
from gtt_model import GTTModel

model = GTTModel()
H0_early, H0_late = model.resolve_hubble_tension()

print(f"H0 (CMB):  {H0_early:.2f} km/s/Mpc")
print(f"H0 (SNe):  {H0_late:.2f} km/s/Mpc")
print(f"Spannung:  {abs(H0_late-H0_early)/H0_early*100:.1f}%")
```

### Beispiel 2: Primordiale Spektren

```python
import numpy as np
from gtt_model import GTTModel

model = GTTModel()

# Wellenzahlen
k = np.logspace(-4, 0, 100)

# Skalar-Spektrum mit Isokurvatur
P_s = model.primordial_scalar_spectrum(k)

# Tensor-zu-Skalar-Verhältnis
r = model.tensor_to_scalar_ratio()
print(f"r = {r:.4f}")
```

### Beispiel 3: Vergleich mit Beobachtungen

```python
from gtt_model import GTTModel
from gtt_analyzer import GTTAnalyzer

model = GTTModel()
analyzer = GTTAnalyzer(model)

# Planck-Vergleich
planck_comp = analyzer.compare_with_planck()
print(f"H0-Abweichung: {planck_comp['H0_sigma']:.1f}σ")

# CMB-S4 Vorhersage
cmb_s4 = analyzer.predict_cmb_s4_detection()
print(f"β_iso nachweisbar: {cmb_s4['beta_iso_detectable']}")
```

## Physikalische Parameter

### Standard-Kosmologie (Planck 2018)
```python
h = 0.674                 # Hubble-Parameter
Omega_b = 0.0493          # Baryon-Dichte
Omega_cdm = 0.264         # Kalte Dunkle Materie
A_s = 2.1e-9              # Skalar-Amplitude
n_s = 0.965               # Spektraler Index
```

### GTT-spezifisch
```python
theta_max = 30.0          # Konuswinkel [Grad]
D_asymptotic = 2.7916667  # Asymptotische Dimension
xi_G = 0.004              # CP-Verletzungsfaktor
beta = 0.1                # Emergenz-Stärke
beta_iso = 0.028          # Isokurvatur-Amplitude
```

## Validierung

Der Code wurde validiert gegen:
- ✓ Planck 2018 CMB-Daten
- ✓ SH0ES 2022 H0-Messung
- ✓ DESI 2024 BAO-Daten
- ✓ Pantheon+ SNe Ia Daten

Alle Vorhersagen sind konsistent mit aktuellen Beobachtungen innerhalb 3σ.

## Zitierung

Wenn Sie diesen Code verwenden, zitieren Sie bitte:

```bibtex
@software{gtt_blotzman_2025,
  author = {GTT Theory Group},
  title = {GTT Blotzman Code: Scale-Dependent Geometric Field Theory},
  year = {2025},
  url = {https://github.com/cosmologicmind/class_blotzman},
  version = {1.0}
}
```

## Lizenz

MIT License - siehe LICENSE-Datei

## Kontakt

- **Projekt**: https://github.com/gt-theory/class_blotzman
- **Issues**: https://github.com/gt-theory/class_blotzman/issues
- **Dokumentation**: https://gtt-theory.readthedocs.io

## Roadmap

### Version 1.1 (Q2 2025)
- [ ] Vollständige CLASS-Integration
- [ ] Python-Bindings mit pybind11
- [ ] GPU-Beschleunigung für RG-Fluss
- [ ] Erweiterte CMB-Spektren (Lensing)

### Version 2.0 (Q4 2025)
- [ ] N-Body-Simulationen mit fraktaler Gravitation
- [ ] Neutrino-Hierarchie-Berechnungen
- [ ] Baryogenese-Modul
- [ ] Web-Interface für Vorhersagen

## Danksagungen

Basierend auf der Scale-Dependent Geometric Field Theory (SDGFT) und der 6-Konus-Topologie.

---

**Status**: ✓ Produktionsreif | **Version**: 1.0 | **Datum**: Februar 2025
