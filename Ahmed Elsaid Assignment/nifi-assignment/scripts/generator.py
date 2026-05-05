import json
import random
import time
import os
from datetime import datetime

# المسار الصحيح (مرتبط مع Docker)
output_dir = r"C:\Users\Admin\Desktop\A1 Assignment\Ahmed Elsaid Assignment\nifi-assignment\data_input"
os.makedirs(output_dir, exist_ok=True)

names = ["Ali", "Ahmed", "Sara", "Mona", "Khaled"]
cities = ["Sanaa", "Aden", "Taiz", "Ibb"]

def generate_record():
    return {
        "id": random.randint(1, 5),  # duplicates
        "name": random.choice(names),
        "city": random.choice(cities),
        "amount": random.choice([100, 200, None, 300]),  # missing values
        "timestamp": random.choice([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            datetime.now().strftime("%d-%m-%Y %H:%M:%S")  # inconsistent format
        ])
    }

while True:
    data = [generate_record() for _ in range(5)]

    file_name = f"data_{int(time.time())}.json"
    file_path = os.path.join(output_dir, file_name)

    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Generated: {file_name}")
    time.sleep(5)