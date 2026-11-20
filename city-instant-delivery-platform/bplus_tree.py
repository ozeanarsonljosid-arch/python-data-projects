import os
import json


class BPlusNode:
    def __init__(self, is_leaf=False):
        self.is_leaf = is_leaf
        self.keys = []
        self.children = []  # child node ids for internal; values for leaf
        self.next_leaf = None  # pointer to next leaf node (node id)
        self.node_id = None


class BPlusTree:
    """B+ Tree with simulated disk I/O. Supports insert, delete, search, range query."""

    def __init__(self, order=4, storage_dir="bplus_storage"):
        self.order = order  # max children for internal node
        self.max_keys = order - 1
        self.min_keys = (order - 1) // 2
        self.root_id = None
        self.next_node_id = 0
        self.storage_dir = storage_dir
        self.io_count = 0

        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)

    def _new_node_id(self):
        nid = self.next_node_id
        self.next_node_id += 1
        return nid

    def _write_node(self, node):
        """Simulate disk write."""
        self.io_count += 1
        data = {
            "is_leaf": node.is_leaf,
            "keys": node.keys,
            "children": node.children,
            "next_leaf": node.next_leaf,
            "node_id": node.node_id
        }
        path = os.path.join(self.storage_dir, f"node_{node.node_id}.json")
        with open(path, 'w') as f:
            json.dump(data, f)

    def _read_node(self, node_id):
        """Simulate disk read."""
        self.io_count += 1
        path = os.path.join(self.storage_dir, f"node_{node_id}.json")
        with open(path, 'r') as f:
            data = json.load(f)
        node = BPlusNode(is_leaf=data["is_leaf"])
        node.keys = data["keys"]
        node.children = data["children"]
        node.next_leaf = data["next_leaf"]
        node.node_id = data["node_id"]
        return node

    def _delete_node_file(self, node_id):
        path = os.path.join(self.storage_dir, f"node_{node_id}.json")
        if os.path.exists(path):
            os.remove(path)

    def reset_io_count(self):
        self.io_count = 0

    def search(self, key):
        """Search for a key, return value or None."""
        if self.root_id is None:
            return None
        node = self._read_node(self.root_id)
        while not node.is_leaf:
            idx = self._find_child_index(node, key)
            node = self._read_node(node.children[idx])
        for i, k in enumerate(node.keys):
            if k == key:
                return node.children[i]
        return None

    def range_query(self, low, high):
        """Return all (key, value) pairs where low <= key <= high."""
        if self.root_id is None:
            return []
        node = self._read_node(self.root_id)
        while not node.is_leaf:
            idx = self._find_child_index(node, low)
            node = self._read_node(node.children[idx])

        results = []
        while node is not None:
            for i, k in enumerate(node.keys):
                if k > high:
                    return results
                if k >= low:
                    results.append((k, node.children[i]))
            if node.next_leaf is not None:
                node = self._read_node(node.next_leaf)
            else:
                break
        return results

    def insert(self, key, value):
        """Insert a key-value pair."""
        if self.root_id is None:
            root = BPlusNode(is_leaf=True)
            root.node_id = self._new_node_id()
            root.keys = [key]
            root.children = [value]
            self.root_id = root.node_id
            self._write_node(root)
            return

        result = self._insert_recursive(self.root_id, key, value)
        if result is not None:
            new_key, new_child_id = result
            new_root = BPlusNode(is_leaf=False)
            new_root.node_id = self._new_node_id()
            new_root.keys = [new_key]
            new_root.children = [self.root_id, new_child_id]
            self.root_id = new_root.node_id
            self._write_node(new_root)

    def _insert_recursive(self, node_id, key, value):
        node = self._read_node(node_id)

        if node.is_leaf:
            idx = 0
            while idx < len(node.keys) and node.keys[idx] < key:
                idx += 1
            if idx < len(node.keys) and node.keys[idx] == key:
                node.children[idx] = value
                self._write_node(node)
                return None
            node.keys.insert(idx, key)
            node.children.insert(idx, value)
            if len(node.keys) > self.max_keys:
                return self._split_leaf(node)
            self._write_node(node)
            return None
        else:
            idx = self._find_child_index(node, key)
            result = self._insert_recursive(node.children[idx], key, value)
            if result is None:
                return None
            new_key, new_child_id = result
            node.keys.insert(idx, new_key)
            node.children.insert(idx + 1, new_child_id)
            if len(node.keys) > self.max_keys:
                return self._split_internal(node)
            self._write_node(node)
            return None

    def _split_leaf(self, node):
        mid = len(node.keys) // 2
        new_leaf = BPlusNode(is_leaf=True)
        new_leaf.node_id = self._new_node_id()
        new_leaf.keys = node.keys[mid:]
        new_leaf.children = node.children[mid:]
        new_leaf.next_leaf = node.next_leaf

        node.keys = node.keys[:mid]
        node.children = node.children[:mid]
        node.next_leaf = new_leaf.node_id

        self._write_node(node)
        self._write_node(new_leaf)
        return (new_leaf.keys[0], new_leaf.node_id)

    def _split_internal(self, node):
        mid = len(node.keys) // 2
        up_key = node.keys[mid]

        new_node = BPlusNode(is_leaf=False)
        new_node.node_id = self._new_node_id()
        new_node.keys = node.keys[mid + 1:]
        new_node.children = node.children[mid + 1:]

        node.keys = node.keys[:mid]
        node.children = node.children[:mid + 1]

        self._write_node(node)
        self._write_node(new_node)
        return (up_key, new_node.node_id)

    def delete(self, key):
        """Delete a key from the tree."""
        if self.root_id is None:
            return False
        result = self._delete_recursive(self.root_id, key)
        if result is None:
            return False
        root = self._read_node(self.root_id)
        if not root.is_leaf and len(root.keys) == 0:
            old_root_id = self.root_id
            self.root_id = root.children[0]
            self._delete_node_file(old_root_id)
        return True

    def _delete_recursive(self, node_id, key):
        node = self._read_node(node_id)

        if node.is_leaf:
            if key not in node.keys:
                return None
            idx = node.keys.index(key)
            node.keys.pop(idx)
            node.children.pop(idx)
            self._write_node(node)
            return True
        else:
            idx = self._find_child_index(node, key)
            result = self._delete_recursive(node.children[idx], key)
            if result is None:
                return None
            child = self._read_node(node.children[idx])
            min_keys = self.min_keys if not child.is_leaf else (self.max_keys + 1) // 2
            if len(child.keys) < min_keys:
                self._rebalance(node, idx)
            return True

    def _rebalance(self, parent, child_idx):
        child = self._read_node(parent.children[child_idx])

        # Try borrow from left sibling
        if child_idx > 0:
            left = self._read_node(parent.children[child_idx - 1])
            min_keys = self.min_keys if not left.is_leaf else (self.max_keys + 1) // 2
            if len(left.keys) > min_keys:
                if child.is_leaf:
                    child.keys.insert(0, left.keys.pop())
                    child.children.insert(0, left.children.pop())
                    parent.keys[child_idx - 1] = child.keys[0]
                else:
                    child.keys.insert(0, parent.keys[child_idx - 1])
                    parent.keys[child_idx - 1] = left.keys.pop()
                    child.children.insert(0, left.children.pop())
                self._write_node(child)
                self._write_node(left)
                self._write_node(parent)
                return

        # Try borrow from right sibling
        if child_idx < len(parent.children) - 1:
            right = self._read_node(parent.children[child_idx + 1])
            min_keys = self.min_keys if not right.is_leaf else (self.max_keys + 1) // 2
            if len(right.keys) > min_keys:
                if child.is_leaf:
                    child.keys.append(right.keys.pop(0))
                    child.children.append(right.children.pop(0))
                    parent.keys[child_idx] = right.keys[0]
                else:
                    child.keys.append(parent.keys[child_idx])
                    parent.keys[child_idx] = right.keys.pop(0)
                    child.children.append(right.children.pop(0))
                self._write_node(child)
                self._write_node(right)
                self._write_node(parent)
                return

        # Merge
        if child_idx > 0:
            left = self._read_node(parent.children[child_idx - 1])
            if child.is_leaf:
                left.keys.extend(child.keys)
                left.children.extend(child.children)
                left.next_leaf = child.next_leaf
            else:
                left.keys.append(parent.keys[child_idx - 1])
                left.keys.extend(child.keys)
                left.children.extend(child.children)
            parent.keys.pop(child_idx - 1)
            parent.children.pop(child_idx)
            self._delete_node_file(child.node_id)
            self._write_node(left)
            self._write_node(parent)
        else:
            right = self._read_node(parent.children[child_idx + 1])
            if child.is_leaf:
                child.keys.extend(right.keys)
                child.children.extend(right.children)
                child.next_leaf = right.next_leaf
            else:
                child.keys.append(parent.keys[child_idx])
                child.keys.extend(right.keys)
                child.children.extend(right.children)
            parent.keys.pop(child_idx)
            parent.children.pop(child_idx + 1)
            self._delete_node_file(right.node_id)
            self._write_node(child)
            self._write_node(parent)

    def update(self, key, new_value):
        """Update value for an existing key."""
        if self.root_id is None:
            return False
        node = self._read_node(self.root_id)
        while not node.is_leaf:
            idx = self._find_child_index(node, key)
            node = self._read_node(node.children[idx])
        for i, k in enumerate(node.keys):
            if k == key:
                node.children[i] = new_value
                self._write_node(node)
                return True
        return False

    def _find_child_index(self, node, key):
        """Find which child to follow for the given key."""
        idx = 0
        while idx < len(node.keys) and key >= node.keys[idx]:
            idx += 1
        return idx

    def clear_storage(self):
        """Remove all storage files."""
        if os.path.exists(self.storage_dir):
            for f in os.listdir(self.storage_dir):
                os.remove(os.path.join(self.storage_dir, f))
            os.rmdir(self.storage_dir)
        self.root_id = None
        self.next_node_id = 0
        self.io_count = 0
