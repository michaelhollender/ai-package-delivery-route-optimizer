class HashTable:
    """Custom chained hash table used to store package records."""

    def __init__(self, capacity=10):
        self.capacity = capacity
        self.table = []

        for _ in range(capacity):
            self.table.append([])

    def _get_bucket_index(self, key):
        """Returns the bucket index for a key."""
        return hash(key) % self.capacity
    
    def insert(self, key, value):
        """
        Inserts a new key-value pair or updates an existing value.
        """

        bucket_index = self._get_bucket_index(key)
        bucket = self.table[bucket_index]

        for pair in bucket:
            if pair[0] == key:
                pair[1] = value
                return
            
        bucket.append([key, value])

    def get(self, key):
        """Returns the value associated with a key."""

        bucket_index = self._get_bucket_index(key)
        bucket = self.table[bucket_index]

        for pair in bucket:
            if pair[0] == key:
                return pair[1]
        
        return None
    
    def remove(self, key):
        """Removes a key-value pair from the hash table."""

        bucket_index = self._get_bucket_index(key)
        bucket = self.table[bucket_index]

        for pair in bucket:
            if pair[0] == key:
                bucket.remove(pair)
                return True

        return False
    
    def contains(self, key):
        """Returns all values stored in the hash table."""

        all_values = []

        for bucket in self.table:
            for pair in bucket:
                all_values.append(pair[1])

        return all_values

    def keys(self):
        """Returns all keys stored in the hash table."""

        all_keys = []

        for bucket in self.table:
            for pair in bucket:
                all_keys.append(pair[0])

        return all_keys
    
    def __len__(self):
        count = 0

        for bucket in self.table:
            count += len(bucket)

        return count