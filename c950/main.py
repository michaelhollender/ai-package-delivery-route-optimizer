from datetime import timedelta
from pathlib import Path

from models.truck import Truck
from services.data_loader import load_packages
from services.distance_service import DistanceService
from services.package_assignment import assign_packages_to_trucks
from services.routing_service import deliver_route


BASE_DIRECTORY = Path(__file__).resolve().parent
DATA_DIRECTORY = BASE_DIRECTORY / "data"

HUB_ADDRESS = "4001 South 700 East"


def create_trucks():
    """Creates the three WGUPS trucks."""

    truck_1 = Truck(
        truck_id=1,
        departure_time=timedelta(hours=8),
        hub_address=HUB_ADDRESS
    )

    truck_2 = Truck(
        truck_id=2,
        departure_time=timedelta(hours=9, minutes=5),
        hub_address=HUB_ADDRESS
    )

    # Truck 3's actual departure time should be updated after
    # one of the first two trucks returns because there are only
    # two available drivers.
    truck_3 = Truck(
        truck_id=3,
        departure_time=timedelta(hours=10, minutes=20),
        hub_address=HUB_ADDRESS
    )

    return truck_1, truck_2, truck_3


def print_package(package):
    """Prints package information."""

    print(
        f"ID: {package.package_id} | "
        f"Address: {package.address}, "
        f"{package.city}, {package.state} "
        f"{package.zip_code} | "
        f"Deadline: {package.deadline} | "
        f"Weight: {package.weight} | "
        f"Status: {package.status} | "
        f"Truck: {package.truck_id} | "
        f"Delivered: {package.delivery_time}"
    )


def run_user_interface(package_table, trucks):
    """Runs the command-line package lookup interface."""

    while True:
        print("\nWGUPS Package Delivery Program")
        print("1. Look up one package")
        print("2. Display all packages")
        print("3. Display truck mileage")
        print("4. Exit")

        choice = input("Enter a menu option: ").strip()

        if choice == "1":
            try:
                package_id = int(
                    input("Enter package ID: ")
                )
            except ValueError:
                print("Package ID must be a number.")
                continue

            package = package_table.get(package_id)

            if package is None:
                print("Package was not found.")
            else:
                print_package(package)

        elif choice == "2":
            packages = package_table.values()
            packages.sort(
                key=lambda package: package.package_id
            )

            for package in packages:
                print_package(package)

        elif choice == "3":
            total_mileage = 0.0

            for truck in trucks:
                print(
                    f"Truck {truck.truck_id}: "
                    f"{truck.mileage:.1f} miles"
                )
                total_mileage += truck.mileage

            print(f"Total mileage: {total_mileage:.1f} miles")

        elif choice == "4":
            print("Program closed.")
            break

        else:
            print("Please enter 1, 2, 3, or 4.")


def main():
    """Loads data and runs the delivery simulation."""

    package_file = DATA_DIRECTORY / "packageCSV.csv"
    address_file = DATA_DIRECTORY / "addressCSV.csv"
    distance_file = DATA_DIRECTORY / "distanceCSV.csv"

    package_table = load_packages(package_file)

    distance_service = DistanceService()
    distance_service.load_addresses(address_file)
    distance_service.load_distances(distance_file)

    truck_1, truck_2, truck_3 = create_trucks()

    assign_packages_to_trucks(
        truck_1,
        truck_2,
        truck_3,
        package_table
    )

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

    # A more accurate implementation should use the return time
    # of Truck 1 or Truck 2 as Truck 3's departure time.
    earliest_driver_return = min(
        truck_1.current_time,
        truck_2.current_time
    )

    if earliest_driver_return > truck_3.departure_time:
        truck_3.departure_time = earliest_driver_return
        truck_3.current_time = earliest_driver_return

        for package_id in truck_3.package_ids:
            package = package_table.get(package_id)
            package.departure_time = earliest_driver_return

    deliver_route(
        truck_3,
        package_table,
        distance_service
    )

    trucks = [truck_1, truck_2, truck_3]

    total_mileage = (
        truck_1.mileage
        + truck_2.mileage
        + truck_3.mileage
    )

    print(
        f"\nAll packages delivered. "
        f"Total mileage: {total_mileage:.1f}"
    )

    run_user_interface(package_table, trucks)


if __name__ == "__main__":
    main()