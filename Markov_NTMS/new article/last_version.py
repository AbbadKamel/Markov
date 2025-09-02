import random
import matplotlib.pyplot as plt
import numpy as np

# Générer des données normales
def generate_normal_data(filename, duration=200):
    with open(filename, 'w') as f:
        for millisecond in range(duration):
            num_packets = random.randint(0, 2) if millisecond < 5 else random.randint(5, 50)
            for _ in range(num_packets):
                f.write(f"$GPGGA,{millisecond:03d}{random.randint(0, 999):03d}.665,4918.{random.randint(100, 999)},N,00014.{random.randint(100, 999)},W,1,12,1.0,0.0,M,0.0,M,,*7A\n")
                f.write(f"$GPGSA,A,3,01,02,03,04,05,06,07,08,09,10,11,12,1.0,1.0,1.0*30\n")
                f.write(f"$GPRMC,{millisecond:03d}{random.randint(0, 999):03d}.665,A,4918.{random.randint(100, 999)},N,00014.{random.randint(100, 999)},W,3711.9,355.5,070824,000.0,W*5C\n")

# Simuler une attaque DDoS
def simulate_ddos_attack(filename, duration=200):
    with open(filename, 'w') as f:
        for millisecond in range(duration):
            if millisecond < 50 or (100 <= millisecond < 150):
                num_packets = random.randint(5, 50)
            else:
                num_packets = random.randint(200, 500)
            for _ in range(num_packets):
                f.write(f"$GPGGA,{millisecond:03d}{random.randint(0, 999):03d}.665,4918.{random.randint(100, 999)},N,00014.{random.randint(100, 999)},W,1,12,1.0,0.0,M,0.0,M,,*7A\n")
                f.write(f"$GPGSA,A,3,01,02,03,04,05,06,07,08,09,10,11,12,1.0,1.0,1.0*30\n")
                f.write(f"$GPRMC,{millisecond:03d}{random.randint(0, 999):03d}.665,A,4918.{random.randint(100, 999)},N,00014.{random.randint(100, 999)},W,3711.9,355.5,070824,000.0,W*5C\n")

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
def detect_ddos(packet_counts, threshold=100):
    current_state = "Normal"
    state_history = [state_indices[current_state]]

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
        
        state_history.append(state_indices[next_state])
        current_state = next_state

    return state_history

# Fonction principale pour analyser plusieurs fichiers et afficher les résultats
def main():
    normal_file = "nmea2000_normal.txt"
    ddos_file = "nmea2000_ddos.txt"

    # Générer des données normales et d'attaque
    generate_normal_data(normal_file)
    simulate_ddos_attack(ddos_file)
    
    filenames = [normal_file, ddos_file]
    labels = ["Normal", "DDoS Attack"]
    colors = ['black', 'red']
    
    plt.figure(figsize=(14, 7))

    for i, filename in enumerate(filenames):
        print(f"Analyzing file: {filename}")
        data = read_nmea2000_data(filename)
        packet_counts = []
        for j in range(200):  # Assumer 200 ms de données
            packet_counts.append(sum(1 for line in data if line.startswith(f"$GPGGA,{j:03d}") or line.startswith(f"$GPRMC,{j:03d}")))

        plt.plot(range(200), packet_counts, label=labels[i], color=colors[i])

    # Détection des attaques avec le modèle de Markov
    data_ddos = read_nmea2000_data(ddos_file)
    packet_counts_ddos = []
    for j in range(200):
        packet_counts_ddos.append(sum(1 for line in data_ddos if line.startswith(f"$GPGGA,{j:03d}") or line.startswith(f"$GPRMC,{j:03d}")))

    state_history = detect_ddos(packet_counts_ddos)
    state_history_normalized = [i * max(packet_counts_ddos) / max(state_indices.values()) for i in state_history]
    plt.plot(range(201), state_history_normalized, label="Predicted Attack", color='blue', linestyle='--')

    plt.xlabel("Time (milliseconds)")
    plt.ylabel("Number of Packets / State")
    plt.legend()
    plt.title("DDoS Attack Detection Using Advanced Markov Model")
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()
