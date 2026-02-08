# Bachelorarbeit

Dieses Repository enthält den im Rahmen einer Bachelorarbeit generierten und analysierten Code. Die Arbeit untersucht die automatisierte Code Generierung und -Optimierung durch KI Systeme anhand verschiedener Komplexitätsstufen (einfach, mittel, komplex).

Alle Code Beispiele wurden systematisch generiert, getestet und optimiert, um die Leistungsfähigkeit und Grenzen von KI gestützter Softwareentwicklung zu evaluieren.

---

## Tests ausführen

### Voraussetzungen

```bash
pip install -r requirements.txt
```

### Unit Tests

**Original-Tests (einfach, mittel, komplex, travel_planner):**

```bash
python -m pytest einfach/ mittel/ komplex/ travel_planner/tests/ -v
```

**Optimierte Tests (mittel_optimiert, travel_planner_optimiert):**

```bash
python -m pytest mittel_optimiert/ travel_planner_optimiert/tests/ -v
```

---

### Code-Qualitäts-Tools

```bash
# Linting mit pylint
pylint einfach/ mittel/ komplex/ travel_planner/

# Code-Formatierung prüfen mit black
black --check einfach/ mittel/ komplex/ travel_planner/

# Flake8 Style-Check
flake8 einfach/ mittel/ komplex/ travel_planner/

# Zyklomatische Komplexität mit radon
radon cc einfach/ mittel/ komplex/ travel_planner/ -a
radon mi einfach/ mittel/ komplex/ travel_planner/

# Sicherheitsanalyse mit bandit
bandit -r einfach/ mittel/ komplex/ travel_planner/

# Type-Checking mit mypy
mypy einfach/ mittel/ komplex/ travel_planner/
```

