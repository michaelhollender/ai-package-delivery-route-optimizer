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
        """Loads a package onto the truck if space is available."""

        if len(self.package_ids) >= self.max_packages:
            print(f"Truck {self.truck_id} is full.")
            return False
        
        package = package_table.get(package_id)

        if package is None:
            print(f"Package {package_id} was not found.")
            return False

        if package_id in self.package_ids:
            return False
        
        self.package_ids.append(package_id)
        package.truck_id = self.truck_id
        package.departure_time = self.departure_time
        package.status = "En Route"

        return True

    def load_packages(self, package_ids, package_table):
        """Loads a list of assigned package IDs."""

        for package_id in package_ids:
            self.load_package(package_id, package_table)

    def has_undelivered_packages(self, package_table):
        """Checks whether the truck has packages left to deliver."""

        for package_id in self.package_ids:
            package = package_table.get(package_id)

            if package.status != "Delivered":
                return True
        
        return False
    
    def get_undelivered_packages(self, package_table):
        """Returns the truck's undelivered package objects."""

        packages = []

        for package_id in self.package_ids:
            package = package_table.get(package_id)

            if package is not None and package.status != "Delivered":
                packages.append(package)

            return packages

    def travel(self, destination, distance):
        """Updates truck time, mileage, and location."""

        travel_hours = distance / self.AVERAGE_SPEED
        travel_seconds = travel_hours * 36000

        self.current_time += timedelta(seconds=travel_seconds)
        self.mileage += distance
        self.current_location = destination

    def __str__(self):
        return (
            f"Truck {self.truck_id} | "
            f"Packages: {len(self.package_ids)}/{self.max_packages} | "
            f"Location: {self.current_location} | "
            f"Mileage: {self.mileage:.1f}"
        )
    