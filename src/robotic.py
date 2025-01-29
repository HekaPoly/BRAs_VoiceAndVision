# ================================================================
# Code modulaire pour un bras robotique 3DDL
# Ecrit et vérifié par :
# Edgard Tambe, Delano Horn-Bourque, Charles Dupuis,
# Louis-Thomas Lapointe, Mathieu Massé
# Dernière révision : 10 octobre 2024
# ================================================================

import math

def is_reachable(base_height, arm1_length, arm2_length, target_position):
    """
    Vérifie si l'objet est atteignable.
    
    :param base_height: hauteur de la base
    :param arm1_length: longueur du premier bras
    :param arm2_length: longueur du deuxième bras
    :param target_position: position cible (x, y, z)
    :return: True si atteignable, sinon False
    """
    x, y, z = target_position
    # Distance projetée sur le plan XZ
    planar_distance = math.sqrt(x**2 + z**2)
    # Distance totale à la cible
    distance_to_target = math.sqrt(planar_distance**2 + y**2)
    
    return distance_to_target <= (arm1_length + arm2_length)

def calculate_angles(base_height, arm1_length, arm2_length, target_position):
    """
    Calcule les angles nécessaires pour atteindre un objet.

    :param base_height: hauteur de la base
    :param arm1_length: longueur du premier bras
    :param arm2_length: longueur du deuxième bras
    :param target_position: position cible (x, y, z)
    :return: angles pour la base, le bras 1 et le bras 2
    """
    x, y, z = target_position

    # Calcul de l'angle de rotation de la base
    theta_base = math.atan2(z, x)  # Rotation autour de l'axe Y

    # Position dans le plan 2D après alignement de la base
    planar_distance = math.sqrt(x**2 + z**2)
    target_2d_x = planar_distance
    target_2d_y = y

    # Loi des cosinus pour le bras 1 et le bras 2
    d = math.sqrt(target_2d_x**2 + target_2d_y**2)
    
    if d > (arm1_length + arm2_length):
        raise ValueError("L'objet est hors de portée.")

    # Calcul des angles
    angle1 = math.atan2(target_2d_y, target_2d_x)  # Angle entre l'horizontale et la cible
    cos_angle2 = (arm1_length**2 + d**2 - arm2_length**2) / (2 * arm1_length * d)
    angle2 = math.acos(cos_angle2)

    theta_arm1 = angle1 + angle2

    # Limite de l'angle pour éviter que le bras 1 frappe la base
    theta_arm1 = max(math.radians(-10), theta_arm1)  # Commentaire : limite provisoire à -10 degrés

    cos_angle3 = (arm1_length**2 + arm2_length**2 - d**2) / (2 * arm1_length * arm2_length)
    theta_arm2 = math.acos(cos_angle3)

    return math.degrees(theta_base), math.degrees(theta_arm1), math.degrees(theta_arm2)

def main():
    # Exemples de paramètres
    base_height = 10.0
    arm1_length = 15.0
    arm2_length = 15.0
    current_angles = (0.0, 0.0, 0.0)  # Angles initiaux (en degrés)
    target_position = (20.0, 5.0, 15.0)

    if not is_reachable(base_height, arm1_length, arm2_length, target_position):
        print("L'objet est hors de portée.")
    else:
        try:
            theta_base, theta_arm1, theta_arm2 = calculate_angles(base_height, arm1_length, arm2_length, target_position)
            print(f"Angles calculés : Base = {theta_base:.2f} degrés, Bras 1 = {theta_arm1:.2f} degrés, Bras 2 = {theta_arm2:.2f} degrés")
        except ValueError as e:
            print(e)

# if __name__ == "__main__":
#    main()
