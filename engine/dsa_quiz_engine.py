import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random

# ----------------------------------------------------------------------------
# DSA & LeetCode Assessment Question Bank (Easy, Medium, Hard)
# Mapped to iconic LeetCode coding patterns & algorithmic problems
# ----------------------------------------------------------------------------
QUESTION_BANK = [
    # ------------------ EASY LEETCODE PROBLEMS (12) ------------------
    {'id': 1, 'topic': 'Arrays & Hashing', 'difficulty': 'Easy', 'leetcode_ref': 'LeetCode 1 - Two Sum',
     'question': '[LeetCode 1 - Two Sum] What is the optimal time complexity to find two numbers that sum up to a target using a Hash Map?',
     'options': ['O(n^2)', 'O(n log n)', 'O(n)', 'O(1)'], 'answer': 2},

    {'id': 2, 'topic': 'Stacks', 'difficulty': 'Easy', 'leetcode_ref': 'LeetCode 20 - Valid Parentheses',
     'question': '[LeetCode 20 - Valid Parentheses] Which data structure is optimal to verify if open brackets are closed in the correct order?',
     'options': ['Queue', 'Stack', 'Min-Heap', 'Binary Search Tree'], 'answer': 1},

    {'id': 3, 'topic': 'Linked List', 'difficulty': 'Easy', 'leetcode_ref': 'LeetCode 21 - Merge Two Sorted Lists',
     'question': '[LeetCode 21 - Merge Two Sorted Lists] When merging two sorted linked lists of lengths m and n into a new list, what is the optimal time complexity?',
     'options': ['O(m + n)', 'O(m * n)', 'O(log(m + n))', 'O(1)'], 'answer': 0},

    {'id': 4, 'topic': 'Sliding Window / Greedy', 'difficulty': 'Easy', 'leetcode_ref': 'LeetCode 121 - Best Time to Buy and Sell Stock',
     'question': '[LeetCode 121 - Best Time to Buy Stock] To find maximum single-transaction profit in an array of stock prices, what is the best time and auxiliary space complexity?',
     'options': ['O(n^2) time, O(1) space', 'O(n) time, O(1) space', 'O(n log n) time, O(n) space', 'O(n) time, O(n) space'], 'answer': 1},

    {'id': 5, 'topic': 'Binary Search', 'difficulty': 'Easy', 'leetcode_ref': 'LeetCode 704 - Binary Search',
     'question': '[LeetCode 704 - Binary Search] In a sorted ascending array of size n, how many comparisons does binary search take in the worst case?',
     'options': ['O(n)', 'O(log2 n)', 'O(n log n)', 'O(1)'], 'answer': 1},

    {'id': 6, 'topic': 'Arrays & Dynamic Programming', 'difficulty': 'Easy', 'leetcode_ref': 'LeetCode 53 - Maximum Subarray',
     'question': "[LeetCode 53 - Maximum Subarray] Which O(n) algorithm solves the maximum contiguous subarray sum problem by tracking current and global maximums?",
     'options': ["Kadane's Algorithm", "Dijkstra's Algorithm", "Kruskal's Algorithm", "Floyd's Algorithm"], 'answer': 0},

    {'id': 7, 'topic': 'Trees', 'difficulty': 'Easy', 'leetcode_ref': 'LeetCode 226 - Invert Binary Tree',
     'question': '[LeetCode 226 - Invert Binary Tree] Inverting a binary tree (swapping left and right children for every node) requires visiting every node once. What is its time complexity?',
     'options': ['O(h) where h is height', 'O(n) where n is node count', 'O(n log n)', 'O(1)'], 'answer': 1},

    {'id': 8, 'topic': 'Linked List', 'difficulty': 'Easy', 'leetcode_ref': 'LeetCode 141 - Linked List Cycle',
     'question': "[LeetCode 141 - Linked List Cycle] Which two-pointer technique detects whether a cycle exists in a singly linked list in O(n) time and O(1) memory?",
     'options': ['Divide and Conquer', "Floyd's Tortoise and Hare (Slow & Fast Pointers)", 'Backtracking', 'Binary Search'], 'answer': 1},

    {'id': 9, 'topic': 'Strings', 'difficulty': 'Easy', 'leetcode_ref': 'LeetCode 242 - Valid Anagram',
     'question': '[LeetCode 242 - Valid Anagram] What is the most efficient auxiliary space complexity to verify if two strings of lowercase English letters are anagrams?',
     'options': ['O(1) space using a fixed 26-element frequency array', 'O(n^2) space', 'O(n!) space', 'O(2^n) space'], 'answer': 0},

    {'id': 10, 'topic': 'Dynamic Programming', 'difficulty': 'Easy', 'leetcode_ref': 'LeetCode 70 - Climbing Stairs',
     'question': '[LeetCode 70 - Climbing Stairs] If you can take 1 or 2 steps to reach step n, the recurrence relation ways(n) = ways(n-1) + ways(n-2) corresponds to which sequence?',
     'options': ['Factorial sequence', 'Catalan numbers', 'Fibonacci sequence', 'Geometric progression'], 'answer': 2},

    {'id': 11, 'topic': 'Linked List', 'difficulty': 'Easy', 'leetcode_ref': 'LeetCode 206 - Reverse Linked List',
     'question': '[LeetCode 206 - Reverse Linked List] An iterative in-place reversal of a singly linked list maintains how many pointers (e.g. prev, curr, next)?',
     'options': ['1 pointer', '3 pointers', '5 pointers', 'O(n) pointers'], 'answer': 1},

    {'id': 12, 'topic': 'Trees', 'difficulty': 'Easy', 'leetcode_ref': 'LeetCode 104 - Maximum Depth of Binary Tree',
     'question': '[LeetCode 104 - Maximum Depth of Binary Tree] What is the worst-case space complexity of recursive DFS on a completely skewed/degenerate binary tree of n nodes?',
     'options': ['O(1)', 'O(log n)', 'O(n) due to call stack frames', 'O(n^2)'], 'answer': 2},

    # ------------------ MEDIUM LEETCODE PROBLEMS (12) ------------------
    {'id': 13, 'topic': 'Sliding Window', 'difficulty': 'Medium', 'leetcode_ref': 'LeetCode 3 - Longest Substring Without Repeating Characters',
     'question': '[LeetCode 3 - Longest Substring Without Repeating Characters] What is the optimal time complexity to find the longest non-repeating substring using a sliding window with a Hash Set?',
     'options': ['O(n^2)', 'O(n)', 'O(n log n)', 'O(2^n)'], 'answer': 1},

    {'id': 14, 'topic': 'Two Pointers', 'difficulty': 'Medium', 'leetcode_ref': 'LeetCode 15 - 3Sum',
     'question': '[LeetCode 15 - 3Sum] After sorting the array in O(n log n), what is the optimal overall time complexity of finding all unique triplets that sum to 0 using Two Pointers?',
     'options': ['O(n^3)', 'O(n^2)', 'O(n log n)', 'O(n)'], 'answer': 1},

    {'id': 15, 'topic': 'Two Pointers', 'difficulty': 'Medium', 'leetcode_ref': 'LeetCode 11 - Container With Most Water',
     'question': '[LeetCode 11 - Container With Most Water] In the two-pointer solution starting at both ends of heights array, which pointer should be moved inwards at each step?',
     'options': ['Always move the left pointer', 'Always move the right pointer', 'Move the pointer with the smaller height', 'Move both pointers simultaneously'], 'answer': 2},

    {'id': 16, 'topic': 'Arrays & Prefix Sum', 'difficulty': 'Medium', 'leetcode_ref': 'LeetCode 238 - Product of Array Except Self',
     'question': '[LeetCode 238 - Product of Array Except Self] How can this problem be solved in O(n) time WITHOUT using the division operator?',
     'options': ['By computing prefix and suffix products', 'By sorting the array first', 'By using brute force nested loops', 'By building a binary tree'], 'answer': 0},

    {'id': 17, 'topic': 'Graphs / BFS / DFS', 'difficulty': 'Medium', 'leetcode_ref': 'LeetCode 200 - Number of Islands',
     'question': '[LeetCode 200 - Number of Islands] Given an m x n binary grid of land (1) and water (0), what is the time complexity of counting islands using BFS or DFS?',
     'options': ['O(m * n)', 'O(m + n)', 'O(m^2 * n^2)', 'O(2^(m+n))'], 'answer': 0},

    {'id': 18, 'topic': 'Dynamic Programming', 'difficulty': 'Medium', 'leetcode_ref': 'LeetCode 322 - Coin Change',
     'question': '[LeetCode 322 - Coin Change] To find the fewest number of coins needed to make up amount A with n coin denominations, what is the bottom-up DP time complexity?',
     'options': ['O(n * A)', 'O(2^A)', 'O(n^A)', 'O(A^2)'], 'answer': 0},

    {'id': 19, 'topic': 'Graphs / Topological Sort', 'difficulty': 'Medium', 'leetcode_ref': 'LeetCode 207 - Course Schedule',
     'question': '[LeetCode 207 - Course Schedule] Checking if you can finish all prerequisite courses is mathematically equivalent to detecting:',
     'options': ['A cycle in a Directed Graph (DAG verification)', 'The shortest path in an undirected graph', 'Eulerian path existence', 'Maximum bipartite matching'], 'answer': 0},

    {'id': 20, 'topic': 'Binary Search Trees', 'difficulty': 'Medium', 'leetcode_ref': 'LeetCode 98 - Validate Binary Search Tree',
     'question': '[LeetCode 98 - Validate Binary Search Tree] Which tree traversal of a valid BST must produce strictly increasing numerical values?',
     'options': ['Pre-order traversal', 'Post-order traversal', 'In-order traversal', 'Level-order traversal'], 'answer': 2},

    {'id': 21, 'topic': 'Heaps / Priority Queue', 'difficulty': 'Medium', 'leetcode_ref': 'LeetCode 347 - Top K Frequent Elements',
     'question': '[LeetCode 347 - Top K Frequent Elements] Using a min-heap of size k on an array of size n with unique elements, what is the time complexity?',
     'options': ['O(n log k)', 'O(n^2)', 'O(k^2)', 'O(n!)'], 'answer': 0},

    {'id': 22, 'topic': 'Matrix BFS', 'difficulty': 'Medium', 'leetcode_ref': 'LeetCode 994 - Rotting Oranges',
     'question': '[LeetCode 994 - Rotting Oranges] What algorithmic approach is optimal to find the minimum minutes until no fresh orange remains?',
     'options': ['Depth First Search (DFS)', 'Multi-Source Breadth First Search (BFS)', 'Binary Search', 'Greedy interval scheduling'], 'answer': 1},

    {'id': 23, 'topic': 'Binary Search', 'difficulty': 'Medium', 'leetcode_ref': 'LeetCode 33 - Search in Rotated Sorted Array',
     'question': '[LeetCode 33 - Search in Rotated Sorted Array] Even when an ascending array is rotated at some unknown pivot, in what time complexity can a target be found?',
     'options': ['O(1)', 'O(log n)', 'O(n)', 'O(n log n)'], 'answer': 1},

    {'id': 24, 'topic': 'Hash Maps & Sorting', 'difficulty': 'Medium', 'leetcode_ref': 'LeetCode 49 - Group Anagrams',
     'question': '[LeetCode 49 - Group Anagrams] For N strings of maximum length K, what is the time complexity of grouping anagrams using sorted strings as hash map keys?',
     'options': ['O(N * K log K)', 'O(N^2 * K)', 'O(N! * K)', 'O(K^N)'], 'answer': 0},

    # ------------------ HARD LEETCODE PROBLEMS (10) ------------------
    {'id': 25, 'topic': 'Two Pointers / Stack', 'difficulty': 'Hard', 'leetcode_ref': 'LeetCode 42 - Trapping Rain Water',
     'question': '[LeetCode 42 - Trapping Rain Water] What is the optimal time and auxiliary space complexity to compute trapped rain water using Two Pointers?',
     'options': ['O(n) time, O(1) space', 'O(n^2) time, O(n) space', 'O(n log n) time, O(n) space', 'O(n) time, O(n) space'], 'answer': 0},

    {'id': 26, 'topic': 'Heaps / Divide & Conquer', 'difficulty': 'Hard', 'leetcode_ref': 'LeetCode 23 - Merge k Sorted Lists',
     'question': '[LeetCode 23 - Merge k Sorted Lists] Merging k sorted linked lists with a total of N nodes using a Min-Heap of size k takes what time complexity?',
     'options': ['O(N * k)', 'O(N log k)', 'O(k * log N)', 'O(N^2)'], 'answer': 1},

    {'id': 27, 'topic': 'Binary Search on Partitions', 'difficulty': 'Hard', 'leetcode_ref': 'LeetCode 4 - Median of Two Sorted Arrays',
     'question': '[LeetCode 4 - Median of Two Sorted Arrays] Given two sorted arrays of sizes m and n, what is the optimal time complexity required to locate the median?',
     'options': ['O(log(min(m, n)))', 'O(m + n)', 'O(m * n)', 'O(log(m * n))'], 'answer': 0},

    {'id': 28, 'topic': 'Dynamic Programming', 'difficulty': 'Hard', 'leetcode_ref': 'LeetCode 72 - Edit Distance',
     'question': '[LeetCode 72 - Edit Distance] What is the dynamic programming time and space complexity to find the Levenshtein distance between two strings of lengths m and n?',
     'options': ['O(m * n) time and O(m * n) space', 'O(2^(m+n)) time and O(1) space', 'O(m + n) time and O(1) space', 'O(m! * n!) time'], 'answer': 0},

    {'id': 29, 'topic': 'Monotonic Deque', 'difficulty': 'Hard', 'leetcode_ref': 'LeetCode 239 - Sliding Window Maximum',
     'question': '[LeetCode 239 - Sliding Window Maximum] What data structure allows finding the maximum in every sliding window of size k in amortized O(n) total time?',
     'options': ['Max-Heap with delete', 'Monotonically Decreasing Deque (Double-Ended Queue)', 'Binary Search Tree', 'Circular Single Queue'], 'answer': 1},

    {'id': 30, 'topic': 'Shortest Path / BFS', 'difficulty': 'Hard', 'leetcode_ref': 'LeetCode 127 - Word Ladder',
     'question': '[LeetCode 127 - Word Ladder] Finding the shortest transformation sequence from beginWord to endWord where each step differs by 1 letter is best solved using:',
     'options': ['Breadth-First Search (BFS) / Bidirectional BFS', 'Depth-First Search (DFS)', "Prim's Algorithm", "Kruskal's Algorithm"], 'answer': 0},

    {'id': 31, 'topic': 'Arrays / In-Place Hashing', 'difficulty': 'Hard', 'leetcode_ref': 'LeetCode 41 - First Missing Positive',
     'question': '[LeetCode 41 - First Missing Positive] To find the smallest missing positive integer in O(n) time and strictly O(1) extra auxiliary space, what technique is used?',
     'options': ['Merge Sort', 'Index as Hash Key (in-place array element swapping to nums[nums[i]-1])', 'Hash Set with dynamic resize', 'Building a Fibonacci heap'], 'answer': 1},

    {'id': 32, 'topic': 'Dynamic Programming / Stack', 'difficulty': 'Hard', 'leetcode_ref': 'LeetCode 32 - Longest Valid Parentheses',
     'question': '[LeetCode 32 - Longest Valid Parentheses] What is the optimal time complexity to find the length of the longest valid parentheses substring?',
     'options': ['O(n^3)', 'O(n^2)', 'O(n) using 1D DP or Stack', 'O(2^n)'], 'answer': 2},

    {'id': 33, 'topic': 'Tree Serialization', 'difficulty': 'Hard', 'leetcode_ref': 'LeetCode 297 - Serialize & Deserialize Binary Tree',
     'question': '[LeetCode 297 - Serialize Binary Tree] To uniquely reconstruct a binary tree from a single serialized string without ambiguities, what must be explicitly preserved?',
     'options': ['Only the root node value', 'Null / None leaf node markers alongside node values in preorder/level-order', 'Only node values in descending order', 'The memory addresses of pointers'], 'answer': 1},

    {'id': 34, 'topic': 'Graphs / DAG', 'difficulty': 'Hard', 'leetcode_ref': 'LeetCode 269 - Alien Dictionary',
     'question': '[LeetCode 269 - Alien Dictionary] Deriving the lexicographical order of characters from a sorted alien word list is solved by building a graph and running:',
     'options': ['Topological Sort (Kahn\'s Algorithm / Post-order DFS)', 'Dijkstra\'s Shortest Path', 'Maximum Flow (Ford-Fulkerson)', 'Bellman-Ford Algorithm'], 'answer': 0},
]

VALID_QUESTION_COUNTS = (15, 20)
DEFAULT_QUESTION_COUNT = 15


def get_quiz_questions(count=DEFAULT_QUESTION_COUNT, seed=None):
    """
    Selects `count` questions from the LeetCode bank:
    - If count == 15: Selects exactly 5 Easy, 5 Medium, and 5 Hard LeetCode questions.
    - If count == 20: Selects 7 Easy, 8 Medium, and 5 Hard LeetCode questions.
    
    Returns:
        (public_questions, answer_key)
    """
    if count not in VALID_QUESTION_COUNTS:
        count = DEFAULT_QUESTION_COUNT

    rng = random.Random(seed) if seed is not None else random.Random()

    easy_pool = [q for q in QUESTION_BANK if q['difficulty'] == 'Easy']
    medium_pool = [q for q in QUESTION_BANK if q['difficulty'] == 'Medium']
    hard_pool = [q for q in QUESTION_BANK if q['difficulty'] == 'Hard']

    if count == 15:
        # User specified criteria: exactly 5 Easy, 5 Medium, 5 Hard
        selected_easy = rng.sample(easy_pool, 5)
        selected_medium = rng.sample(medium_pool, 5)
        selected_hard = rng.sample(hard_pool, 5)
        # Order them progressively: Easy -> Medium -> Hard
        selected = selected_easy + selected_medium + selected_hard
    elif count == 20:
        selected_easy = rng.sample(easy_pool, min(7, len(easy_pool)))
        selected_medium = rng.sample(medium_pool, min(8, len(medium_pool)))
        selected_hard = rng.sample(hard_pool, min(5, len(hard_pool)))
        selected = selected_easy + selected_medium + selected_hard
    else:
        selected = rng.sample(QUESTION_BANK, min(count, len(QUESTION_BANK)))

    public_questions = []
    answer_key = {}
    for q in selected:
        public_questions.append({
            'id': q['id'],
            'topic': q['topic'],
            'difficulty': q['difficulty'],
            'leetcode_ref': q.get('leetcode_ref', ''),
            'question': q['question'],
            'options': q['options']
        })
        answer_key[str(q['id'])] = q['answer']

    return public_questions, answer_key


def score_quiz(submitted_answers, answer_key):
    """
    submitted_answers: dict {question_id(str): selected_option_index(int)}
    answer_key: dict {question_id(str): correct_option_index(int)}

    Returns score, breakdown, difficulty breakdown, and weak topics.
    """
    total = len(answer_key)
    correct = 0
    topic_stats = {}
    difficulty_stats = {'Easy': {'correct': 0, 'total': 0},
                        'Medium': {'correct': 0, 'total': 0},
                        'Hard': {'correct': 0, 'total': 0}}
    id_to_question = {q['id']: q for q in QUESTION_BANK}

    for qid_str, correct_idx in answer_key.items():
        qid = int(qid_str)
        selected_idx = submitted_answers.get(qid_str)
        is_correct = (selected_idx is not None and int(selected_idx) == correct_idx)
        if is_correct:
            correct += 1

        q_info = id_to_question.get(qid, {})
        topic = q_info.get('topic', 'General')
        diff = q_info.get('difficulty', 'Medium')

        stat = topic_stats.setdefault(topic, {'correct': 0, 'total': 0})
        stat['total'] += 1
        if is_correct:
            stat['correct'] += 1

        if diff in difficulty_stats:
            difficulty_stats[diff]['total'] += 1
            if is_correct:
                difficulty_stats[diff]['correct'] += 1

    score_percentage = round((correct / total) * 100.0, 1) if total > 0 else 0.0

    weak_topics = sorted(
        [t for t, s in topic_stats.items() if s['total'] > 0 and (s['correct'] / s['total']) < 0.5],
        key=lambda t: topic_stats[t]['correct'] / topic_stats[t]['total']
    )

    return {
        'total_questions': total,
        'correct_answers': correct,
        'score_percentage': score_percentage,
        'topic_breakdown': topic_stats,
        'difficulty_breakdown': difficulty_stats,
        'weak_topics': weak_topics
    }
