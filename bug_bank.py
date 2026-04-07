"""
Bug Bank - Collection of buggy Python code problems.
Contains 30+ problems across 8 bug categories for BugLab.
"""

PROBLEMS = [
    # ============================================================
    # CATEGORY 1: Logic Errors (wrong operators)
    # ============================================================
    {
        "id": "logic_001",
        "difficulty": "easy",
        "category": "logic_error",
        "description": "Function should return the maximum of two numbers",
        "buggy_code": """def find_max(a, b):
    if a < b:
        return a
    return b""",
        "fixed_code": """def find_max(a, b):
    if a > b:
        return a
    return b""",
        "test_cases": [
            {"input": [5, 3], "expected": 5},
            {"input": [2, 8], "expected": 8},
            {"input": [7, 7], "expected": 7},
        ]
    },
    {
        "id": "logic_002",
        "difficulty": "easy",
        "category": "logic_error",
        "description": "Function should check if a number is even",
        "buggy_code": """def is_even(n):
    return n % 2 == 1""",
        "fixed_code": """def is_even(n):
    return n % 2 == 0""",
        "test_cases": [
            {"input": [4], "expected": True},
            {"input": [7], "expected": False},
            {"input": [0], "expected": True},
        ]
    },
    {
        "id": "logic_003",
        "difficulty": "medium",
        "category": "logic_error",
        "description": "Function should return True if score is passing (>= 60)",
        "buggy_code": """def is_passing(score):
    return score > 60""",
        "fixed_code": """def is_passing(score):
    return score >= 60""",
        "test_cases": [
            {"input": [70], "expected": True},
            {"input": [60], "expected": True},
            {"input": [59], "expected": False},
        ]
    },
    {
        "id": "logic_004",
        "difficulty": "easy",
        "category": "logic_error",
        "description": "Function should add two numbers",
        "buggy_code": """def add(a, b):
    return a - b""",
        "fixed_code": """def add(a, b):
    return a + b""",
        "test_cases": [
            {"input": [2, 3], "expected": 5},
            {"input": [10, -5], "expected": 5},
            {"input": [0, 0], "expected": 0},
        ]
    },
    
    # ============================================================
    # CATEGORY 2: Off-by-One Errors
    # ============================================================
    {
        "id": "off_by_one_001",
        "difficulty": "medium",
        "category": "off_by_one",
        "description": "Function should return first N natural numbers (1 to N inclusive)",
        "buggy_code": """def first_n_numbers(n):
    return list(range(1, n))""",
        "fixed_code": """def first_n_numbers(n):
    return list(range(1, n + 1))""",
        "test_cases": [
            {"input": [5], "expected": [1, 2, 3, 4, 5]},
            {"input": [1], "expected": [1]},
            {"input": [3], "expected": [1, 2, 3]},
        ]
    },
    {
        "id": "off_by_one_002",
        "difficulty": "medium",
        "category": "off_by_one",
        "description": "Function should return the last element of a list",
        "buggy_code": """def get_last(lst):
    return lst[len(lst)]""",
        "fixed_code": """def get_last(lst):
    return lst[len(lst) - 1]""",
        "test_cases": [
            {"input": [[1, 2, 3]], "expected": 3},
            {"input": [["a", "b"]], "expected": "b"},
            {"input": [[42]], "expected": 42},
        ]
    },
    {
        "id": "off_by_one_003",
        "difficulty": "easy",
        "category": "off_by_one",
        "description": "Function should count from 0 to n (inclusive)",
        "buggy_code": """def count_to_n(n):
    return list(range(n))""",
        "fixed_code": """def count_to_n(n):
    return list(range(n + 1))""",
        "test_cases": [
            {"input": [3], "expected": [0, 1, 2, 3]},
            {"input": [0], "expected": [0]},
            {"input": [5], "expected": [0, 1, 2, 3, 4, 5]},
        ]
    },
    {
        "id": "off_by_one_004",
        "difficulty": "medium",
        "category": "off_by_one",
        "description": "Function should sum all numbers from 1 to N inclusive",
        "buggy_code": """def sum_to_n(n):
    total = 0
    for i in range(1, n):
        total += i
    return total""",
        "fixed_code": """def sum_to_n(n):
    total = 0
    for i in range(1, n + 1):
        total += i
    return total""",
        "test_cases": [
            {"input": [5], "expected": 15},
            {"input": [1], "expected": 1},
            {"input": [10], "expected": 55},
        ]
    },
    
    # ============================================================
    # CATEGORY 3: Wrong Return Value
    # ============================================================
    {
        "id": "return_001",
        "difficulty": "easy",
        "category": "wrong_return",
        "description": "Function should return the square of a number",
        "buggy_code": """def square(n):
    result = n * n
    return n""",
        "fixed_code": """def square(n):
    result = n * n
    return result""",
        "test_cases": [
            {"input": [4], "expected": 16},
            {"input": [0], "expected": 0},
            {"input": [7], "expected": 49},
        ]
    },
    {
        "id": "return_002",
        "difficulty": "medium",
        "category": "wrong_return",
        "description": "Function should return the length of a string",
        "buggy_code": """def string_length(s):
    count = 0
    for char in s:
        count += 1
    return s""",
        "fixed_code": """def string_length(s):
    return len(s)""",
        "test_cases": [
            {"input": ["hello"], "expected": 5},
            {"input": [""], "expected": 0},
            {"input": ["test"], "expected": 4},
        ]
    },
    {
        "id": "return_003",
        "difficulty": "easy",
        "category": "wrong_return",
        "description": "Function should return True if list is empty",
        "buggy_code": """def is_empty(lst):
    if len(lst) == 0:
        return False
    return True""",
        "fixed_code": """def is_empty(lst):
    if len(lst) == 0:
        return True
    return False""",
        "test_cases": [
            {"input": [[]], "expected": True},
            {"input": [[1, 2]], "expected": False},
            {"input": [[0]], "expected": False},
        ]
    },
    {
        "id": "return_004",
        "difficulty": "medium",
        "category": "wrong_return",
        "description": "Function should return the minimum value in a list",
        "buggy_code": """def find_min(numbers):
    minimum = numbers[0]
    for num in numbers:
        if num < minimum:
            minimum = num
    return numbers[0]""",
        "fixed_code": """def find_min(numbers):
    minimum = numbers[0]
    for num in numbers:
        if num < minimum:
            minimum = num
    return minimum""",
        "test_cases": [
            {"input": [[5, 2, 8, 1]], "expected": 1},
            {"input": [[10, 20, 30]], "expected": 10},
            {"input": [[-5, -2, -10]], "expected": -10},
        ]
    },
    
    # ============================================================
    # CATEGORY 4: Missing Edge Cases
    # ============================================================
    {
        "id": "edge_001",
        "difficulty": "medium",
        "category": "missing_edge_case",
        "description": "Function should return the first element, or None if list is empty",
        "buggy_code": """def first_or_none(lst):
    return lst[0]""",
        "fixed_code": """def first_or_none(lst):
    if len(lst) == 0:
        return None
    return lst[0]""",
        "test_cases": [
            {"input": [[1, 2, 3]], "expected": 1},
            {"input": [[]], "expected": None},
            {"input": [["a"]], "expected": "a"},
        ]
    },
    {
        "id": "edge_002",
        "difficulty": "medium",
        "category": "missing_edge_case",
        "description": "Function should safely divide two numbers, return None if divisor is zero",
        "buggy_code": """def safe_divide(a, b):
    return a / b""",
        "fixed_code": """def safe_divide(a, b):
    if b == 0:
        return None
    return a / b""",
        "test_cases": [
            {"input": [10, 2], "expected": 5.0},
            {"input": [10, 0], "expected": None},
            {"input": [7, 2], "expected": 3.5},
        ]
    },
    {
        "id": "edge_003",
        "difficulty": "hard",
        "category": "missing_edge_case",
        "description": "Function should return the average of a list, or 0 if empty",
        "buggy_code": """def average(numbers):
    return sum(numbers) / len(numbers)""",
        "fixed_code": """def average(numbers):
    if len(numbers) == 0:
        return 0
    return sum(numbers) / len(numbers)""",
        "test_cases": [
            {"input": [[1, 2, 3]], "expected": 2.0},
            {"input": [[]], "expected": 0},
            {"input": [[10]], "expected": 10.0},
        ]
    },
    {
        "id": "edge_004",
        "difficulty": "medium",
        "category": "missing_edge_case",
        "description": "Function should find index of element, return -1 if not found",
        "buggy_code": """def find_index(lst, target):
    for i in range(len(lst)):
        if lst[i] == target:
            return i""",
        "fixed_code": """def find_index(lst, target):
    for i in range(len(lst)):
        if lst[i] == target:
            return i
    return -1""",
        "test_cases": [
            {"input": [[1, 2, 3], 2], "expected": 1},
            {"input": [[1, 2, 3], 5], "expected": -1},
            {"input": [[], 1], "expected": -1},
        ]
    },
    
    # ============================================================
    # CATEGORY 5: Type Errors
    # ============================================================
    {
        "id": "type_001",
        "difficulty": "easy",
        "category": "type_error",
        "description": "Function should concatenate a string and a number",
        "buggy_code": """def concat_str_num(s, n):
    return s + n""",
        "fixed_code": """def concat_str_num(s, n):
    return s + str(n)""",
        "test_cases": [
            {"input": ["Score: ", 95], "expected": "Score: 95"},
            {"input": ["Count: ", 0], "expected": "Count: 0"},
            {"input": ["Value: ", 42], "expected": "Value: 42"},
        ]
    },
    {
        "id": "type_002",
        "difficulty": "medium",
        "category": "type_error",
        "description": "Function should repeat a string N times",
        "buggy_code": """def repeat_string(s, n):
    return s * str(n)""",
        "fixed_code": """def repeat_string(s, n):
    return s * n""",
        "test_cases": [
            {"input": ["ab", 3], "expected": "ababab"},
            {"input": ["x", 1], "expected": "x"},
            {"input": ["hi", 0], "expected": ""},
        ]
    },
    {
        "id": "type_003",
        "difficulty": "easy",
        "category": "type_error",
        "description": "Function should convert string input to integer and add 10",
        "buggy_code": """def add_ten(s):
    return s + 10""",
        "fixed_code": """def add_ten(s):
    return int(s) + 10""",
        "test_cases": [
            {"input": ["5"], "expected": 15},
            {"input": ["0"], "expected": 10},
            {"input": ["25"], "expected": 35},
        ]
    },
    {
        "id": "type_004",
        "difficulty": "medium",
        "category": "type_error",
        "description": "Function should sum string numbers in a list",
        "buggy_code": """def sum_string_numbers(str_nums):
    total = 0
    for s in str_nums:
        total += s
    return total""",
        "fixed_code": """def sum_string_numbers(str_nums):
    total = 0
    for s in str_nums:
        total += int(s)
    return total""",
        "test_cases": [
            {"input": [["1", "2", "3"]], "expected": 6},
            {"input": [["10", "20"]], "expected": 30},
            {"input": [["5"]], "expected": 5},
        ]
    },
    
    # ============================================================
    # CATEGORY 6: Recursion Errors (missing base case)
    # ============================================================
    {
        "id": "recursion_001",
        "difficulty": "hard",
        "category": "recursion_error",
        "description": "Function should calculate factorial using recursion",
        "buggy_code": """def factorial(n):
    return n * factorial(n - 1)""",
        "fixed_code": """def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)""",
        "test_cases": [
            {"input": [5], "expected": 120},
            {"input": [0], "expected": 1},
            {"input": [3], "expected": 6},
        ]
    },
    {
        "id": "recursion_002",
        "difficulty": "hard",
        "category": "recursion_error",
        "description": "Function should sum all numbers from n down to 0",
        "buggy_code": """def sum_down(n):
    return n + sum_down(n - 1)""",
        "fixed_code": """def sum_down(n):
    if n <= 0:
        return 0
    return n + sum_down(n - 1)""",
        "test_cases": [
            {"input": [5], "expected": 15},
            {"input": [0], "expected": 0},
            {"input": [3], "expected": 6},
        ]
    },
    {
        "id": "recursion_003",
        "difficulty": "hard",
        "category": "recursion_error",
        "description": "Function should count down from N to 1",
        "buggy_code": """def countdown(n):
    result = [n]
    result.extend(countdown(n - 1))
    return result""",
        "fixed_code": """def countdown(n):
    if n <= 0:
        return []
    result = [n]
    result.extend(countdown(n - 1))
    return result""",
        "test_cases": [
            {"input": [3], "expected": [3, 2, 1]},
            {"input": [1], "expected": [1]},
            {"input": [5], "expected": [5, 4, 3, 2, 1]},
        ]
    },
    
    # ============================================================
    # CATEGORY 7: Loop Errors
    # ============================================================
    {
        "id": "loop_001",
        "difficulty": "medium",
        "category": "loop_error",
        "description": "Function should count occurrences of target in list",
        "buggy_code": """def count_occurrences(lst, target):
    count = 0
    for item in lst:
        if item == target:
            count += 1
    return count
    count = 0""",
        "fixed_code": """def count_occurrences(lst, target):
    count = 0
    for item in lst:
        if item == target:
            count += 1
    return count""",
        "test_cases": [
            {"input": [[1, 2, 3, 2, 2], 2], "expected": 3},
            {"input": [[1, 1, 1], 1], "expected": 3},
            {"input": [[1, 2, 3], 5], "expected": 0},
        ]
    },
    {
        "id": "loop_002",
        "difficulty": "easy",
        "category": "loop_error",
        "description": "Function should reverse a list",
        "buggy_code": """def reverse_list(lst):
    result = []
    for i in range(len(lst)):
        result.append(lst[i])
    return result""",
        "fixed_code": """def reverse_list(lst):
    result = []
    for i in range(len(lst) - 1, -1, -1):
        result.append(lst[i])
    return result""",
        "test_cases": [
            {"input": [[1, 2, 3]], "expected": [3, 2, 1]},
            {"input": [["a", "b"]], "expected": ["b", "a"]},
            {"input": [[5]], "expected": [5]},
        ]
    },
    {
        "id": "loop_003",
        "difficulty": "medium",
        "category": "loop_error",
        "description": "Function should collect all even numbers from a list",
        "buggy_code": """def get_evens(numbers):
    evens = []
    for num in numbers:
        if num % 2 == 0:
            evens.append(num)
            break
    return evens""",
        "fixed_code": """def get_evens(numbers):
    evens = []
    for num in numbers:
        if num % 2 == 0:
            evens.append(num)
    return evens""",
        "test_cases": [
            {"input": [[1, 2, 3, 4, 5]], "expected": [2, 4]},
            {"input": [[2, 4, 6]], "expected": [2, 4, 6]},
            {"input": [[1, 3, 5]], "expected": []},
        ]
    },
    {
        "id": "loop_004",
        "difficulty": "hard",
        "category": "loop_error",
        "description": "Function should build a multiplication table",
        "buggy_code": """def mult_table(n):
    table = []
    for i in range(1, n + 1):
        row = []
        for j in range(1, n + 1):
            row.append(i * i)
        table.append(row)
    return table""",
        "fixed_code": """def mult_table(n):
    table = []
    for i in range(1, n + 1):
        row = []
        for j in range(1, n + 1):
            row.append(i * j)
        table.append(row)
    return table""",
        "test_cases": [
            {"input": [2], "expected": [[1, 2], [2, 4]]},
            {"input": [1], "expected": [[1]]},
            {"input": [3], "expected": [[1, 2, 3], [2, 4, 6], [3, 6, 9]]},
        ]
    },
    
    # ============================================================
    # CATEGORY 8: Variable Shadowing
    # ============================================================
    {
        "id": "shadow_001",
        "difficulty": "medium",
        "category": "variable_shadowing",
        "description": "Function should sum a list and return the total",
        "buggy_code": """def sum_list(numbers):
    sum = 0
    for num in numbers:
        sum = num
    return sum""",
        "fixed_code": """def sum_list(numbers):
    sum = 0
    for num in numbers:
        sum += num
    return sum""",
        "test_cases": [
            {"input": [[1, 2, 3]], "expected": 6},
            {"input": [[10, 20]], "expected": 30},
            {"input": [[5]], "expected": 5},
        ]
    },
    {
        "id": "shadow_002",
        "difficulty": "hard",
        "category": "variable_shadowing",
        "description": "Function should collect unique values from a list",
        "buggy_code": """def get_unique(lst):
    unique = []
    for item in lst:
        unique = item
        if item not in unique:
            unique.append(item)
    return unique""",
        "fixed_code": """def get_unique(lst):
    unique = []
    for item in lst:
        if item not in unique:
            unique.append(item)
    return unique""",
        "test_cases": [
            {"input": [[1, 2, 2, 3]], "expected": [1, 2, 3]},
            {"input": [[5, 5, 5]], "expected": [5]},
            {"input": [[1, 2, 3]], "expected": [1, 2, 3]},
        ]
    },
    {
        "id": "shadow_003",
        "difficulty": "medium",
        "category": "variable_shadowing",
        "description": "Function should find the product of all numbers in a list",
        "buggy_code": """def product(numbers):
    result = 1
    for num in numbers:
        result = num
    return result""",
        "fixed_code": """def product(numbers):
    result = 1
    for num in numbers:
        result *= num
    return result""",
        "test_cases": [
            {"input": [[2, 3, 4]], "expected": 24},
            {"input": [[5, 2]], "expected": 10},
            {"input": [[7]], "expected": 7},
        ]
    },
]

# Verify we have 30+ problems
assert len(PROBLEMS) >= 30, f"Need at least 30 problems, have {len(PROBLEMS)}"

# Verify all required fields present
required_fields = {"id", "difficulty", "category", "description", "buggy_code", "fixed_code", "test_cases"}
for problem in PROBLEMS:
    assert required_fields.issubset(problem.keys()), f"Problem {problem.get('id')} missing required fields"
    assert len(problem["test_cases"]) >= 3, f"Problem {problem.get('id')} needs at least 3 test cases"
