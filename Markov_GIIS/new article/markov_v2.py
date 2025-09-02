import numpy as np
import matplotlib.pyplot as plt

# Lire les données NMEA 2000 depuis un fichier
def read_nmea2000_data(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    return [line.strip() for line in lines]

# Définir les états
states = ["Normal", "Anomaly Detected", "Mitigation in Progress", "Blocking"]
state_indices = {state: i for i, state in enumerate(states)}

# Matrice de transition avancée
transition_matrix = np.array([
    [0.85, 0.15, 0.0, 0.0],  # Normal
    [0.1, 0.6, 0.3, 0.0],    # Anomaly Detected
    [0.0, 0.2, 0.6, 0.2],    # Mitigation in Progress
    [0.0, 0.0, 0.0, 1.0]     # Blocking
])

# Fonction de détection avancée utilisant le modèle de Markov
def detect_ddos_advanced(packet_counts, normal_packet_counts, threshold=500):
    current_state = "Normal"
    state_history = [current_state]

    for packet_count in packet_counts:
        if packet_count > threshold:
            if current_state == "Normal":
                next_state = "Anomaly Detected"
            elif current_state == "Anomaly Detected":
                next_state = "Mitigation in Progress"
            elif current_state == "Mitigation in Progress":
                next_state = "Blocking"
        else:
            if current_state == "Anomaly Detected":
                next_state = "Normal" if np.random.rand() < transition_matrix[state_indices[current_state], state_indices["Normal"]] else "Anomaly Detected"
            elif current_state == "Mitigation in Progress":
                next_state = "Normal" if np.random.rand() < transition_matrix[state_indices[current_state], state_indices["Normal"]] else "Mitigation in Progress"
            elif current_state == "Blocking":
                next_state = "Blocking"
            else:
                next_state = "Normal"
        
        state_history.append(next_state)
        current_state = next_state

    return state_history

# Fonction principale pour analyser plusieurs fichiers et afficher les résultats
def main():
    normal_file = "nmea2000_normal.txt"
    attack_files = ["nmea2000_flooding.txt", "nmea2000_request_flooding.txt", "nmea2000_configuration.txt"]
    labels = ["Flooding Attack", "Request Flooding Attack", "Configuration Attack"]
    colors = ['blue', 'orange', 'green']

    # Lire les données normales
    normal_data = read_nmea2000_data(normal_file)
    normal_packet_counts = []
    for j in range(200):
        normal_packet_counts.append(sum(1 for line in normal_data if f"{j:03d}" in line.split(",")[1]))

    plt.figure(figsize=(14, 7))

    for i, filename in enumerate(attack_files):
        print(f"Analyzing file: {filename}")
        attack_data = read_nmea2000_data(filename)
        attack_packet_counts = []

        # Compter le nombre de paquets pour chaque milliseconde
        for j in range(200):
            attack_packet_counts.append(sum(1 for line in attack_data if f"{j:03d}" in line.split(",")[1]))

        state_history = detect_ddos_advanced(attack_packet_counts, normal_packet_counts)
        state_indices_history = [state_indices[state] for state in state_history]
        
        # Tracer les résultats
        plt.plot(range(201), state_indices_history, label=labels[i], color=colors[i])

        # Afficher les états détectés
        for state in state_history:
            if state != "Normal":
                plt.plot(state_indices_history, label="Detected Anomaly", color='red')

    plt.xlabel("Time (milliseconds)")
    plt.ylabel("State")
    plt.yticks(ticks=list(state_indices.values()), labels=list(state_indices.keys()))
    plt.legend()
    plt.title("DDoS Attack Detection Using Advanced Markov Model")
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()
