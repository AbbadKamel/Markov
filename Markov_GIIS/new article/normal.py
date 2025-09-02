import time
import random

# Fonction pour générer un message NMEA 2000
def generate_nmea2000_message():
    message_types = ["GPGGA", "GPGSA", "GPRMC"]
    message_type = random.choice(message_types)
    
    if message_type == "GPGGA":
        message = f"{message_type},{generate_time()},{generate_latitude()},{generate_longitude()},1,12,1.0,0.0,M,0.0,M,,*7A"
    elif message_type == "GPGSA":
        message = f"{message_type},A,3,01,02,03,04,05,06,07,08,09,10,11,12,1.0,1.0,1.0*30"
    elif message_type == "GPRMC":
        message = f"{message_type},{generate_time()},A,{generate_latitude()},{generate_longitude()},{generate_speed()},{generate_heading()},{generate_date()},000.0,W*5C"
    
    return message

# Générer une heure au format hhmmss.sss
def generate_time():
    return time.strftime("%H%M%S") + ".665"

# Générer une latitude aléatoire
def generate_latitude():
    degrees = random.randint(0, 90)
    minutes = round(random.uniform(0, 59.999), 3)
    direction = random.choice(["N", "S"])
    return f"{degrees:02d}{minutes:06.3f},{direction}"

# Générer une longitude aléatoire
def generate_longitude():
    degrees = random.randint(0, 180)
    minutes = round(random.uniform(0, 59.999), 3)
    direction = random.choice(["E", "W"])
    return f"{degrees:03d}{minutes:06.3f},{direction}"

# Générer une vitesse aléatoire en nœuds
def generate_speed():
    return round(random.uniform(0, 60), 1)

# Générer un cap aléatoire
def generate_heading():
    return round(random.uniform(0, 360), 1)

# Générer une date au format ddmmyy
def generate_date():
    return time.strftime("%d%m%y")

# Simuler des données NMEA 2000 et les enregistrer dans un fichier
def simulate_nmea2000_data(filename, duration=10, packets_per_second=200):
    start_time = time.time()
    with open(filename, 'w') as f:
        while time.time() - start_time < duration:
            for _ in range(packets_per_second):
                message = generate_nmea2000_message()
                f.write(message + "\n")
            time.sleep(1)

if __name__ == "__main__":
    simulate_nmea2000_data("nmea2000_normal.txt", duration=10, packets_per_second=200)
