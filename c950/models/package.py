from datetime import timedelta


PACKAGE_9_CORRECTION_TIME = timedelta(
    hours=10,
    minutes=20
)

PACKAGE_9_ORIGINAL_ADDRESS = "300 State St"
PACKAGE_9_ORIGINAL_CITY = "Salt Lake City"
PACKAGE_9_ORIGINAL_STATE = "UT"
PACKAGE_9_ORIGINAL_ZIP = "84103"

PACKAGE_9_CORRECT_ADDRESS = "410 S State St"
PACKAGE_9_CORRECT_CITY = "Salt Lake City"
PACKAGE_9_CORRECT_STATE = "UT"
PACKAGE_9_CORRECT_ZIP = "84111"


class Package:
    """Stores delivery information and status for one package."""

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
        """
        Returns package status at a requested time.
        """

        if (
            self.hub_arrival_time is not None
            and lookup_time < self.hub_arrival_time
        ):
            return (
                f"Delayed until "
                f"{format_time(self.hub_arrival_time)}"
            )

        if (
            self.delivery_time is not None
            and lookup_time >= self.delivery_time
        ):
            return (
                f"Delivered at "
                f"{format_time(self.delivery_time)}"
            )

        if (
            self.departure_time is not None
            and lookup_time >= self.departure_time
        ):
            return (
                f"En Route since "
                f"{format_time(self.departure_time)}"
            )

        if self.hub_arrival_time is not None:
            return (
                f"At Hub since "
                f"{format_time(self.hub_arrival_time)}"
            )

        return "At Hub"

    def get_address_at_time(self, lookup_time):
        """
        Returns the address known at the requested time.

        Package 9 did not have its corrected address
        until 10:20 AM.
        """

        if self.package_id == 9:

            if lookup_time < PACKAGE_9_CORRECTION_TIME:
                return (
                    PACKAGE_9_ORIGINAL_ADDRESS,
                    PACKAGE_9_ORIGINAL_CITY,
                    PACKAGE_9_ORIGINAL_STATE,
                    PACKAGE_9_ORIGINAL_ZIP
                )

            return (
                PACKAGE_9_CORRECT_ADDRESS,
                PACKAGE_9_CORRECT_CITY,
                PACKAGE_9_CORRECT_STATE,
                PACKAGE_9_CORRECT_ZIP
            )

        return (
            self.address,
            self.city,
            self.state,
            self.zip_code
        )

    def __str__(self):
        return (
            f"Package {self.package_id} | "
            f"{self.address}, {self.city}, "
            f"{self.state} {self.zip_code} | "
            f"Deadline: {self.deadline} | "
            f"Weight: {self.weight} | "
            f"Status: {self.status}"
        )


def format_time(time_value):
    """
    Formats timedelta as 12-hour clock time.
    """

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

    period = "PM" if hours >= 12 else "AM"

    display_hour = hours % 12

    if display_hour == 0:
        display_hour = 12

    return (
        f"{display_hour:02d}:"
        f"{minutes:02d}:"
        f"{seconds:02d} {period}"
    ) 