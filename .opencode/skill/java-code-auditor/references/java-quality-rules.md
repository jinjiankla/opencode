# Java Code Quality Rules

This document defines the quality standards and thresholds used in the Java code auditor.

## Code Quality Metrics

### Method Length

- **Threshold**: 50 lines maximum
- **Severity**: Medium (50-100 lines), High (100+ lines)
- **Rationale**: Long methods are harder to understand, test, and maintain

### Class Size

- **Threshold**: 300 lines maximum
- **Severity**: Medium (300-500 lines), High (500+ lines)
- **Rationale**: Large classes often violate Single Responsibility Principle

### Parameter Count

- **Threshold**: 5 parameters maximum
- **Severity**: Medium (6-8 parameters), High (9+ parameters)
- **Rationale**: Too many parameters indicate complex method signatures

### File Length

- **Threshold**: 1000 lines maximum
- **Severity**: Medium (1000-2000 lines), High (2000+ lines)
- **Rationale**: Very long files are difficult to navigate and maintain

## Code Duplication

### Duplicate Detection

- **Minimum block size**: 5 lines
- **Similarity threshold**: 80% for similar code
- **Exact duplicates**: 100% similarity
- **Severity**: High for exact duplicates, Medium for similar

## Naming Conventions

### Class Names

- **Pattern**: PascalCase (e.g., `CustomerService`)
- **Length**: 3-50 characters
- **Requirements**: Must be noun or noun phrase

### Method Names

- **Pattern**: camelCase (e.g., `calculateTotal`)
- **Length**: 2-30 characters
- **Requirements**: Must be verb or verb phrase

### Variable Names

- **Pattern**: camelCase (e.g., `customerName`)
- **Length**: 1-20 characters
- **Requirements**: Descriptive and meaningful

### Constant Names

- **Pattern**: UPPER_SNAKE_CASE (e.g., `MAX_RETRY_COUNT`)
- **Requirements**: All static final fields

### Package Names

- **Pattern**: lowercase with dots (e.g., `com.company.project`)
- **Requirements**: Reverse domain name convention

## Documentation Standards

### JavaDoc Requirements

- **Public classes**: Must have JavaDoc
- **Public methods**: Must have JavaDoc explaining:
  - Purpose
  - Parameters (@param)
  - Return value (@return)
  - Exceptions (@throws)
- **Complex methods**: Should have inline comments for business logic

### Comment Quality

- **Comments should explain "why" not "what"**
- **Keep comments up-to-date with code**
- **Avoid redundant comments that repeat the code**

## Complexity Thresholds

### Cyclomatic Complexity

- **Good**: 1-10
- **Warning**: 11-20 (Medium severity)
- **Critical**: 21+ (High severity)

### Cognitive Complexity

- **Good**: 1-10
- **Warning**: 11-20 (Medium severity)
- **Critical**: 21+ (High severity)

### Nesting Depth

- **Maximum**: 4 levels
- **Severity**: Medium for 5 levels, High for 6+ levels

## Performance Guidelines

### Memory Management

- **Avoid unnecessary object creation in loops**
- **Use appropriate collection types with initial capacity**
- **Close resources properly (try-with-resources)**
- **Avoid memory leaks in collections**

### String Operations

- **Use StringBuilder for string concatenation in loops**
- **Avoid creating temporary strings**
- **Use efficient string comparison methods**

### Collection Usage

- **Choose appropriate collection type**
- **Set initial capacity when size is known**
- **Use efficient iteration patterns**
- **Avoid boxing/unboxing in critical paths**

## Security Standards

### Input Validation

- **Validate all external input**
- **Use whitelist approach for validation**
- **Sanitize user input before processing**

### Cryptography

- **Use strong encryption algorithms**
- **Never hardcode encryption keys**
- **Use secure random number generation**
- **Implement proper key management**

### SQL Injection Prevention

- **Use parameterized queries**
- **Avoid string concatenation for SQL**
- **Use ORM frameworks when possible**

### Authentication and Authorization

- **Never store plain text passwords**
- **Use strong password policies**
- **Implement proper session management**
- **Follow principle of least privilege**

## Error Handling

### Exception Handling

- **Use specific exception types**
- **Handle exceptions appropriately**
- **Never catch generic Exception unless necessary**
- **Log errors with sufficient context**

### Resource Management

- **Use try-with-resources for AutoCloseable objects**
- **Implement proper cleanup in finally blocks**
- **Avoid resource leaks**

## Testing Guidelines

### Code Coverage

- **Minimum 80% line coverage for new code**
- **Critical paths should have 100% coverage**
- **Focus on business logic testing**

### Test Quality

- **Write meaningful test names**
- **Test both positive and negative cases**
- **Use appropriate assertions**
- **Maintain test independence**

## Code Style

### Indentation and Formatting

- **Use 4 spaces for indentation**
- **Maximum line length: 120 characters**
- **Consistent code formatting**
- **Proper use of whitespace**

### Import Statements

- **No wildcard imports**
- **Organize imports alphabetically**
- **Remove unused imports**
- **Group imports by type**

### Code Organization

- **Logical grouping of methods**
- **Consistent ordering of class members**
- **Proper package organization**
- \*\*Follow standard Java conventions
