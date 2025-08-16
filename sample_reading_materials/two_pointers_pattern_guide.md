# The Two Pointers Pattern: A Complete Guide

## Overview

The two pointers technique is one of the most elegant and efficient patterns in algorithmic problem-solving. By using two references to traverse data structures, we can solve problems that would otherwise require nested loops, reducing time complexity from O(n²) to O(n).

## Learning Objectives

After mastering this guide, you will be able to:
- Recognize when to apply the two pointers pattern
- Implement opposite-direction and same-direction pointer techniques
- Solve common interview problems using this pattern
- Optimize brute force solutions using two pointers

## Prerequisites

- Understanding of arrays and basic iteration
- Familiarity with Big-O notation
- Knowledge of sorting algorithms

## Section 1: Pattern Recognition

### When to Use Two Pointers

#### ✅ Strong Indicators
- **Sorted arrays or strings** (or sortable data)
- **Finding pairs, triplets, or subarrays** that meet criteria
- **Problems involving "opposite" or "converging" elements**
- **Palindrome-related problems**
- **Removing duplicates or elements**

#### ❌ When NOT to Use
- Unsorted data where sorting would be too expensive
- Problems requiring random access to multiple positions
- When you need to maintain relative order of elements
- Complex nested data structures

### Problem Patterns

#### Pattern 1: Target Sum Problems
"Find two numbers that sum to target"
```
[2, 7, 11, 15], target = 9
     ↑      ↑
   left   right
```

#### Pattern 2: Palindrome Problems
"Check if string is palindrome"
```
"racecar"
 ↑     ↑
left right
```

#### Pattern 3: Container Problems
"Find container with most water"
```
Heights: [1, 8, 6, 2, 5, 4, 8, 3, 7]
         ↑                       ↑
       left                   right
```

## Section 2: Opposite Direction Pointers

### The Classic Approach

Start with pointers at opposite ends and move them toward each other based on conditions.

#### Template Pattern
```python
def two_pointers_opposite(arr):
    left = 0
    right = len(arr) - 1
    
    while left < right:
        # Process current pair
        current_condition = process(arr[left], arr[right])
        
        if condition_met:
            return result
        elif need_larger_sum:
            left += 1  # Move to larger element
        else:
            right -= 1  # Move to smaller element
    
    return default_result
```

### Example 1: Two Sum (Sorted Array)

**Problem**: Find two numbers in sorted array that sum to target.

```python
def two_sum_sorted(nums, target):
    """
    Time: O(n), Space: O(1)
    Input: nums = [2,7,11,15], target = 9
    Output: [0,1]
    """
    left, right = 0, len(nums) - 1
    
    while left < right:
        current_sum = nums[left] + nums[right]
        
        if current_sum == target:
            return [left, right]
        elif current_sum < target:
            left += 1  # Need larger sum
        else:
            right -= 1  # Need smaller sum
    
    return []  # No solution found
```

**Walkthrough**:
```
nums = [2, 7, 11, 15], target = 9

Step 1: left=0, right=3
        sum = 2 + 15 = 17 > 9
        Move right pointer left

Step 2: left=0, right=2  
        sum = 2 + 11 = 13 > 9
        Move right pointer left

Step 3: left=0, right=1
        sum = 2 + 7 = 9 == 9
        Found! Return [0, 1]
```

### Example 2: Valid Palindrome

**Problem**: Check if string is a palindrome, ignoring non-alphanumeric characters.

```python
def is_palindrome(s):
    """
    Time: O(n), Space: O(1)
    Input: "A man, a plan, a canal: Panama"
    Output: True
    """
    left, right = 0, len(s) - 1
    
    while left < right:
        # Skip non-alphanumeric characters
        while left < right and not s[left].isalnum():
            left += 1
        while left < right and not s[right].isalnum():
            right -= 1
        
        # Compare characters (case-insensitive)
        if s[left].lower() != s[right].lower():
            return False
        
        left += 1
        right -= 1
    
    return True
```

### Example 3: Container With Most Water

**Problem**: Find two lines that form container with maximum area.

```python
def max_area(height):
    """
    Time: O(n), Space: O(1)
    Input: [1,8,6,2,5,4,8,3,7]
    Output: 49
    """
    left, right = 0, len(height) - 1
    max_water = 0
    
    while left < right:
        # Calculate current area
        width = right - left
        current_area = width * min(height[left], height[right])
        max_water = max(max_water, current_area)
        
        # Move pointer with smaller height
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    
    return max_water
```

**Key Insight**: Always move the pointer with the smaller height because moving the larger one cannot increase the area.

## Section 3: Same Direction Pointers

### The Fast and Slow Approach

Both pointers start at the same position and move in the same direction at different speeds.

#### Template Pattern
```python
def two_pointers_same_direction(arr):
    slow = 0
    
    for fast in range(len(arr)):
        if condition_met(arr[fast]):
            arr[slow] = process(arr[fast])
            slow += 1
    
    return slow  # Often returns new length
```

### Example 1: Remove Duplicates

**Problem**: Remove duplicates from sorted array in-place.

```python
def remove_duplicates(nums):
    """
    Time: O(n), Space: O(1)
    Input: [1,1,2,2,2,3]
    Output: 3 (array becomes [1,2,3,_,_,_])
    """
    if not nums:
        return 0
    
    slow = 0  # Position for next unique element
    
    for fast in range(1, len(nums)):
        if nums[fast] != nums[slow]:
            slow += 1
            nums[slow] = nums[fast]
    
    return slow + 1  # Length of unique elements
```

**Visualization**:
```
nums = [1,1,2,2,2,3]

Initial: slow=0, fast=1
[1,1,2,2,2,3]
 ↑ ↑
slow fast

fast=1: nums[1]==nums[0], skip
fast=2: nums[2]!=nums[0], slow++, nums[1]=nums[2]
[1,2,2,2,2,3]
   ↑ ↑
  slow fast

fast=3: nums[3]==nums[1], skip
fast=4: nums[4]==nums[1], skip
fast=5: nums[5]!=nums[1], slow++, nums[2]=nums[5]
[1,2,3,2,2,3]
     ↑     ↑
    slow  fast

Result: length = 3, array = [1,2,3,_,_,_]
```

### Example 2: Move Zeroes

**Problem**: Move all zeroes to end while maintaining relative order.

```python
def move_zeroes(nums):
    """
    Time: O(n), Space: O(1)
    Input: [0,1,0,3,12]
    Output: [1,3,12,0,0]
    """
    slow = 0  # Position for next non-zero element
    
    # Move all non-zero elements to front
    for fast in range(len(nums)):
        if nums[fast] != 0:
            nums[slow] = nums[fast]
            slow += 1
    
    # Fill remaining positions with zeros
    while slow < len(nums):
        nums[slow] = 0
        slow += 1
```

### Example 3: Remove Element

**Problem**: Remove all instances of a value in-place.

```python
def remove_element(nums, val):
    """
    Time: O(n), Space: O(1)
    Input: nums = [3,2,2,3], val = 3
    Output: 2 (array becomes [2,2,_,_])
    """
    slow = 0
    
    for fast in range(len(nums)):
        if nums[fast] != val:
            nums[slow] = nums[fast]
            slow += 1
    
    return slow
```

## Section 4: Advanced Applications

### Three Sum Problem

**Problem**: Find all unique triplets that sum to zero.

```python
def three_sum(nums):
    """
    Time: O(n²), Space: O(1) excluding output
    Input: [-1,0,1,2,-1,-4]
    Output: [[-1,-1,2],[-1,0,1]]
    """
    nums.sort()  # Required for two pointers
    result = []
    
    for i in range(len(nums) - 2):
        # Skip duplicates for first number
        if i > 0 and nums[i] == nums[i-1]:
            continue
        
        # Two pointers for remaining sum
        left, right = i + 1, len(nums) - 1
        target = -nums[i]
        
        while left < right:
            current_sum = nums[left] + nums[right]
            
            if current_sum == target:
                result.append([nums[i], nums[left], nums[right]])
                
                # Skip duplicates
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                
                left += 1
                right -= 1
            elif current_sum < target:
                left += 1
            else:
                right -= 1
    
    return result
```

### Trapping Rain Water

**Problem**: Calculate trapped rainwater between elevation bars.

```python
def trap(height):
    """
    Time: O(n), Space: O(1)
    Input: [0,1,0,2,1,0,1,3,2,1,2,1]
    Output: 6
    """
    if not height:
        return 0
    
    left, right = 0, len(height) - 1
    left_max, right_max = 0, 0
    water = 0
    
    while left < right:
        if height[left] < height[right]:
            if height[left] >= left_max:
                left_max = height[left]
            else:
                water += left_max - height[left]
            left += 1
        else:
            if height[right] >= right_max:
                right_max = height[right]
            else:
                water += right_max - height[right]
            right -= 1
    
    return water
```

**Key Insight**: Water level at any position is determined by the minimum of maximum heights to its left and right.

## Section 5: Common Variations and Tricks

### Window-Based Two Pointers

Sometimes two pointers maintain a "window" of elements:

```python
def longest_substring_k_distinct(s, k):
    """
    Find longest substring with at most k distinct characters
    """
    left = 0
    char_count = {}
    max_length = 0
    
    for right in range(len(s)):
        # Expand window
        char_count[s[right]] = char_count.get(s[right], 0) + 1
        
        # Contract window if needed
        while len(char_count) > k:
            char_count[s[left]] -= 1
            if char_count[s[left]] == 0:
                del char_count[s[left]]
            left += 1
        
        max_length = max(max_length, right - left + 1)
    
    return max_length
```

### Partition Problems

Use two pointers to partition arrays:

```python
def partition_array(nums, pivot):
    """
    Partition array around pivot value
    """
    left, right = 0, len(nums) - 1
    
    while left <= right:
        if nums[left] < pivot:
            left += 1
        elif nums[right] > pivot:
            right -= 1
        else:
            nums[left], nums[right] = nums[right], nums[left]
            left += 1
            right -= 1
    
    return left  # Index where pivot elements start
```

## Section 6: Problem-Solving Strategy

### Step-by-Step Approach

1. **Identify the Pattern**
   - Is the array sorted or can it be sorted?
   - Are you looking for pairs/triplets?
   - Do you need to remove or rearrange elements?

2. **Choose Pointer Direction**
   - **Opposite**: Pairs with specific sum, palindromes, containers
   - **Same**: Remove duplicates, partitioning, sliding window

3. **Define Movement Logic**
   - What condition moves which pointer?
   - How do you avoid infinite loops?
   - When do you stop?

4. **Handle Edge Cases**
   - Empty arrays
   - Single element
   - All elements the same
   - No valid solution exists

### Interview Communication

#### Template Response
1. **Recognize Pattern**: "This looks like a two pointers problem because..."
2. **Explain Approach**: "I'll use opposite-direction pointers starting from..."
3. **Walk Through Logic**: "If the sum is too small, I'll move the left pointer..."
4. **Analyze Complexity**: "Time complexity is O(n) because each element is visited once..."

## Section 7: Practice Problems

### Beginner Level
1. **Valid Palindrome** (LeetCode 125)
2. **Two Sum II** (LeetCode 167)
3. **Remove Duplicates from Sorted Array** (LeetCode 26)
4. **Move Zeroes** (LeetCode 283)

### Intermediate Level
5. **Container With Most Water** (LeetCode 11)
6. **3Sum** (LeetCode 15)
7. **Sort Colors** (LeetCode 75)
8. **Remove Element** (LeetCode 27)

### Advanced Level
9. **Trapping Rain Water** (LeetCode 42)
10. **4Sum** (LeetCode 18)
11. **Longest Substring Without Repeating Characters** (LeetCode 3)
12. **Minimum Window Substring** (LeetCode 76)

### Problem-Solving Checklist

Before implementing:
- [ ] Can the data be sorted if needed?
- [ ] What are the pointer movement conditions?
- [ ] How do you handle duplicates?
- [ ] What's the termination condition?
- [ ] Are there any edge cases?

## Conclusion

The two pointers technique is a powerful tool that can dramatically improve the efficiency of many algorithms. By mastering both opposite-direction and same-direction patterns, you'll be able to solve a wide variety of problems with optimal time and space complexity.

### Key Takeaways

1. **Pattern Recognition** is crucial - learn to identify two-pointer problems quickly
2. **Pointer Direction** determines the approach - opposite for pairs, same for filtering
3. **Movement Logic** must be carefully designed to ensure progress toward solution
4. **Edge Cases** are important - always consider empty arrays and boundary conditions
5. **Practice** builds intuition - solve problems regularly to internalize patterns

### Next Steps

1. Practice the provided problems, starting with beginner level
2. Study how two pointers combines with other patterns (sliding window, binary search)
3. Learn to optimize brute force solutions by identifying two-pointer opportunities
4. Apply the pattern to new problems you encounter

Remember: The two pointers technique is not just about efficiency - it's about elegant problem-solving that demonstrates deep understanding of algorithmic thinking.
