from datetime import timedelta


PACKAGE_9_CORRECTION_TIME = timedelta(
    hours=10,
    minutes=20
)

PACKAGE_9_CORRECT_ADDRESS = "410 S State St"
PACKAGE_9_CORRECT_CITY = "Salt Lake City"
PACKAGE_9_CORRECT_STATE = "UT"
PACKAGE_9_CORRECT_ZIP = "84111"


def apply_package_9_correction(
    package_table,
    current_time
):
    """
    Updates Package 9 only after WGUPS receives
    the corrected address at 10:20 AM.
    """

    if current_time < PACKAGE_9_CORRECTION_TIME:
        return

    package_9 = package_table.get(9)

    if package_9 is None:
        return

    package_9.address = PACKAGE_9_CORRECT_ADDRESS
    package_9.city = PACKAGE_9_CORRECT_CITY
    package_9.state = PACKAGE_9_CORRECT_STATE
    package_9.zip_code = PACKAGE_9_CORRECT_ZIP


def package_is_available(
    package,
    truck
):
    """
    Returns True when a package is eligible to be
    considered for delivery.
    """

    if package.status == "Delivered":
        return False

    # Delayed packages cannot be delivered before
    # they arrive at the hub.
    if (
        package.hub_arrival_time is not None
        and truck.current_time
        < package.hub_arrival_time
    ):
        return False

    # WGUPS does not know Package 9's correct address
    # before 10:20 AM.
    if (
        package.package_id == 9
        and truck.current_time
        < PACKAGE_9_CORRECTION_TIME
    ):
        return False

    return True


def get_deadline_value(package):
    """
    Converts a package deadline into a timedelta.

    End-of-day packages receive a late time so that
    packages with specific deadlines are prioritized.
    """

    if (
        package.deadline is None
        or package.deadline == ""
        or package.deadline.upper() == "EOD"
    ):
        return timedelta(
            hours=23,
            minutes=59
        )

    deadline_text = package.deadline.strip().upper()

    try:
        clock_time, period = deadline_text.split()

        hour_text, minute_text = (
            clock_time.split(":")
        )

        hour = int(hour_text)
        minute = int(minute_text)

        if period == "PM" and hour != 12:
            hour += 12

        if period == "AM" and hour == 12:
            hour = 0

        return timedelta(
            hours=hour,
            minutes=minute
        )

    except ValueError:
        return timedelta(
            hours=23,
            minutes=59
        )


def select_next_package(
    truck,
    package_table,
    distance_service
):
    """
    Selects the next package using a constraint-aware
    nearest neighbor algorithm.

    Eligible packages with specific deadlines are
    considered before end-of-day packages. The nearest
    package in the selected candidate group is chosen.
    """

    candidates = []

    undelivered_packages = (
        truck.get_undelivered_packages(
            package_table
        )
    )

    for package in undelivered_packages:
        if package_is_available(
            package,
            truck
        ):
            candidates.append(package)

    if not candidates:
        return None

    deadline_packages = []

    for package in candidates:
        if (
            package.deadline is not None
            and package.deadline.upper() != "EOD"
        ):
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

        elif (
            distance == nearest_distance
            and nearest_package is not None
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
    """
    Delivers every eligible package on the truck
    that matches the current delivery address.
    """

    delivered_packages = []

    for package_id in truck.package_ids:
        package = package_table.get(package_id)

        if package is None:
            continue

        if package.status == "Delivered":
            continue

        if package.address != delivery_address:
            continue

        if not package_is_available(
            package,
            truck
        ):
            continue

        package.status = "Delivered"
        package.delivery_time = truck.current_time

        delivered_packages.append(package)

    return delivered_packages


def deliver_route(
    truck,
    package_table,
    distance_service
):
    """
    Delivers all assigned packages using the
    constraint-aware nearest neighbor algorithm.
    """

    print()
    print("=" * 65)

    print(
        f"Truck {truck.truck_id} departing at "
        f"{format_time(truck.departure_time)}"
    )

    print("=" * 65)

    while truck.has_undelivered_packages(
        package_table
    ):
        # The correction is applied only when the
        # simulated truck time reaches 10:20 AM.
        if (
            truck.current_time
            >= PACKAGE_9_CORRECTION_TIME
        ):
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
            next_available_time = (
                find_next_available_time(
                    truck,
                    package_table
                )
            )

            if (
                next_available_time is not None
                and next_available_time
                > truck.current_time
            ):
                print(
                    f"Truck {truck.truck_id} waiting until "
                    f"{format_time(next_available_time)} "
                    f"for an eligible package."
                )

                truck.current_time = (
                    next_available_time
                )

                continue

            print(
                f"Truck {truck.truck_id} has no "
                f"eligible packages remaining."
            )

            break

        distance = distance_service.get_distance(
            truck.current_location,
            next_package.address
        )

        previous_location = truck.current_location

        truck.travel(
            next_package.address,
            distance
        )

        delivered_packages = (
            deliver_packages_at_address(
                truck,
                package_table,
                truck.current_location
            )
        )

        delivered_ids = [
            package.package_id
            for package in delivered_packages
        ]

        print()

        print(
            f"Truck {truck.truck_id}: "
            f"{previous_location} -> "
            f"{truck.current_location}"
        )

        print(
            f"Distance traveled: "
            f"{distance:.1f} miles"
        )

        print(
            f"Arrival time: "
            f"{format_time(truck.current_time)}"
        )

        print(
            f"Packages delivered: "
            f"{delivered_ids}"
        )

        print(
            f"Current truck mileage: "
            f"{truck.mileage:.1f} miles"
        )

    if not truck.has_undelivered_packages(
        package_table
    ):
        return_to_hub(
            truck,
            distance_service
        )


def find_next_available_time(
    truck,
    package_table
):
    """
    Finds the next time when an unavailable package
    assigned to the truck becomes eligible.
    """

    next_times = []

    undelivered_packages = (
        truck.get_undelivered_packages(
            package_table
        )
    )

    for package in undelivered_packages:
        if (
            package.hub_arrival_time is not None
            and package.hub_arrival_time
            > truck.current_time
        ):
            next_times.append(
                package.hub_arrival_time
            )

        if (
            package.package_id == 9
            and PACKAGE_9_CORRECTION_TIME
            > truck.current_time
        ):
            next_times.append(
                PACKAGE_9_CORRECTION_TIME
            )

    if not next_times:
        return None

    return min(next_times)


def return_to_hub(
    truck,
    distance_service
):
    """Returns the truck to the WGUPS hub."""

    if (
        truck.current_location
        == truck.hub_address
    ):
        return

    distance = distance_service.get_distance(
        truck.current_location,
        truck.hub_address
    )

    previous_location = truck.current_location

    truck.travel(
        truck.hub_address,
        distance
    )

    print()

    print(
        f"Truck {truck.truck_id} returning "
        f"from {previous_location} to the hub."
    )

    print(
        f"Return distance: "
        f"{distance:.1f} miles"
    )

    print(
        f"Hub arrival time: "
        f"{format_time(truck.current_time)}"
    )

    print(
        f"Truck {truck.truck_id} total mileage: "
        f"{truck.mileage:.1f} miles"
    )


def format_time(time_value):
    """Formats a timedelta as a readable clock time."""

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

    period = (
        "PM"
        if hours >= 12
        else "AM"
    )

    display_hour = hours % 12

    if display_hour == 0:
        display_hour = 12

    return (
        f"{display_hour:02d}:"
        f"{minutes:02d}:"
        f"{seconds:02d} {period}"
    )