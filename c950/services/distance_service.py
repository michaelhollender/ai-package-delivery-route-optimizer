import csv


class DistanceService:
    """Loads address data and retrieves direct distances."""

    def __init__(self):
        self.addresses = []
        self.address_to_index = {}
        self.distances = []

    def load_addresses(self, file_path):
        """Loads delivery addresses from the address CSV."""

        with open(file_path, mode="r", encoding="utf-8-sig") as file:
            reader = csv.reader(file)

            for index, row in enumerate(reader):
                if not row:
                    continue

                # Adjust this position if your address CSV has
                # the address in a different column.
                address = row[2].strip()

                self.addresses.append(address)
                self.address_to_index[address] = index

    def load_distances(self, file_path):
        """Loads the triangular distance table."""

        with open(file_path, mode="r", encoding="utf-8-sig") as file:
            reader = csv.reader(file)

            for row in reader:
                cleaned_row = []

                for value in row:
                    value = value.strip()

                    if value == "":
                        cleaned_row.append(None)
                    else:
                        cleaned_row.append(float(value))

                self.distances.append(cleaned_row)

    def get_address_index(self, address):
        """Returns the distance-table index for an address."""
        return self.address_to_index.get(address)

    def get_distance(self, address_1, address_2):
        """Returns the direct distance between two addresses."""

        if address_1 == address_2:
            return 0.0

        index_1 = self.get_address_index(address_1)
        index_2 = self.get_address_index(address_2)

        if index_1 is None:
            raise ValueError(f"Unknown address: {address_1}")

        if index_2 is None:
            raise ValueError(f"Unknown address: {address_2}")

        distance = self.distances[index_1][index_2]

        if distance is None:
            distance = self.distances[index_2][index_1]

        return float(distance)