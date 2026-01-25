# Complexity Thresholds

This document defines complexity thresholds and their rationale for Java code analysis.

## Cyclomatic Complexity

### Definition

Cyclomatic complexity measures the number of linearly independent paths through a program's source code. It was developed by Thomas McCabe and is calculated using control flow graph analysis.

### Calculation Method

Base formula: `CC = E - N + 2P`
Where:

- E = Number of edges in control flow graph
- N = Number of nodes in control flow graph
- P = Number of connected components

### Simplified Calculation for Java

Base complexity = 1 (for a simple method)
Add 1 for each occurrence of:

- `if` statement
- `else` statement
- `while` loop
- `for` loop
- `case` statement in `switch`
- `catch` block
- Conditional operator `?:`
- Logical AND `&&`
- Logical OR `||`

### Thresholds

| Score Range | Category     | Severity    | Recommended Action              |
| ----------- | ------------ | ----------- | ------------------------------- |
| 1-10        | Simple       | ✅ Good     | No action needed                |
| 11-15       | Moderate     | ⚠️ Medium   | Consider refactoring if complex |
| 16-20       | Complex      | 🔴 High     | Refactoring recommended         |
| 21+         | Very Complex | 🚨 Critical | Immediate refactoring required  |

### Example Calculations

```java
// Complexity: 1 (base)
public void simpleMethod() {
    System.out.println("Hello");
}

// Complexity: 3 (1 base + 1 if + 1 else)
public void conditionalExample(boolean flag) {
    if (flag) {           // +1
        doSomething();
    } else {              // +1
        doSomethingElse();
    }
}

// Complexity: 6 (1 base + 2 if + 2 && + 1 ||)
public boolean complexExample(boolean a, boolean b, boolean c, boolean d) {
    if (a && b) {         // +1 if, +1 &&
        return true;
    } else if (c || d) {  // +1 if, +1 ||
        return false;     // +1 else
    }
    return false;
}
```

## Cognitive Complexity

### Definition

Cognitive complexity measures how difficult code is to understand by humans. Developed by SonarSource, it focuses on code readability and maintainability rather than just control flow.

### Key Principles

1. **Increment when nesting increases**
2. **Increment on control flow breaks**
3. **No penalty for boolean operations**
4. **Lower penalty than cyclomatic complexity**

### Calculation Rules

#### Nesting Increments

- First level: +1 point
- Each additional nesting level: +1 additional point

#### Control Flow Breaks

- `if`, `else`, `while`, `for`, `catch`: +1 point
- `switch`: +1 point
- `case`: +1 point (no nesting penalty)
- `break`, `continue`, `goto`: +1 point
- Recursion: +1 point

#### Examples

```java
// Cognitive Complexity: 1
public void simpleExample() {
    if (condition) {              // +1
        doSomething();
    }
}

// Cognitive Complexity: 4
public void nestedExample() {
    if (condition1) {              // +1
        if (condition2) {          // +1 (nesting level 2)
            while (condition3) {   // +1 (nesting level 3)
                doSomething();
            }
        }
    }
}
```

### Thresholds

| Score Range | Category     | Severity    | Recommended Action             |
| ----------- | ------------ | ----------- | ------------------------------ |
| 1-10        | Simple       | ✅ Good     | No action needed               |
| 11-15       | Moderate     | ⚠️ Medium   | Consider simplification        |
| 16-20       | Complex      | 🔴 High     | Refactoring recommended        |
| 21+         | Very Complex | 🚨 Critical | Immediate refactoring required |

## Nesting Depth

### Definition

Nesting depth measures the maximum level of nested control structures in a method.

### Thresholds

| Depth | Category  | Severity    | Recommended Action     |
| ----- | --------- | ----------- | ---------------------- |
| 1-2   | Simple    | ✅ Good     | No action needed       |
| 3-4   | Moderate  | ⚠️ Medium   | Monitor for complexity |
| 5-6   | Deep      | 🔴 High     | Consider flattening    |
| 7+    | Very Deep | 🚨 Critical | Refactoring required   |

### Example

```java
// Nesting Depth: 4
public void deepNesting() {
    if (level1) {                    // Level 1
        if (level2) {                // Level 2
            if (level3) {            // Level 3
                if (level4) {        // Level 4
                    doSomething();
                }
            }
        }
    }
}
```

## Parameter Count

### Thresholds

| Parameters | Category  | Severity    | Recommended Action        |
| ---------- | --------- | ----------- | ------------------------- |
| 0-4        | Simple    | ✅ Good     | No action needed          |
| 5-7        | Many      | ⚠️ Medium   | Consider parameter object |
| 8-10       | Too Many  | 🔴 High     | Use parameter object      |
| 11+        | Excessive | 🚨 Critical | Refactoring required      |

### Refactoring Suggestions

```java
// Bad: Too many parameters
public void createUser(String firstName, String lastName, String email,
                       String phone, String address, String city,
                       String state, String zip, String country) {
    // implementation
}

// Good: Using parameter object
public void CreateUser(UserData userData) {
    // implementation
}

class UserData {
    private String firstName;
    private String lastName;
    private String email;
    // ... other fields
}
```

## Method Length

### Measurement Lines

- **Physical lines**: Count including blank lines and comments
- **Logical lines**: Count statements and declarations only

### Thresholds

| Lines | Category  | Severity    | Recommended Action     |
| ----- | --------- | ----------- | ---------------------- |
| 1-20  | Short     | ✅ Good     | No action needed       |
| 21-30 | Moderate  | ⚠️ Medium   | Monitor complexity     |
| 31-50 | Long      | 🔴 High     | Consider breaking down |
| 51+   | Very Long | 🚨 Critical | Refactoring required   |

## Class Size

### Thresholds

| Lines   | Category   | Severity    | Recommended Action       |
| ------- | ---------- | ----------- | ------------------------ |
| 1-200   | Small      | ✅ Good     | No action needed         |
| 201-300 | Moderate   | ⚠️ Medium   | Monitor responsibilities |
| 301-500 | Large      | 🔴 High     | Consider splitting       |
| 501+    | Very Large | 🚨 Critical | Refactoring required     |

## File Size

### Thresholds

| Lines     | Category   | Severity    | Recommended Action   |
| --------- | ---------- | ----------- | -------------------- |
| 1-500     | Small      | ✅ Good     | No action needed     |
| 501-1000  | Moderate   | ⚠️ Medium   | Monitor organization |
| 1001-2000 | Large      | 🔴 High     | Consider splitting   |
| 2001+     | Very Large | 🚨 Critical | Refactoring required |

## Combined Complexity Assessment

### Weighted Score Calculation

When multiple complexity metrics are high, use a weighted approach:

```
Total Score = (Cyclomatic / 20) + (Cognitive / 25) + (Nesting / 8) + (Parameters / 10)
```

### Action Levels

| Total Score | Category    | Action                       |
| ----------- | ----------- | ---------------------------- |
| 0-1.0       | ✅ Good     | No action                    |
| 1.1-2.0     | ⚠️ Monitor  | Consider in next refactoring |
| 2.1-3.0     | 🔴 Review   | Plan refactoring             |
| 3.0+        | 🚨 Critical | Immediate action             |

## Best Practices for Reducing Complexity

### Extract Method

Break down complex methods into smaller, focused methods.

### Use Guard Clauses

Replace nested conditions with early returns.

### Strategy Pattern

Replace complex conditional logic with strategy objects.

### Parameter Object

Replace long parameter lists with objects.

### Builder Pattern

For complex object construction with many parameters.

## Tools and Integration

### IDE Support

- IntelliJ IDEA: Built-in complexity analysis
- Eclipse: Metrics plugin available
- VS Code: Complexity analysis extensions

### Build Tools

- Maven: Checkstyle plugin
- Gradle: SonarQube integration
- Ant: PMD integration

### Continuous Integration

- Jenkins: SonarQube quality gates
- GitHub Actions: Code quality checks
- GitLab CI: Complexity analysis in pipeline

These thresholds provide a comprehensive framework for maintaining code quality and readability in Java projects.
