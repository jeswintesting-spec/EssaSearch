from typing import List, Tuple, Dict

class TrieNode:
    """A node in the Trie data structure."""
    def __init__(self):
        self.children: Dict[str, 'TrieNode'] = {}
        self.is_word: bool = False
        self.word: str = ""

class Trie:
    """
    A Prefix Tree (Trie) used to store the vocabulary of the search engine.
    Allows for highly efficient fuzzy string matching using Levenshtein distance.
    """
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str):
        """Insert a word into the Trie."""
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_word = True
        node.word = word

    def search_fuzzy(self, word: str, max_edit_distance: int = 2) -> List[Tuple[str, int]]:
        """
        Find all words in the Trie that are within the max_edit_distance of the target word.
        Returns a list of tuples: (matched_word, edit_distance).
        
        This uses an optimization where we compute the Levenshtein distance DP matrix
        row-by-row as we traverse the Trie using DFS, allowing us to prune entire branches
        if the minimum edit distance exceeds our max_edit_distance.
        """
        results: List[Tuple[str, int]] = []
        
        # The initial DP row (comparing empty string to the target word)
        # e.g., for "apple", row is [0, 1, 2, 3, 4, 5]
        current_row = list(range(len(word) + 1))
        
        for char, child_node in self.root.children.items():
            self._search_recursive(child_node, char, word, current_row, results, max_edit_distance)
            
        # Sort results by edit distance (closest first)
        results.sort(key=lambda x: x[1])
        return results

    def _search_recursive(self, node: TrieNode, char: str, word: str, previous_row: List[int], results: List[Tuple[str, int]], max_cost: int):
        columns = len(word) + 1
        # The first column is the cost to delete all characters from the current prefix
        current_row = [previous_row[0] + 1]

        # Build the DP row for this specific character in the Trie
        for col in range(1, columns):
            insert_cost = current_row[col - 1] + 1
            delete_cost = previous_row[col] + 1
            
            # If characters match, replace cost is 0, else 1
            replace_cost = previous_row[col - 1] + (0 if word[col - 1] == char else 1)
            
            current_row.append(min(insert_cost, delete_cost, replace_cost))

        # If this node represents a complete word and the final edit distance <= max_cost
        if node.is_word and current_row[-1] <= max_cost:
            results.append((node.word, current_row[-1]))

        # PRUNING: Only traverse children if there is a possibility of finding a match.
        # If the minimum cost in the current row > max_cost, any further additions will
        # only increase the cost, so we can stop exploring this branch entirely.
        if min(current_row) <= max_cost:
            for child_char, child_node in node.children.items():
                self._search_recursive(child_node, child_char, word, current_row, results, max_cost)
