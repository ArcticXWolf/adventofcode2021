from __future__ import annotations
import sys, os, re, json, itertools
import logging
from typing import Deque, Dict, Generator, List, Optional, Set, Tuple, Union

logging.basicConfig(format="%(message)s", level=logging.INFO)

filename = (
    sys.argv[1]
    if len(sys.argv) > 1
    else os.path.join(os.path.dirname(os.path.abspath(__file__)), "testinput")
)
COLORS_RED = "\x1b[38;5;9m"
COLOR_RESET = "\x1b[0m"


class TreeNode:
    left_element: TreeNode
    right_element: TreeNode
    value: Optional[int]
    parent: TreeNode

    def __init__(self, value: Optional[int] = None) -> None:
        self.left_element = None
        self.right_element = None
        self.parent = None
        self.value = value

    @classmethod
    def parse_list(cls, input: List) -> TreeNode:
        left = None
        if isinstance(input[0], list):
            left = TreeNode.parse_list(input[0])
        elif isinstance(input[0], int):
            left = TreeNode(input[0])
        else:
            raise Exception("unknown type for left pair %s", input[0])

        right = None
        if isinstance(input[1], list):
            right = TreeNode.parse_list(input[1])
        elif isinstance(input[1], int):
            right = TreeNode(input[1])
        else:
            raise Exception("unknown type for right pair %s", input[1])

        node = TreeNode()
        node.set_left(left)
        node.set_right(right)

        return node

    @classmethod
    def sum(cls, left_summand: TreeNode, right_summand: TreeNode) -> TreeNode:
        if left_summand == None and right_summand != None:
            return right_summand
        if right_summand == None and left_summand != None:
            return left_summand

        new_tree = TreeNode()
        new_tree.set_left(left_summand)
        new_tree.set_right(right_summand)

        # reduce

        return new_tree

    def set_left(self, element: TreeNode) -> None:
        self.left_element = element
        element.parent = self

    def set_right(self, element: TreeNode) -> None:
        self.right_element = element
        element.parent = self

    def is_leaf(self) -> bool:
        return self.left_element == None and self.right_element == None

    def is_root(self) -> bool:
        return self.parent == None

    def magnitude(self) -> int:
        if self.is_leaf():
            return self.value

        magnitude = 0
        if self.left_element != None:
            magnitude += 3 * self.left_element.magnitude()
        if self.right_element != None:
            magnitude += 2 * self.right_element.magnitude()
        return magnitude

    def depth(self) -> int:
        if self.is_root():
            return 0

        return self.parent.depth() + 1

    def subtree_depth(self) -> int:
        if self.is_leaf():
            return 1

        subtree_depth = 0
        if self.left_element != None:
            subtree_depth = max(subtree_depth, self.left_element.subtree_depth())
        if self.right_element != None:
            subtree_depth = max(subtree_depth, self.right_element.subtree_depth())
        return subtree_depth + 1

    def get_leaves(self) -> List[TreeNode]:
        if self.is_leaf():
            return [self]

        leaf_list = []

        if self.left_element != None:
            leaf_list.extend(self.left_element.get_leaves())
        if self.right_element != None:
            leaf_list.extend(self.right_element.get_leaves())

        return leaf_list

    def exploding_leaves_with_index(self) -> List[Tuple[int, TreeNode]]:
        return [(i, x) for i, x in enumerate(self.get_leaves()) if x.depth() > 4]

    def splitting_leaves_with_index(self) -> List[Tuple[int, TreeNode]]:
        return [(i, x) for i, x in enumerate(self.get_leaves()) if x.value >= 10]

    def reduce(self) -> None:
        while True:
            if len(self.exploding_leaves_with_index()) > 0:
                self.explode()
                logging.debug(
                    "after explode:  %s, leaflist %s",
                    str(self),
                    [(x.value, x.depth()) for x in self.get_leaves()],
                )
                continue
            if len(self.splitting_leaves_with_index()) > 0:
                self.split()
                logging.debug(
                    "after split:    %s",
                    str(self),
                )
                continue

            # done
            break

    def explode(self) -> None:
        exploding_index, exploding_leaf = self.exploding_leaves_with_index()[0]
        # exploding leaf will be the left one of the exploding pair
        exploding_node = exploding_leaf.parent

        # add left
        if exploding_index - 1 >= 0:
            self.get_leaves()[
                exploding_index - 1
            ].value += exploding_node.left_element.value

        # add right
        if exploding_index + 2 < len(self.get_leaves()):
            self.get_leaves()[
                exploding_index + 2
            ].value += exploding_node.right_element.value

        # replace with 0
        if exploding_node.parent.left_element == exploding_node:
            exploding_node.parent.set_left(TreeNode(0))
        elif exploding_node.parent.right_element == exploding_node:
            exploding_node.parent.set_right(TreeNode(0))

    def split(self) -> None:
        _, splitting_leaf = self.splitting_leaves_with_index()[0]
        # new pair
        new_subtree = TreeNode()
        new_subtree.set_left(TreeNode(splitting_leaf.value // 2))
        new_subtree.set_right(TreeNode((splitting_leaf.value + 1) // 2))

        # replace leaf
        if splitting_leaf.parent.left_element == splitting_leaf:
            splitting_leaf.parent.set_left(new_subtree)
        elif splitting_leaf.parent.right_element == splitting_leaf:
            splitting_leaf.parent.set_right(new_subtree)

    def __str__(self) -> str:
        if self.is_leaf():
            return f"{self.value}"
        return f"({str(self.left_element)},{self.right_element})"


def main():
    # part 1
    with open(filename, "r") as f:
        trees = [
            TreeNode.parse_list(json.loads(line.strip())) for line in f.readlines()
        ]

        current_sum = None
        for index, tree in enumerate(trees):
            current_sum = TreeNode.sum(current_sum, tree)
            logging.debug(
                "after addition: %s, depth %d, leaflist %s",
                str(current_sum),
                current_sum.subtree_depth(),
                [(x.value, x.depth()) for x in current_sum.get_leaves()],
            )
            current_sum.reduce()
        logging.info("Result sum: %s", str(current_sum))
        logging.info("Result magnitude: %d", current_sum.magnitude())

    # part 2
    with open(filename, "r") as f:
        lines = [line.strip() for line in f.readlines()]
        highest_sum = None
        highest_sum_magnitude = 0
        for x, y in list(itertools.permutations(lines, 2)):
            current_sum = TreeNode.sum(
                TreeNode.parse_list(json.loads(x)), TreeNode.parse_list(json.loads(y))
            )
            current_sum.reduce()
            logging.debug(
                "Mag: %d, x=%s, y=%s, sum=%s",
                current_sum.magnitude(),
                x,
                y,
                str(current_sum),
            )
            if current_sum.magnitude() > highest_sum_magnitude:
                highest_sum_magnitude = current_sum.magnitude()
                highest_sum = (x, y, current_sum)
        logging.info(
            "Highest magnitude %d with x=%s and y=%s",
            highest_sum_magnitude,
            highest_sum[0],
            highest_sum[1],
        )


main()