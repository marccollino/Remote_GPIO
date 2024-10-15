import csv
from datetime import datetime

def logTextToCSV(text, filePath="/home/administrator/projects/Remote_GPIO/repo/project-root/logs/dataLog.csv"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filePath, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, text])