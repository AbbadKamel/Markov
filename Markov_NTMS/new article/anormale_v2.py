import random
import matplotlib.pyplot as plt

def simulate_flooding_attack(filename, duration=200):
    with open(filename, 'w') as f:
        for millisecond in range(duration):
            if millisecond < 50:  # Normal operation
                num_packets = random.randint(5, 50)
            elif 50 <= millisecond < 100:  # First attack
                num_packets = random.randint(100, 200)
            elif 100 <= millisecond < 150:  # Return to normal
                num_packets = random.randint(5, 50)
            elif 150 <= millisecond < 175:  # Second attack
                num_packets = random.randint(100, 200)
            else:  # Massive attack
                num_packets = random.randint(200, 300)

            for _ in range(num_packets):
                f.write(f"$GPGGA,{millisecond:03d}{random.randint(0, 999):03d}.665,4918.{random.randint(100, 999)},N,00014.{random.randint(100, 999)},W,1,12,1.0,0.0,M,0.0,M,,*7A\n")
                f.write(f"$GPGSA,A,3,01,02,03,04,05,06,07,08,09,10,11,12,1.0,1.0,1.0*30\n")
                f.write(f"$GPRMC,{millisecond:03d}{random.randint(0, 999):03d}.665,A,4918.{random.randint(100, 999)},N,00014.{random.randint(100, 999)},W,3711.9,355.5,070824,000.0,W*5C\n")

def simulate_request_flooding_attack(filename, duration=200):
    with open(filename, 'w') as f:
        for millisecond in range(duration):
            if millisecond < 50:  # Normal operation
                num_packets = random.randint(5, 50)
            elif 50 <= millisecond < 100:  # First attack
                num_packets = random.randint(100, 200)
            elif 100 <= millisecond < 150:  # Return to normal
                num_packets = random.randint(5, 50)
            elif 150 <= millisecond < 175:  # Second attack
                num_packets = random.randint(100, 200)
            else:  # Massive attack
                num_packets = random.randint(200, 300)

            for _ in range(num_packets):
                f.write(f"$GPGGA,{millisecond:03d}{random.randint(0, 999):03d}.665,4918.{random.randint(100, 999)},N,00014.{random.randint(100, 999)},W,1,12,1.0,0.0,M,0.0,M,,*7A\n")

def simulate_configuration_attack(filename, duration=200):
    with open(filename, 'w') as f:
        for millisecond in range(duration):
            if millisecond < 50:  # Normal operation
                num_packets = random.randint(5, 50)
            elif 50 <= millisecond < 100:  # First attack
                num_packets = random.randint(100, 200)
            elif 100 <= millisecond < 150:  # Return to normal
                num_packets = random.randint(5, 50)
            elif 150 <= millisecond < 175:  # Second attack
                num_packets = random.randint(100, 200)
            else:  # Massive attack
                num_packets = random.randint(200, 300)

            for _ in range(num_packets):
                f.write(f"$GPGSA,{millisecond:03d}{random.randint(0, 999):03d},A,3,01,02,03,04,05,06,07,08,09,10,11,12,1.0,1.0,1.0*30\n")

def read_nmea2000_data(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    return [line.strip() for line in lines]

def plot_ddos_attacks():
    filenames = ["nmea2000_flooding.txt", "nmea2000_request_flooding.txt", "nmea2000_configuration.txt"]
    labels = ["Flooding Attack", "Request Flooding Attack", "Configuration Attack"]
    colors = ['blue', 'orange', 'green']
    
    plt.figure(figsize=(14, 7))
    
    for i, filename in enumerate(filenames):
        print(f"Analyzing file: {filename}")
        data = read_nmea2000_data(filename)
        packet_counts = []
        for j in range(200):  # Assumer 200 ms de données
            if i == 2:
                # For the configuration attack, we count "$GPGSA" messages
                packet_counts.append(sum(1 for line in data if line.startswith(f"$GPGSA,{j:03d}")))
            else:
                # For the other attacks, we count "$GPGGA" and "$GPRMC" messages
                packet_counts.append(sum(1 for line in data if line.startswith(f"$GPGGA,{j:03d}") or line.startswith(f"$GPRMC,{j:03d}")))

        plt.plot(range(200), packet_counts, label=labels[i], color=colors[i])

    plt.xlabel("Time (milliseconds)")
    plt.ylabel("Number of Packets")
    plt.title("DDoS Attack Detection Using Markov Model")
    plt.legend()
    plt.grid(True)
    plt.show()

# Generate the attack data
simulate_flooding_attack("nmea2000_flooding.txt")
simulate_request_flooding_attack("nmea2000_request_flooding.txt")
simulate_configuration_attack("nmea2000_configuration.txt")

# Plot the results
plot_ddos_attacks()
