import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, ConnectionPatch
import numpy as np

# Ustawienia A4 (w calach)
A4_WIDTH = 8.27
A4_HEIGHT = 11.69
DPI = 300  # Wysoka rozdzielczość dla Word

fig, ax = plt.subplots(figsize=(A4_WIDTH, A4_HEIGHT), dpi=DPI)
ax.set_xlim(0, 10)
ax.set_ylim(0, 14)
ax.axis('off')

# Kolory
color_user = '#4A90E2'  # Niebieski
color_reg = '#5CB85C'  # Zielony
color_security = '#F39C12'  # Pomarańczowy
color_auth = '#9B59B6'  # Fioletowy
color_routing = '#E74C3C'  # Czerwony
color_user_path = '#3498DB'  # Jasny niebieski
color_admin_path = '#E67E22'  # Ciemny pomarańczowy
color_data = '#16A085'  # Turkusowy
color_dashboard = '#8E44AD'  # Purpurowy

# Funkcja do tworzenia zaokrąglonych prostokątów
def create_box(x, y, width, height, text, color, text_color='white', fontsize=10, bold=False):
    box = FancyBboxPatch((x - width/2, y - height/2), width, height,
                        boxstyle="round,pad=0.1", 
                        facecolor=color, edgecolor='black', linewidth=2)
    ax.add_patch(box)
    weight = 'bold' if bold else 'normal'
    ax.text(x, y, text, ha='center', va='center', 
           color=text_color, fontsize=fontsize, weight=weight, 
           wrap=True, family='Arial')

# Funkcja do tworzenia strzałek
def create_arrow(x1, y1, x2, y2, color='black', linewidth=2):
    arrow = FancyArrowPatch((x1, y1), (x2, y2),
                           arrowstyle='->', mutation_scale=20,
                           color=color, linewidth=linewidth, zorder=1)
    ax.add_patch(arrow)

# Pozycje (od góry do dołu)
y_positions = [13, 11.5, 9.5, 7.5, 5.5, 4, 2.5, 1]

# 1. User
create_box(5, y_positions[0], 2, 0.8, 'User', color_user, fontsize=14, bold=True)
create_arrow(5, y_positions[0] - 0.4, 5, y_positions[1] + 0.4, color_user, 2.5)

# 2. Registration/Login
create_box(5, y_positions[1], 3, 0.8, 'Registration/Login', color_reg, fontsize=12, bold=True)
create_arrow(5, y_positions[1] - 0.4, 5, y_positions[2] + 0.4, color_reg, 2.5)

# 3. Security Layer
create_box(5, y_positions[2], 4, 1.5, 'Security Layer', color_security, fontsize=12, bold=True)
# Elementy Security Layer
security_items = [
    'Password Hashing',
    'License Key Verification',
    'Recovery Code Validation',
    'Login Attempt Control'
]
for i, item in enumerate(security_items):
    y_item = y_positions[2] - 0.3 + i * 0.3
    ax.text(5, y_item, f'• {item}', ha='center', va='center',
           color='white', fontsize=9, weight='normal', family='Arial')
create_arrow(5, y_positions[2] - 0.75, 5, y_positions[3] + 0.4, color_security, 2.5)

# 4. Authentication & Role Assignment
create_box(5, y_positions[3], 4, 0.8, 'Authentication\n& Role Assignment', color_auth, fontsize=12, bold=True)
create_arrow(5, y_positions[3] - 0.4, 5, y_positions[4] + 0.4, color_auth, 2.5)

# 5. Role-Based Routing
create_box(5, y_positions[4], 3.5, 0.8, 'Role-Based Routing', color_routing, fontsize=12, bold=True)

# 6. Rozgałęzienie - Standard User Path i Admin Path
# Standard User Path (lewo)
create_arrow(5, y_positions[4] - 0.4, 2.5, y_positions[5] + 0.4, color_user_path, 2.5)
create_box(2.5, y_positions[5], 3, 0.8, 'Standard User Path', color_user_path, fontsize=11, bold=True)
create_arrow(2.5, y_positions[5] - 0.4, 2.5, y_positions[6] + 0.4, color_user_path, 2.5)

# Admin Path (prawo)
create_arrow(5, y_positions[4] - 0.4, 7.5, y_positions[5] + 0.4, color_admin_path, 2.5)
create_box(7.5, y_positions[5], 3, 0.8, 'Admin Path', color_admin_path, fontsize=11, bold=True)
create_arrow(7.5, y_positions[5] - 0.4, 7.5, y_positions[6] + 0.4, color_admin_path, 2.5)

# 7. User-Accessible Data / Full System Data
create_box(2.5, y_positions[6], 3.5, 1.2, 'User-Accessible Data\n• Analytics Tables\n• Visualisation Data', 
          color_data, fontsize=10, bold=False)
create_box(7.5, y_positions[6], 3.5, 1.2, 'Full System Data\n• All Analytics Data\n• User Accounts\n• Security Logs', 
          color_data, fontsize=10, bold=False)

create_arrow(2.5, y_positions[6] - 0.6, 2.5, y_positions[7] + 0.4, color_dashboard, 2.5)
create_arrow(7.5, y_positions[6] - 0.6, 7.5, y_positions[7] + 0.4, color_dashboard, 2.5)

# 8. User Dashboards / Admin Dashboards
create_box(2.5, y_positions[7], 3.5, 1, 'User Dashboards\n• Charts & Tables', 
          color_dashboard, fontsize=10, bold=True)
create_box(7.5, y_positions[7], 3.5, 1, 'Admin Dashboards\n• Charts & Tables\n• User Management', 
          color_dashboard, fontsize=10, bold=True)

# Tytuł
ax.text(5, 13.8, 'System Authentication & Role-Based Access Control Flow', 
       ha='center', va='center', fontsize=16, weight='bold', 
       family='Arial', color='#2C3E50')

# Zapisz jako PNG (wysoka jakość)
plt.tight_layout()
plt.savefig('authentication_diagram.png', dpi=DPI, bbox_inches='tight', 
           facecolor='white', edgecolor='none')
print("Diagram został zapisany jako 'authentication_diagram.png'")
print("Rozmiar: A4, rozdzielczość: 300 DPI - gotowe do wklejenia do Word")

# Opcjonalnie zapisz jako PDF (lepsze dla Word)
plt.savefig('authentication_diagram.pdf', bbox_inches='tight', 
           facecolor='white', edgecolor='none')
print("Diagram został również zapisany jako 'authentication_diagram.pdf'")

plt.close()

