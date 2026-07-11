def assign_packages_to_trucks(
    truck_1,
    truck_2,
    truck_3,
    package_table
):
    """
    Loads packages onto trucks based on deadlines,
    delays, grouped deliveries, and truck restrictions.
    """

    truck_1_packages = [
        1, 4, 7, 8, 13, 14, 15, 16,
        19, 20, 21, 29, 30, 34, 37, 40
    ]

    truck_2_packages = [
        3, 6, 10, 11, 12, 17, 18, 23,
        25, 26, 27, 31, 32, 35, 36, 38
    ]

    truck_3_packages = [
        2, 5, 9, 22, 24, 28, 33, 39
    ]

    truck_1.load_packages(truck_1_packages, package_table)
    truck_2.load_packages(truck_2_packages, package_table)
    truck_3.load_packages(truck_3_packages, package_table)