from datetime import timedelta


class Truck:
    """Stores the state of one delivery truck."""

    AVERAGE_SPEED = 18.0

    def __init__(
        self,
        truck_id,
        departure_time,
        hub_address,
        max_packages=16
    ):
        self.truck_id = truck_id
        self.departure_time = departure_time
        self.current_time = departure_time
        self.current_location = hub_address
        self.hub_address = hub_address
        self.max_packages = max_packages
        self.package_ids = []
        self.mileage = 0.0

    def load_package(self, package_id, package_table):
        """Loads one package onto the truck."""

        if len(self.package_ids) >= self.max_packages:
            print(
                f"Truck {self.truck_id} is full. "
                f"Package {package_id} was not loaded."
            )
            return False

        package = package_table.get(package_id)

        if package is None:
            print(f"Package {package_id} was not found.")
            return False

        if package_id in self.package_ids:
            print(
                f"Package {package_id} is already loaded "
                f"on Truck {self.truck_id}."
            )
            return False

        self.package_ids.append(package_id)

        package.truck_id = self.truck_id
        package.status = "At Hub"

        # A package cannot leave before it arrives at the hub.
        if (
            package.hub_arrival_time is not None
            and package.hub_arrival_time > self.departure_time
        ):
            package.departure_time = package.hub_arrival_time
        else:
            package.departure_time = self.departure_time

        return True

    def load_packages(self, package_ids, package_table):
        """Loads multiple packages onto the truck."""

        for package_id in package_ids:
            self.load_package(
                package_id,
                package_table
            )

    def has_undelivered_packages(self, package_table):
        """Returns True if the truck has packages left to deliver."""

        for package_id in self.package_ids:
            package = package_table.get(package_id)

            if (
                package is not None
                and package.status != "Delivered"
            ):
                return True

        return False

    def get_undelivered_packages(self, package_table):
        """Returns all undelivered package objects on the truck."""

        undelivered_packages = []

        for package_id in self.package_ids:
            package = package_table.get(package_id)

            if (
                package is not None
                and package.status != "Delivered"
            ):
                undelivered_packages.append(package)

        return undelivered_packages

    def travel(self, destination, distance):
        """Updates the truck's time, mileage, and location."""

        travel_hours = distance / self.AVERAGE_SPEED
        travel_seconds = travel_hours * 3600

        self.current_time += timedelta(
            seconds=travel_seconds
        )

        self.mileage += distance
        self.current_location = destination

    def update_departure_time(
        self,
        new_departure_time,
        package_table
    ):
        """
        Updates the truck and package departure times.

        This is useful for Truck 3 because only two drivers
        are available.
        """

        self.departure_time = new_departure_time
        self.current_time = new_departure_time

        for package_id in self.package_ids:
            package = package_table.get(package_id)

            if package is None:
                continue

            if (
                package.hub_arrival_time is not None
                and package.hub_arrival_time
                > new_departure_time
            ):
                package.departure_time = (
                    package.hub_arrival_time
                )
            else:
                package.departure_time = (
                    new_departure_time
                )

    def __str__(self):
        return (
            f"Truck {self.truck_id} | "
            f"Packages: "
            f"{len(self.package_ids)}/"
            f"{self.max_packages} | "
            f"Location: {self.current_location} | "
            f"Mileage: {self.mileage:.1f}"
        )
    