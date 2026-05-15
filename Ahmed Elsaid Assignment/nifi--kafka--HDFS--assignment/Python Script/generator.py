import csv
import time
import random
import uuid
import os
from datetime import datetime

# إعداد مسار المجلد الذي سيقرأ منه NiFi
OUTPUT_DIR = "E:\Data Engineering Bootcamp Lab\spark-sql-and-pyspark-using-python3\lab_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# قائمة المنتجات والعملاء الوهميين
PRODUCTS = ['Laptop', 'Smartphone', 'Headphones', 'Monitor', 'Keyboard']
CUSTOMERS = [f'CUST{i:03}' for i in range(1, 20)]


def generate_messy_record():
    """توليد سجل بيانات مع احتمالية وجود أخطاء مقصودة"""
    transaction_id = str(uuid.uuid4())[:8]
    customer_id = random.choice(CUSTOMERS)
    product = random.choice(PRODUCTS)
    amount = round(random.uniform(10.0, 1500.0), 2)

    # 1. تنسيقات تاريخ مختلفة (Different timestamp formats)
    if random.random() < 0.2:
        date_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    else:
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 2. قيم مفقودة (Missing values)
    if random.random() < 0.1:
        customer_id = ""

    # 3. تناقضات رقمية (Numeric inconsistencies)
    if random.random() < 0.1:
        amount = amount * -1  # قيمة سالبة غير منطقية

    # 4. سجلات غير صالحة/تالفة (Invalid/Corrupted records)
    if random.random() < 0.05:
        return ["CORRUPTED_ROW_ERROR", "###", "NULL", "???"]

    return [transaction_id, customer_id, product, amount, date_str]


def start_streaming():
    print(f"Starting data generation in directory: {OUTPUT_DIR}")
    file_counter = 1

    while True:  # توليد البيانات بشكل مستمر (Continuously generate data)
        file_name = f"ecommerce_batch_{file_counter}_{int(time.time())}.csv"
        file_path = os.path.join(OUTPUT_DIR, file_name)

        # إنشاء من 50 إلى 200 سجل في كل ملف
        num_records = random.randint(50, 200)
        records = [generate_messy_record() for _ in range(num_records)]

        # 5. سجلات مكررة (Duplicate records)
        if random.random() < 0.15 and len(records) > 0:
            records.append(records[0])

        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['transaction_id', 'customer_id', 'product', 'amount', 'timestamp'])
            writer.writerows(records)

        print(f"Generated {file_name} with {len(records)} records.")
        file_counter += 1

        # التوقف لثوانٍ قليلة لمحاكاة التدفق المستمر (Simulate streaming behavior)
        time.sleep(random.randint(3, 7))


if __name__ == "__main__":
    start_streaming()