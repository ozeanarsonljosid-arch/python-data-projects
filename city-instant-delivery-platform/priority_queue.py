class PriorityQueue:
    """Min-heap based priority queue. Smaller priority value = higher priority."""

    def __init__(self):
        self._heap = []  # list of (priority, item_id, item)
        self._index_map = {}  # item_id -> index in heap
        self._size = 0

    def is_empty(self):
        return self._size == 0

    def size(self):
        return self._size

    def _swap(self, i, j):
        self._heap[i], self._heap[j] = self._heap[j], self._heap[i]
        self._index_map[self._heap[i][1]] = i
        self._index_map[self._heap[j][1]] = j

    def _sift_up(self, idx):
        while idx > 0:
            parent = (idx - 1) // 2
            if self._heap[idx][0] < self._heap[parent][0]:
                self._swap(idx, parent)
                idx = parent
            else:
                break

    def _sift_down(self, idx):
        while True:
            smallest = idx
            left = 2 * idx + 1
            right = 2 * idx + 2
            if left < self._size and self._heap[left][0] < self._heap[smallest][0]:
                smallest = left
            if right < self._size and self._heap[right][0] < self._heap[smallest][0]:
                smallest = right
            if smallest != idx:
                self._swap(idx, smallest)
                idx = smallest
            else:
                break

    def insert(self, item_id, priority, item=None):
        entry = (priority, item_id, item)
        self._heap.append(entry)
        self._index_map[item_id] = self._size
        self._size += 1
        self._sift_up(self._size - 1)

    def extract_min(self):
        if self._size == 0:
            return None
        top = self._heap[0]
        self._size -= 1
        if self._size > 0:
            self._heap[0] = self._heap[self._size]
            self._index_map[self._heap[0][1]] = 0
            self._heap.pop()
            self._sift_down(0)
        else:
            self._heap.pop()
        del self._index_map[top[1]]
        return top  # (priority, item_id, item)

    def peek(self):
        if self._size == 0:
            return None
        return self._heap[0]

    def update_priority(self, item_id, new_priority):
        if item_id not in self._index_map:
            return False
        idx = self._index_map[item_id]
        old_priority = self._heap[idx][0]
        self._heap[idx] = (new_priority, self._heap[idx][1], self._heap[idx][2])
        if new_priority < old_priority:
            self._sift_up(idx)
        else:
            self._sift_down(idx)
        return True

    def remove(self, item_id):
        if item_id not in self._index_map:
            return False
        idx = self._index_map[item_id]
        self._size -= 1
        if idx == self._size:
            self._heap.pop()
            del self._index_map[item_id]
        else:
            self._heap[idx] = self._heap[self._size]
            self._index_map[self._heap[idx][1]] = idx
            self._heap.pop()
            del self._index_map[item_id]
            self._sift_up(idx)
            self._sift_down(idx)
        return True

    def top_k(self, k):
        """Return top-k items without modifying the queue."""
        if k <= 0:
            return []
        temp = []
        results = []
        count = min(k, self._size)
        for _ in range(count):
            item = self.extract_min()
            results.append(item)
            temp.append(item)
        for priority, item_id, item in temp:
            self.insert(item_id, priority, item)
        return results

    def contains(self, item_id):
        return item_id in self._index_map
