import random
import matplotlib.pyplot as plt

def generate_normal_data(filename, duration=200):
    with open(filename, 'w') as f:
        for millisecond in range(duration):
            num_packets = random.randint(0, 2) if millisecond < 5 else random.randint(5, 50)
            for _ in range(num_packets):
                f.write(f"$GPGGA,{millisecond:03d}{random.randint(0, 999):03d}.665,4918.{random.randint(100, 999)},N,00014.{random.randint(100, 999)},W,1,12,1.0,0.0,M,0.0,M,,*7A\n")
                f.write(f"$GPGSA,A,3,01,02,03,04,05,06,07,08,09,10,11,12,1.0,1.0,1.0*30\n")
                f.write(f"$GPRMC,{millisecond:03d}{random.randint(0, 999):03d}.665,A,4918.{random.randint(100, 999)},N,00014.{random.randint(100, 999)},W,3711.9,355.5,070824,000.0,W*5C\n")

def read_nmea2000_data(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    return [line.strip() for line in lines]

def main():
    normal_file = "nmea2000_normal.txt"
    generate_normal_data(normal_file)
    
    # Analyse du fichier normal
    data = read_nmea2000_data(normal_file)
    packet_counts = []
    for j in range(200):  # Changer la durée à 200 ms
        packet_counts.append(sum(1 for line in data if line.startswith(f"$GPGGA,{j:03d}") or line.startswith(f"$GPRMC,{j:03d}")))

    plt.figure(figsize=(10, 7))
    plt.plot(range(200), packet_counts, label="Normal", color='black')  # Changer la durée à 200 ms
    
    plt.xlabel("Time (milliseconds)")
    plt.ylabel("Number of Packets")
    plt.title("Normal Operation of NMEA 2000")
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()
