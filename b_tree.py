# Implementation of B+-tree functionality.

from index import *
from copy import deepcopy

class b_tree:

    #returns 2 if all list items are ints, 1 if there is a mix of int and None, and 0 if all items are None
    @staticmethod
    def all_or_none(list):
        num_none = 0
        num_non_none = 0
        for x in list:
            if x is None:
                num_none += 1
            else:
                num_non_none += 1
        if num_none == 0:
            return 2
        elif num_non_none == 0:
            return 0
        else:
            return 1

    def is_leaf(node):
        p = node.pointers.pointers
        if p[0] is None and p[1] is None:
            return True
        else:
            return False

    # Returns a B+-tree obtained by inserting a key into a pre-existing
    # B+-tree index if the key is not already there. If it already exists,
    # the return value is equivalent to the original, input tree.
    #
    # Complexity: Guaranteed to be asymptotically linear in the height of the tree
    # Because the tree is balanced, it is also asymptotically logarithmic in the
    # number of keys that already exist in the index.
    @staticmethod
    def InsertIntoIndex(index, key):

        if (not b_tree.all_or_none(index.root.keys.keys)):
            root_node = Node(KeySet([key, None]),
                             PointerSet([None, None, None]))
            index.root = root_node
            return index
        is_done = False
        visited_nodes = []
        cur_node = index.root
        cur_keys = cur_node.keys.keys
        cur_pointers = cur_node.pointers.pointers
        if b_tree.LookupKeyInIndex(index, key) == True:
            return index
        else:
            while cur_pointers[0] is not None and cur_pointers[1] is not None:
                visited_nodes.append(cur_node)
                next_pointer = None
                if key < cur_keys[0]:
                    next_pointer = cur_pointers[0]
                elif key >= cur_keys[0] and (
                        cur_keys[1] is None or key < cur_keys[1] or
                    (cur_pointers[2] is None and key > cur_keys[1])):
                    next_pointer = cur_pointers[1]
                elif key >= cur_keys[1]:
                    next_pointer = cur_pointers[2]
                cur_node = next_pointer
                cur_keys = cur_node.keys.keys
                cur_pointers = cur_node.pointers.pointers
            # End of branch navigation
            if key == cur_keys[0] or key == cur_keys[1]:
                return index
            if b_tree.all_or_none(cur_keys) == 1:
                # Key can be inserted without splits
                if b_tree.all_or_none(cur_keys) == False:
                    cur_keys[0] = key
                elif cur_keys[0] > key:
                    cur_keys[1] = cur_keys[0]
                    cur_keys[0] = key
                elif cur_keys[0] < key:
                    cur_keys[1] = key
            elif b_tree.all_or_none(cur_keys) == 2:
                #insert requires a split
                new_node = None
                search_key = None
                if key < cur_keys[0]:
                    search_key = cur_keys[0]
                    new_node = Node(
                        KeySet([search_key, cur_keys[1]]),
                        PointerSet(([None, None, cur_pointers[2]])))
                    cur_keys[1] = None
                    cur_keys[0] = key
                    cur_pointers[2] = new_node

                elif key > cur_keys[0] and key < cur_keys[1]:
                    search_key = key
                    new_node = Node(KeySet([search_key, cur_keys[1]]),
                                    PointerSet([None, None, cur_pointers[2]]))
                    cur_keys[1] = None
                    cur_pointers[2] = new_node

                elif key > cur_keys[1]:
                    search_key = cur_keys[1]
                    new_node = Node(KeySet([search_key, key]),
                                    PointerSet([None, None, cur_pointers[2]]))
                    cur_pointers[2] = new_node
                    cur_keys[1] = None

                elif key == cur_keys[0] or key == cur_keys[1]:
                    return index
                # finished inserting and splitting
                while is_done == False:
                    if (len(visited_nodes) > 0):
                        cur_node = visited_nodes.pop()
                        cur_pointers = cur_node.pointers.pointers
                        cur_keys = cur_node.keys.keys
                    elif (len(visited_nodes) == 0):
                        child_1 = None
                        child_2 = None
                        if b_tree.is_leaf(cur_node):
                            child_1 = cur_node
                            child_2 = cur_pointers[2]
                        elif cur_node.keys.keys[0] < new_node.keys.keys[0]:
                            child_1 = cur_node
                            child_2 = new_node
                        elif cur_node.keys.keys[0] > new_node.keys.keys[0]:
                            child_1 = new_node
                            child_2 = cur_node
                        root_node = Node(KeySet([search_key, None]),
                                         PointerSet([child_1, child_2, None]))
                        index.root = root_node
                        return index
                    if b_tree.all_or_none(cur_pointers) == 1:
                        # search key can be inserted without splits
                        if search_key > cur_keys[0]:
                            cur_keys[1] = search_key
                            cur_pointers[2] = new_node
                        elif search_key < cur_keys[0]:
                            cur_keys[1] = cur_keys[0]
                            cur_pointers[2] = cur_pointers[1]
                            if new_node.keys.keys[0] > cur_pointers[
                                    0].keys.keys[0]:
                                cur_pointers[1] = new_node
                            else:
                                cur_pointers[1] = cur_pointers[0]
                                cur_pointers[0] = new_node

                            cur_keys[0] = search_key
                        is_done = True

                    elif b_tree.all_or_none(cur_pointers) == 2:
                        #split is required
                        if search_key < cur_keys[0]:
                            new_parent = Node(
                                KeySet([search_key, None]),
                                PointerSet([cur_pointers[0], new_node, None]))
                            search_key = cur_keys[0]
                            cur_keys[0] = cur_keys[1]
                            cur_keys[1] = None
                            cur_pointers[0] = cur_pointers[1]
                            cur_pointers[1] = cur_pointers[2]
                            cur_pointers[2] = None
                            new_node = new_parent
                        elif search_key > cur_keys[
                                0] and search_key < cur_keys[1]:
                            search_key = search_key
                            new_parent = Node(
                                KeySet([cur_keys[1], None]),
                                PointerSet([new_node, cur_pointers[2], None]))
                            new_node = new_parent

                        elif search_key > cur_keys[1]:
                            new_parent = Node(
                                KeySet([search_key, None]),
                                PointerSet([cur_pointers[2], new_node, None]))
                            search_key = cur_keys[1]
                            cur_pointers[2] = None
                            cur_keys[1] = None
                            new_node = new_parent

        return index

    # Returns a boolean that indicates whether a given key
    # is found among the leaves of a B+-tree index.
    #
    # Complexity: Guaranteed not to touch more nodes than the
    # height of the tree
    @staticmethod
    def LookupKeyInIndex(index, key):
        cur_node = index.root
        cur_keys = cur_node.keys.keys
        cur_pointers = cur_node.pointers.pointers
        while cur_pointers[0] is not None and cur_pointers[1] is not None:
            next_pointer = None
            if key < cur_keys[0]:
                next_pointer = cur_pointers[0]
            elif key >= cur_keys[0] and (
                    cur_keys[1] is None or key < cur_keys[1] or
                (cur_pointers[2] is None and key > cur_keys[1])):
                next_pointer = cur_pointers[1]
            elif key >= cur_keys[1]:
                next_pointer = cur_pointers[2]
            cur_node = next_pointer
            cur_keys = cur_node.keys.keys
            cur_pointers = cur_node.pointers.pointers
        if (cur_keys[0] is not None
                and cur_keys[0] == key) or (cur_keys[1] is not None
                                            and cur_keys[1] == key):
            return True

        return False

    # Returns a list of keys in a B+-tree index within the half-open
    # interval [lower_bound, upper_bound)
    #
    # Complexity: Guaranteed not to touch more nodes than the height
    # of the tree and the number of leaves overlapping the interval.
    @staticmethod
    def RangeSearchInIndex(index, lower_bound, upper_bound):
        if lower_bound == upper_bound:
            r = []
            return r

        key = lower_bound
        in_range = []
        cur_node = index.root
        cur_keys = cur_node.keys.keys
        cur_pointers = cur_node.pointers.pointers
        while cur_pointers[0] is not None and cur_pointers[1] is not None:
            next_pointer = None
            if key < cur_keys[0]:
                next_pointer = cur_pointers[0]
            elif key >= cur_keys[0] and (cur_keys[1] is None
                                         or key < cur_keys[1]):
                next_pointer = cur_pointers[1]
            elif (cur_pointers[2] is None and key > cur_keys[1]):
                next_pointer = cur_pointers[1]
            elif key >= cur_keys[1]:
                next_pointer = cur_pointers[2]
            elif key == cur_keys[0]:
                next_pointer = cur_pointers[1]
            cur_node = next_pointer
            cur_keys = cur_node.keys.keys
            cur_pointers = cur_node.pointers.pointers
        if cur_keys[0] is not None and cur_keys[0] >= key and cur_keys[
                0] < upper_bound:
            in_range.append(cur_keys[0])
        if cur_keys[1] is not None and cur_keys[1] >= key and cur_keys[
                1] < upper_bound:
            in_range.append(cur_keys[1])
        while True is not None:
            if cur_pointers[2] is not None:
                cur_node = cur_pointers[2]
            else:
                break
            cur_pointers = cur_node.pointers.pointers
            cur_keys = cur_node.keys.keys
            if cur_keys[0] is not None and cur_keys[0] < upper_bound:
                in_range.append(cur_keys[0])
            else:
                break
            if cur_keys[1] is not None and cur_keys[1] < upper_bound:
                in_range.append(cur_keys[1])
            elif cur_keys[1] is None:
                continue
            elif cur_keys[1] >= upper_bound:
                break

        return in_range
