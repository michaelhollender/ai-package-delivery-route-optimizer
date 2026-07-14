# Author: Michael Hollender
# Student ID: 011912131
# Title: WGUPS Routing Program
# Submitted: 07/11/2026

from datetime import timedelta
from pathlib import Path

from models.truck import Truck
from services.data_loader import load_packages
from services.distance_service import DistanceService
from services.package_assignment import (
    assign_packages_to_trucks
)
from services.routing_service import deliver_route


BASE_DIRECTORY = Path(__file__).resolve().parent
DATA_DIRECTORY = BASE_DIRECTORY / "data"

HUB_ADDRESS = "4001 South 700 East"


def create_trucks():
    """Creates the three delivery trucks."""

    truck_1 = Truck(
        truck_id=1,
        departure_time=timedelta(
            hours=8
        ),
        hub_address=HUB_ADDRESS
    )

    truck_2 = Truck(
        truck_id=2,
        departure_time=timedelta(
            hours=9,
            minutes=5
        ),
        hub_address=HUB_ADDRESS
    )

    # Truck 3 leaves when a driver returns.
    # Its actual departure time is updated later.
    truck_3 = Truck(
        truck_id=3,
        departure_time=timedelta(
            hours=8
            ),
        hub_address=HUB_ADDRESS
    )

    return truck_1, truck_2, truck_3


def parse_lookup_time(time_text):
    """
    Converts user input such as 9:45 AM into
    a timedelta.
    """

    time_text = time_text.strip().upper()

    try:
        clock_time, period = time_text.split()

        hour_text, minute_text = (
            clock_time.split(":")
        )

        hour = int(hour_text)
        minute = int(minute_text)

        if hour < 1 or hour > 12:
            return None

        if minute < 0 or minute > 59:
            return None

        if period not in ("AM", "PM"):
            return None

        if period == "PM" and hour != 12:
            hour += 12

        if period == "AM" and hour == 12:
            hour = 0

        return timedelta(
            hours=hour,
            minutes=minute
        )

    except ValueError:
        return None


def format_time(time_value):
    """Formats a timedelta as a 12-hour clock time."""

    if time_value is None:
        return "N/A"

    total_seconds = int(
        time_value.total_seconds()
    )

    hours = total_seconds // 3600
    minutes = (
        total_seconds % 3600
    ) // 60
    seconds = total_seconds % 60

    if hours >= 12:
        period = "PM"
    else:
        period = "AM"

    display_hour = hours % 12

    if display_hour == 0:
        display_hour = 12

    return (
        f"{display_hour:02d}:"
        f"{minutes:02d}:"
        f"{seconds:02d} {period}"
    )


def print_package(
    package,
    lookup_time
):
    """Prints one package's status at a selected time."""

    status = package.get_status_at_time(
        lookup_time
    )

    (
        display_address,
        display_city,
        display_state,
        display_zip
    ) = package.get_address_at_time(
        lookup_time
    )

    truck_display = (
        package.truck_id
        if package.truck_id is not None
        else "None"
    )

    full_address = (
        f"{display_address}, "
        f"{display_city}, "
        f"{display_state} "
        f"{display_zip}"
    )

    print(
        f"ID: {package.package_id:<2} | "
        f"Truck: {str(truck_display):<4} | "
        f"Address: {full_address:<58} | "
        f"Deadline: {package.deadline:<9} | "
        f"Status: {status}"
    )

def display_one_package_at_time(
    package_table
):
    """Displays one package at a requested time."""

    try:
        package_id = int(
            input(
                "Enter package ID: "
            ).strip()
        )

    except ValueError:
        print(
            "Package ID must be a number."
        )
        return

    package = package_table.get(package_id)

    if package is None:
        print("Package was not found.")
        return

    time_text = input(
        "Enter lookup time, such as 9:45 AM: "
    )

    lookup_time = parse_lookup_time(
        time_text
    )

    if lookup_time is None:
        print(
            "Invalid time. Use the format "
            "HH:MM AM or HH:MM PM."
        )
        return

    print()
    print("=" * 125)

    print(
        f"PACKAGE {package.package_id} STATUS AT "
        f"{format_time(lookup_time)}"
    )

    print("=" * 125)

    print_package(
        package,
        lookup_time
    )

    print("=" * 125)


def display_all_packages_at_time(
    package_table,
    trucks
):
    """
    Displays every package grouped by truck
    at a selected time.
    """

    time_text = input(
        "Enter lookup time, such as 9:00 AM: "
    )

    lookup_time = parse_lookup_time(
        time_text
    )

    if lookup_time is None:
        print(
            "Invalid time. Use the format "
            "HH:MM AM or HH:MM PM."
        )
        return

    print()
    print("=" * 125)

    print(
        f"PACKAGE DELIVERY STATUS AT "
        f"{format_time(lookup_time)}"
    )

    print("=" * 125)

    for truck in trucks:
        print()

        print(
            f"TRUCK {truck.truck_id} | "
            f"Departure: "
            f"{format_time(truck.departure_time)} | "
            f"Assigned packages: "
            f"{len(truck.package_ids)}"
        )

        print("-" * 125)

        package_ids = sorted(
            truck.package_ids
        )

        for package_id in package_ids:
            package = package_table.get(
                package_id
            )

            if package is not None:
                print_package(
                    package,
                    lookup_time
                )

    print()
    print("=" * 125)


def display_total_mileage(trucks):
    """
    Displays each truck's mileage and the combined
    mileage traveled by all trucks.
    """

    total_mileage = 0.0

    print()
    print("=" * 60)
    print("DELIVERY COMPLETION AND TOTAL MILEAGE")
    print("=" * 60)

    for truck in trucks:
        print(
            f"Truck {truck.truck_id}: "
            f"{truck.mileage:.1f} miles"
        )

        total_mileage += truck.mileage

    print("-" * 60)

    print(
        f"Total mileage traveled by all trucks: "
        f"{total_mileage:.1f} miles"
    )

    print(
        "All assigned packages have been delivered."
    )

    print("=" * 60)


def verify_all_packages_delivered(
    package_table
):
    """Checks whether every package was delivered."""

    undelivered_packages = []

    for package in package_table.values():
        if package.status != "Delivered":
            undelivered_packages.append(
                package.package_id
            )

    if undelivered_packages:
        print(
            "Warning: The following packages "
            "were not delivered:"
        )

        print(undelivered_packages)

        return False

    return True


def run_user_interface(
    package_table,
    trucks
):
    """Runs the command-line user interface."""

    while True:
        print()
        print("=" * 55)
        print("WGUPS PACKAGE DELIVERY PROGRAM")
        print("=" * 55)

        print(
            "1. View one package at a selected time"
        )

        print(
            "2. View all packages by truck "
            "at a selected time"
        )

        print(
            "3. View total truck mileage"
        )

        print("4. Exit")

        choice = input(
            "Enter a menu option: "
        ).strip()

        if choice == "1":
            display_one_package_at_time(
                package_table
            )

        elif choice == "2":
            display_all_packages_at_time(
                package_table,
                trucks
            )

        elif choice == "3":
            display_total_mileage(
                trucks
            )

        elif choice == "4":
            print("Program closed.")
            break

        else:
            print(
                "Please enter 1, 2, 3, or 4."
            )


def main():
    """Loads data and runs the delivery program."""

    package_file = (
        DATA_DIRECTORY / "packageCSV.csv"
    )

    address_file = (
        DATA_DIRECTORY / "addressCSV.csv"
    )

    distance_file = (
        DATA_DIRECTORY / "distanceCSV.csv"
    )

    print("Loading package data...")

    package_table = load_packages(
        package_file
    )

    print("Loading distance data...")

    distance_service = DistanceService()

    distance_service.load_addresses(
        address_file
    )

    distance_service.load_distances(
        distance_file
    )

    truck_1, truck_2, truck_3 = (
        create_trucks()
    )

    assign_packages_to_trucks(
        truck_1,
        truck_2,
        truck_3,
        package_table
    )

    print()
    print("Starting delivery simulation...")

    deliver_route(
        truck_1,
        package_table,
        distance_service
    )

    deliver_route(
        truck_2,
        package_table,
        distance_service
    )

    # Only two drivers are available. Truck 3
    # leaves when a driver returns.

    earliest_driver_return = min(
        truck_1.current_time,
        truck_2.current_time
    )

    truck_3_departure = earliest_driver_return

    truck_3.update_departure_time(
        truck_3_departure,
        package_table
    )
    
    deliver_route(
        truck_3,
        package_table,
        distance_service
    )

   
    trucks = [
        truck_1,
        truck_2,
        truck_3
    ]

    print()
    print("=" * 60)

    if verify_all_packages_delivered(
        package_table
    ):
        print(
            "Delivery simulation completed successfully."
        )

    print("=" * 60)

    display_total_mileage(trucks)

    run_user_interface(
        package_table,
        trucks
    )


if __name__ == "__main__":
    main()