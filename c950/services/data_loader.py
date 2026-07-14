import csv 
from datetime import timedelta

from models.package import Package
from structures.hash_table import HashTable

def parse_time(time_text):
    """Converts a time such as 9:05 AM into a timedelta."""

    if time_text is None or time_text == "":
        return None

    time_text = time_text.strip().upper()

    if time_text == "EOD":
        return None

    clock_time, period = time_text.split()
    hour, minute = clock_time.split(":")

    hour = int(hour)
    minute = int(minute)

    if period == "PM" and hour != 12:
        hour += 12

    if period == "AM" and hour == 12:
        hour = 0

    return timedelta(hours=hour, minutes=minute)


def get_hub_arrival_time(notes):
    """Determines when a package becomes available at the hub."""

    notes_lower = notes.lower()

    if "delayed" in notes_lower:
        return timedelta(hours=9, minutes=5)
    
    return timedelta(hours=8)


def load_packages(file_path):
    """Loads package records into a custom hash table."""

    package_table = HashTable(capacity=20)

    with open(
        file_path,
        mode="r",
        encoding="utf-8-sig"
    ) as file:

        reader = csv.reader(file)

        next(reader, None)

        for row in reader:
            if not row:
                continue

            notes = row[7].strip()

            package = Package(
                package_id=int(row[0]),
                address=row[1].strip(),
                city=row[2].strip(),
                state=row[3].strip(),
                zip_code=row[4].strip(),
                deadline=row[5].strip(),
                weight=row[6].strip(),
                notes=notes,
                hub_arrival_time=get_hub_arrival_time(notes)
            )

            package_table.insert(
                package.package_id,
                package
            )

    return package_table
