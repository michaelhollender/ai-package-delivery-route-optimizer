from datetime import timedelta


PACKAGE_9_CORRECTION_TIME = timedelta(hours=10, minutes=20)
PACKAGE_9_CORRECT_ADDRESS = "410 S State St"
PACKAGE_9_CORRECT_CITY = "Salt Lake City"
PACKAGE_9_CORRECT_ZIP = "84111"


def apply_package_9_correction(package_table, current_time):
    """Updates Package 9 when its corrected address becomes available."""

    package_9 = package_table.get(9)

    if package_9 is None:
        return

    if current_time >= PACKAGE_9_CORRECTION_TIME:
        package_9.address = PACKAGE_9_CORRECT_ADDRESS
        package_9.city = PACKAGE_9_CORRECT_CITY
        package_9.zip_code = PACKAGE_9_CORRECT_ZIP


def package_is_available(package, truck):
    """Checks whether a package can currently be delivered."""

    if package.status == "Delivered":
        return False

    if (
        package.hub_arrival_time is not None
        and truck.current_time < package.hub_arrival_time
    ):
        return False

    if (
        package.package_id == 9
        and truck.current_time < PACKAGE_9_CORRECTION_TIME
    ):
        return False

    return True


def get_deadline_value(package):
    """
    Converts a package deadline into a sortable value.

    Earlier deadlines receive lower values. EOD receives a large value.
    """

    if package.deadline == "EOD":
        return timedelta(hours=23, minutes=59)

    time_text, period = package.deadline.split()
    hour, minute = time_text.split(":")

    hour = int(hour)
    minute = int(minute)

    if period.upper() == "PM" and hour != 12:
        hour += 12

    if period.upper() == "AM" and hour == 12:
        hour = 0

    return timedelta(hours=hour, minutes=minute)


def select_next_package(truck, package_table, distance_service):
    """
    Selects the next eligible package.

    Constraints are checked first. Among eligible packages, packages
    with deadlines are considered before EOD packages. The nearest
    package in the selected group is returned.
    """

    candidates = []

    for package in truck.get_undelivered_packages(package_table):
        if package_is_available(package, truck):
            candidates.append(package)

    if not candidates:
        return None

    deadline_packages = []

    for package in candidates:
        if package.deadline != "EOD":
            deadline_packages.append(package)

    if deadline_packages:
        candidate_group = deadline_packages
    else:
        candidate_group = candidates

    nearest_package = None
    nearest_distance = float("inf")

    for package in candidate_group:
        distance = distance_service.get_distance(
            truck.current_location,
            package.address
        )

        if distance < nearest_distance:
            nearest_distance = distance
            nearest_package = package

        elif distance == nearest_distance:
            if (
                nearest_package is not None
                and get_deadline_value(package)
                < get_deadline_value(nearest_package)
            ):
                nearest_package = package

    return nearest_package


def deliver_packages_at_address(
    truck,
    package_table,
    delivery_address
):
    """Delivers all packages on the truck for one address."""

    delivered_packages = []

    for package_id in truck.package_ids:
        package = package_table.get(package_id)

        if (
            package.status != "Delivered"
            and package.address == delivery_address
        ):
            package.status = "Delivered"
            package.delivery_time = truck.current_time
            delivered_packages.append(package)

    return delivered_packages


def deliver_route(truck, package_table, distance_service):
    """
    Delivers a truck's packages using the constraint-aware
    nearest neighbor algorithm.
    """

    while truck.has_undelivered_packages(package_table):
        apply_package_9_correction(
            package_table,
            truck.current_time
        )

        next_package = select_next_package(
            truck,
            package_table,
            distance_service
        )

        if next_package is None:
            print(
                f"Truck {truck.truck_id} has no eligible "
                f"packages at {format_time(truck.current_time)}."
            )
            break

        distance = distance_service.get_distance(
            truck.current_location,
            next_package.address
        )

        truck.travel(next_package.address, distance)

        delivered_packages = deliver_packages_at_address(
            truck,
            package_table,
            truck.current_location
        )

        delivered_ids = []

        for package in delivered_packages:
            delivered_ids.append(package.package_id)

        print(
            f"Truck {truck.truck_id} delivered "
            f"{delivered_ids} at "
            f"{format_time(truck.current_time)}"
        )

        print(
            f"Location: {truck.current_location} | "
            f"Distance: {distance:.1f} miles | "
            f"Truck mileage: {truck.mileage:.1f}"
        )

    return_to_hub(truck, distance_service)


def return_to_hub(truck, distance_service):
    """Returns a truck to the WGUPS hub."""

    if truck.current_location == truck.hub_address:
        return

    distance = distance_service.get_distance(
        truck.current_location,
        truck.hub_address
    )

    truck.travel(truck.hub_address, distance)

    print(
        f"Truck {truck.truck_id} returned to the hub at "
        f"{format_time(truck.current_time)}."
    )

    print(
        f"Truck {truck.truck_id} total mileage: "
        f"{truck.mileage:.1f}"
    )


def format_time(time_value):
    """Formats a timedelta as a readable clock time."""

    total_seconds = int(time_value.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"