import numpy as np
import matplotlib.pyplot as plt

# Function to read NMEA2000 data
def read_nmea2000_data(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    return [line.strip() for line in lines]

# Function to calculate the transition matrix
def calculate_transition_matrix(state_history, num_states):
    transition_matrix = np.zeros((num_states, num_states))
    for (current_state, next_state) in zip(state_history[:-1], state_history[1:]):
        transition_matrix[current_state, next_state] += 1

    # Avoid division by zero by checking if row sums are zero
    row_sums = transition_matrix.sum(axis=1, keepdims=True)
    with np.errstate(divide='ignore', invalid='ignore'):
        transition_matrix = np.divide(transition_matrix, row_sums, where=row_sums != 0)

    return transition_matrix

# Function to detect DDoS attacks and determine device states
def detect_ddos(packet_counts, packet_types, interval_timings, thresholds):
    current_state = 0  # Authentic is represented by 0
    state_history = [current_state]
    state_durations = {state: 0 for state in range(13)}  # Track duration in each state

    for packet_count, packet_type, interval_timing in zip(packet_counts, packet_types, interval_timings):
        if packet_count > thresholds['high']:
            if current_state == 0:  # Authentic
                next_state = 1  # Peripheral Low Risk (P1)
            elif current_state == 1:  # P1
                if packet_type == 'suspicious':
                    next_state = 2  # Peripheral Medium Risk (P2)
                else:
                    next_state = 3  # Core Low Risk (C1)
            elif current_state == 2:  # P2
                next_state = 4  # Peripheral High Risk (P3)
            elif current_state == 3:  # C1
                if interval_timing < thresholds['interval']:
                    next_state = 5  # Core Medium Risk (C2)
                else:
                    next_state = 6  # Peripheral Critical Risk (P4)
            elif current_state == 4:  # P3
                next_state = 7  # Core High Risk (C3)
            elif current_state == 5:  # C2
                next_state = 8  # Core Critical Risk (C4)
            elif current_state == 6:  # P4
                next_state = 9  # Observation (Obs)
            elif current_state == 7:  # C3
                next_state = 10  # Suspicion (S)
            elif current_state == 8:  # C4
                next_state = 11  # Blocked (B)
            elif current_state == 9:  # Obs
                next_state = 12  # Shutdown (SD)
            elif current_state == 10:  # S
                next_state = 12  # Shutdown (SD)
            elif current_state == 11:  # B
                next_state = 12  # Shutdown (SD)
        else:
            next_state = 0  # Revert to Authentic if thresholds are not met

        state_history.append(next_state)
        state_durations[next_state] += 1  # Track how long we're in the state
        current_state = next_state

    return state_history, state_durations

# Function to analyze the duration spent in each state (semi-Markov aspect)
def analyze_state_durations(state_durations):
    total_time = sum(state_durations.values())
    normalized_durations = {state: duration / total_time for state, duration in state_durations.items()}
    return normalized_durations

# Function to calculate accuracy, detection rate, and error rate
def calculate_metrics(state_history, true_states):
    correct_predictions = sum(1 for pred, true in zip(state_history, true_states) if pred == true)
    accuracy = correct_predictions / len(true_states)

    detection_rate = sum(1 for pred in state_history if pred != 0) / len(state_history)  # Not in Authentic state
    error_rate = 1 - accuracy

    return accuracy, detection_rate, error_rate

def main():
    normal_file = "nmea2000_normal.txt"
    ddos_file = "nmea2000_ddos.txt"

    # Analyze normal data file
    normal_data = read_nmea2000_data(normal_file)
    normal_packet_counts = []
    for j in range(200):
        normal_packet_counts.append(sum(1 for line in normal_data if line.startswith(f"$GPGGA,{j:03d}") or line.startswith(f"$GPRMC,{j:03d}")))

    # Analyze DDoS data file
    ddos_data = read_nmea2000_data(ddos_file)
    ddos_packet_counts = []
    packet_types = []
    interval_timings = []
    for j in range(200):
        ddos_packet_counts.append(sum(1 for line in ddos_data if line.startswith(f"$GPGGA,{j:03d}") or line.startswith(f"$GPRMC,{j:03d}")))
        packet_types.append('normal' if j % 10 != 0 else 'suspicious')  # Simple example
        interval_timings.append(j % 50)  # Simple example

    # Set thresholds for state transitions
    thresholds = {
        'high': 100,
        'interval': 20
    }

    # Calculate state history and durations based on DDoS data
    state_history, state_durations = detect_ddos(ddos_packet_counts, packet_types, interval_timings, thresholds)

    # Analyze state durations
    state_durations_normalized = analyze_state_durations(state_durations)

    # Calculate transition matrix based on state history
    num_states = 13  # Number of states
    transition_matrix = calculate_transition_matrix(state_history, num_states)
    print("Transition Matrix:")
    print(transition_matrix)

    # Simulate true states for calculating metrics
    true_states = [0 if i < 150 else 1 for i in range(200)]  # Simple example

    # Calculate metrics
    accuracy, detection_rate, error_rate = calculate_metrics(state_history, true_states)
    print(f"Accuracy: {accuracy*100:.2f}%")
    print(f"Detection Rate: {detection_rate*100:.2f}%")
    print(f"Error Rate: {error_rate*100:.2f}%")

    # Plot results

    # Figure 1: Packet Count Over Time (Normal vs. DDoS)
    plt.figure(figsize=(14, 7))
    plt.plot(range(200), normal_packet_counts, label="Normal", color='black')
    plt.plot(range(200), ddos_packet_counts, label="DDoS Attack", color='red')
    plt.xlabel("Time (milliseconds)")
    plt.ylabel("Number of Packets")
    plt.legend()
    plt.title("Figure 1: Packet Count Over Time (Normal vs. DDoS)")
    plt.grid(True)
    plt.show()

    # Figure 2: State History Over Time
    plt.figure(figsize=(14, 7))
    plt.plot(range(200), state_history[:-1], label="Predicted Attack State", color='blue', linestyle='--')
    plt.xlabel("Time (milliseconds)")
    plt.ylabel("State Value")
    plt.legend()
    plt.title("Figure 2: State History Over Time")
    plt.grid(True)
    plt.show()

    # Figure 3: Transition Matrix
    plt.figure(figsize=(10, 7))
    plt.imshow(transition_matrix, cmap='Blues', interpolation='none')
    plt.colorbar()
    plt.title("Figure 3: Transition Matrix")
    plt.xlabel("Next State")
    plt.ylabel("Current State")
    plt.show()

    # Figure 4: State Duration Distribution
    plt.figure(figsize=(10, 7))
    state_ids = list(state_durations_normalized.keys())
    state_durations = list(state_durations_normalized.values())
    plt.bar(state_ids, state_durations, color='purple')
    plt.xlabel("State ID")
    plt.ylabel("Normalized Duration")
    plt.title("Figure 4: State Duration Distribution")
    plt.show()

    # Figure 5: Cumulative Packet Count Over Time
    plt.figure(figsize=(14, 7))
    plt.plot(range(200), np.cumsum(normal_packet_counts), label="Normal", color='black')
    plt.plot(range(200), np.cumsum(ddos_packet_counts), label="DDoS Attack", color='red')
    plt.xlabel("Time (milliseconds)")
    plt.ylabel("Cumulative Number of Packets")
    plt.legend()
    plt.title("Figure 5: Cumulative Packet Count Over Time")
    plt.grid(True)
    plt.show()

    # Figure 6: Packet Type Distribution
    plt.figure(figsize=(10, 7))
    unique_packet_types, packet_type_counts = np.unique(packet_types, return_counts=True)
    plt.bar(unique_packet_types, packet_type_counts, color=['green', 'orange'])
    plt.xlabel("Packet Type")
    plt.ylabel("Count")
    plt.title("Figure 6: Packet Type Distribution")
    plt.show()

    # Figure 7: Interval Timing Distribution (Removed)

    # New Figure 7: Accuracy, Detection Rate, and Error Rate
    metrics = ['Accuracy', 'Detection Rate', 'Error Rate']
    values = [accuracy, detection_rate, error_rate]
    plt.figure(figsize=(10, 7))
    plt.bar(metrics, values, color=['blue', 'green', 'red'])
    plt.xlabel("Metrics")
    plt.ylabel("Rate")
    plt.title("Figure 7: Accuracy, Detection Rate, and Error Rate")
    plt.ylim(0, 1)
    plt.show()



if __name__ == "__main__":
    main()
