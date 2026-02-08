import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

# Deutscher Stil für die Abbildungen
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

# Daten für Abbildung 1: Komplexitätsprogression (MI und CC)
kategorien = ['EINFACH', 'MITTEL', 'KOMPLEX']
mi_werte = [78.4, 74.2, 71.8]  # Maintainability Index
cc_werte = [3.2, 5.8, 7.4]     # Cyclomatic Complexity

# Abbildung 1: Komplexitätsprogression (Dual-Axis)
fig1, ax1 = plt.subplots(figsize=(10, 6))

x = np.arange(len(kategorien))
width = 0.35

# MI Balken (linke Y-Achse)
bars1 = ax1.bar(x - width/2, mi_werte, width, label='Maintainability Index (MI)',
                color='#2E86AB', edgecolor='black', linewidth=1.2)
ax1.set_xlabel('Aufgabenkategorie', fontsize=12, fontweight='bold')
ax1.set_ylabel('Maintainability Index (MI)', fontsize=11, color='#2E86AB')
ax1.tick_params(axis='y', labelcolor='#2E86AB')
ax1.set_ylim(60, 85)

# CC Balken (rechte Y-Achse)
ax2 = ax1.twinx()
bars2 = ax2.bar(x + width/2, cc_werte, width, label='Cyclomatic Complexity (CC)',
                color='#E94F37', edgecolor='black', linewidth=1.2)
ax2.set_ylabel('Cyclomatic Complexity (CC)', fontsize=11, color='#E94F37')
ax2.tick_params(axis='y', labelcolor='#E94F37')
ax2.set_ylim(0, 10)

# X-Achse Beschriftung
ax1.set_xticks(x)
ax1.set_xticklabels(kategorien, fontsize=11, fontweight='bold')

# Werte auf den Balken anzeigen
for bar, val in zip(bars1, mi_werte):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
             f'{val}', ha='center', va='bottom', fontsize=10, fontweight='bold')

for bar, val in zip(bars2, cc_werte):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
             f'{val}', ha='center', va='bottom', fontsize=10, fontweight='bold')

# Legende
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper center',
           bbox_to_anchor=(0.5, -0.12), ncol=2, fontsize=10)

plt.title('Abbildung 1: Komplexitätsprogression nach Aufgabenkategorie',
          fontsize=14, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig('c:/dev/projects/Bachelorarbeit/travel_planner/abb1_komplexitaet.png',
            dpi=300, bbox_inches='tight', facecolor='white')
plt.close()

# Abbildung 2: Design Patterns pro Aufgabe
patterns_werte = [0.2, 1.4, 3.3]

fig2, ax3 = plt.subplots(figsize=(10, 6))

colors = ['#4CAF50', '#FFC107', '#F44336']  # Grün, Gelb, Rot für steigenden Trend
bars3 = ax3.bar(kategorien, patterns_werte, color=colors,
                edgecolor='black', linewidth=1.5, width=0.6)

ax3.set_xlabel('Aufgabenkategorie', fontsize=12, fontweight='bold')
ax3.set_ylabel('Durchschnittliche Anzahl Design Patterns', fontsize=11)
ax3.set_ylim(0, 4.5)

# Werte auf den Balken anzeigen
for bar, val in zip(bars3, patterns_werte):
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
             f'{val}', ha='center', va='bottom', fontsize=12, fontweight='bold')

# Trendlinie hinzufügen
z = np.polyfit(range(len(kategorien)), patterns_werte, 1)
p = np.poly1d(z)
ax3.plot(range(len(kategorien)), p(range(len(kategorien))),
         linestyle='--', color='#333333', linewidth=2, label='Trend')

ax3.legend(loc='upper left', fontsize=10)
ax3.set_axisbelow(True)
ax3.yaxis.grid(True, linestyle='--', alpha=0.7)

plt.title('Abbildung 2: Design Patterns pro Aufgabe nach Kategorie',
          fontsize=14, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig('c:/dev/projects/Bachelorarbeit/travel_planner/abb2_design_patterns.png',
            dpi=300, bbox_inches='tight', facecolor='white')
plt.close()

print("\n" + "="*60)
print("Abbildungen erfolgreich erstellt und gespeichert:")
print("  - abb1_komplexitaet.png")
print("  - abb2_design_patterns.png")
print("="*60)
