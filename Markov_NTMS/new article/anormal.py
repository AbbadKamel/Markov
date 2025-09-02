import time
import random

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

def generate_time():
    return time.strftime("%H%M%S") + ".665"

def generate_latitude():
    degrees = random.randint(0, 90)
    minutes = round(random.uniform(0, 59.999), 3)
    direction = random.choice(["N", "S"])
    return f"{degrees:02d}{minutes:06.3f},{direction}"

def generate_longitude():
    degrees = random.randint(0, 180)
    minutes = round(random.uniform(0, 59.999), 3)
    direction = random.choice(["E", "W"])
    return f"{degrees:03d}{minutes:06.3f},{direction}"

def generate_speed():
    return round(random.uniform(0, 60), 1)

def generate_heading():
    return round(random.uniform(0, 360), 1)

def generate_date():
    return time.strftime("%d%m%y")

def simulate_flooding_attack(filename, duration=60, normal_packets_per_second=200, ddos_packets_per_second=10000, attack_intervals=[(10, 20), (30, 40), (50, 60)]):
    start_time = time.time()
    with open(filename, 'w') as f:
        while time.time() - start_time < duration:
            current_time = time.time() - start_time
            packets_per_second = normal_packets_per_second
            
            for start, end in attack_intervals:
                if start <= current_time < end:
                    packets_per_second = ddos_packets_per_second
                    break
            
            for _ in range(packets_per_second):
                message = generate_nmea2000_message()
                f.write(message + "\n")
            
            time.sleep(1)





def simulate_request_flooding_attack(filename, duration=60, normal_packets_per_second=200, ddos_packets_per_second=10000, attack_intervals=[(15, 25), (35, 45)]):
    start_time = time.time()
    with open(filename, 'w') as f:
        while time.time() - start_time < duration:
            current_time = time.time() - start_time
            packets_per_second = normal_packets_per_second
            
            for start, end in attack_intervals:
                if start <= current_time < end:
                    packets_per_second = ddos_packets_per_second
                    break
            
            for _ in range(packets_per_second):
                message = generate_nmea2000_message()
                f.write(message + "\n")
            
            time.sleep(1)




def simulate_configuration_attack(filename, duration=60, normal_packets_per_second=200, ddos_packets_per_second=10000, attack_intervals=[(20, 30), (40, 50)]):
    start_time = time.time()
    with open(filename, 'w') as f:
        while time.time() - start_time < duration:
            current_time = time.time() - start_time
            packets_per_second = normal_packets_per_second
            
            for start, end in attack_intervals:
                if start <= current_time < end:
                    packets_per_second = ddos_packets_per_second
                    break
            
            for _ in range(packets_per_second):
                message = generate_nmea2000_message()
                f.write(message + "\n")
            
            time.sleep(1)




if __name__ == "__main__":
    simulate_flooding_attack("nmea2000_flooding.txt")
    simulate_request_flooding_attack("nmea2000_request_flooding.txt")
    simulate_configuration_attack("nmea2000_configuration.txt")

