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

# Matrice de transition
transition_matrix = np.array([
    [0.8, 0.2, 0.0, 0.0],  # Normal
    [0.0, 0.6, 0.4, 0.0],  # Anomaly Detected
    [0.0, 0.0, 0.7, 0.3],  # Mitigation in Progress
    [0.0, 0.0, 0.0, 1.0]   # Blocking
])

# Détecter une attaque DDoS basée sur le nombre de paquets
def detect_ddos(packet_counts, threshold=5000):
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
            next_state = "Normal"
        
        state_history.append(next_state)
        current_state = next_state

    return state_history

# Fonction principale pour analyser plusieurs fichiers et afficher les résultats
def main():
    normal_filename = "nmea2000_normal.txt"
    attack_filenames = ["nmea2000_flooding.txt", "nmea2000_request_flooding.txt", "nmea2000_configuration.txt"]
    attack_labels = ["Flooding Attack", "Request Flooding Attack", "Configuration Attack"]
    colors = ['blue', 'orange', 'green']
    
    # Analyser et afficher les données normales
    print(f"Analyzing normal file: {normal_filename}")
    normal_data = read_nmea2000_data(normal_filename)
    normal_packet_counts = []

    for j in range(60):  # Assumer 60 secondes de données
        normal_packet_counts.append(sum(1 for line in normal_data if f"{j:02d}" in line.split(",")[1]))

    normal_state_history = detect_ddos(normal_packet_counts)
    normal_state_indices_history = [state_indices[state] for state in normal_state_history]
    
    plt.figure(figsize=(14, 7))
    plt.plot(range(61), normal_state_indices_history, label="Normal Operation", color='black')

    plt.xlabel("Time (seconds)")
    plt.ylabel("State")
    plt.yticks(ticks=list(state_indices.values()), labels=list(state_indices.keys()))
    plt.legend()
    plt.title("Normal Operation Detection Using Markov Model")
    plt.grid(True)
    plt.show()

    # Analyser et afficher les données d'attaque
    plt.figure(figsize=(14, 7))
    
    for i, filename in enumerate(attack_filenames):
        print(f"Analyzing file: {filename}")
        attack_data = read_nmea2000_data(filename)
        attack_packet_counts = []

        for j in range(60):  # Assumer 60 secondes de données
            attack_packet_counts.append(sum(1 for line in attack_data if f"{j:02d}" in line.split(",")[1]))

        attack_state_history = detect_ddos(attack_packet_counts)
        attack_state_indices_history = [state_indices[state] for state in attack_state_history]
        
        plt.plot(range(61), attack_state_indices_history, label=attack_labels[i], color=colors[i])

    plt.xlabel("Time (seconds)")
    plt.ylabel("State")
    plt.yticks(ticks=list(state_indices.values()), labels=list(state_indices.keys()))
    plt.legend()
    plt.title("DDoS Attack Detection Using Markov Model")
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()
