import random
import matplotlib.pyplot as plt

def simulate_flooding_attack(filename, duration=200):
    with open(filename, 'w') as f:
        for millisecond in range(duration):
            if millisecond < 30 or (80 <= millisecond < 90) or (140 <= millisecond < 150):  # Normal traffic
                num_packets = random.randint(5, 50)
            elif (30 <= millisecond < 80) or (90 <= millisecond < 140) or (150 <= millisecond < 200):  # DDoS traffic
                num_packets = random.randint(200, 500)
            for _ in range(num_packets):
                f.write(f"$GPGGA,{millisecond:03d}{random.randint(0, 999):03d}.665,4918.{random.randint(100, 999)},N,00014.{random.randint(100, 999)},W,1,12,1.0,0.0,M,0.0,M,,*7A\n")
                f.write(f"$GPGSA,A,3,01,02,03,04,05,06,07,08,09,10,11,12,1.0,1.0,1.0*30\n")
                f.write(f"$GPRMC,{millisecond:03d}{random.randint(0, 999):03d}.665,A,4918.{random.randint(100, 999)},N,00014.{random.randint(100, 999)},W,3711.9,355.5,070824,000.0,W*5C\n")

def read_nmea2000_data(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    return [line.strip() for line in lines]

def main():
    ddos_file = "nmea2000_ddos.txt"
    simulate_flooding_attack(ddos_file)
    
    # Analyse du fichier DDoS
    data = read_nmea2000_data(ddos_file)
    packet_counts = []
    for j in range(200):
        packet_counts.append(sum(1 for line in data if line.startswith(f"$GPGGA,{j:03d}") or line.startswith(f"$GPRMC,{j:03d}")))

    plt.figure(figsize=(10, 7))
    plt.plot(range(200), packet_counts, label="DDoS Attack", color='red')
    
    plt.xlabel("Time (milliseconds)")
    plt.ylabel("Number of Packets")
    plt.title("DDoS Attack on NMEA 2000")
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()
