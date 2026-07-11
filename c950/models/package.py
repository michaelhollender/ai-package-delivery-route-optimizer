from datetime import timedelta

class Package:
    """Stores delivery information for one package."""

    def __init__(
            self,
            package_id,
            address,
            city,
            state,
            zip_code,
            deadline,
            weight,
            notes="",
            status="At Hub",
            truck_id=None,
            hub_arrival_time=None,
            departure_time=None,
            delivery_time=None
    ):
        
        self.package_id = int(package_id)
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.deadline = deadline
        self.weight = weight
        self.notes = notes
        self.status = status
        self.truck_id = truck_id
        self.hub_arrival_time = hub_arrival_time
        self.departure_time = departure_time
        self.delivery_time = delivery_time

    def get_status_at_time(self, lookup_time):
        """Returns the package status at a requested time."""

        if (
            self.delivery_time is not Non
            and lookup_time >= self.delivery_time
        ):
            return "Delivered"
        
        if (
            self.departure_time is not None
            and lookup_time >= self.departure_time
        ):
            return "En Route"
        
        if (
            self.hub_arrival_time is not None
            and lookup_time < self.hub_arrival_time
        ):
            return "Delayed"
        
        return "At Hub"
    
    def __str__(self):
        return (
            f"Package {self.package_id} | "
            f"{self.address}, {self.city}, {self.state} "
            f"{self.zip_code} | "
            f"Deadline: {self.deadline} | "
            f"Weight: {self.weight} | "
            f"Status: {self.status}"
        )
    