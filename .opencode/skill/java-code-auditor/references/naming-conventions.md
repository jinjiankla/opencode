# Java Naming Conventions

This document provides detailed naming conventions for Java code elements.

## Class Names

### Convention

- **Format**: PascalCase (Upper Camel Case)
- **Pattern**: `[A-Z][a-zA-Z0-9]*`
- **Length**: 3-50 characters

### Examples

```java
// Good
public class CustomerService { }
public class OrderProcessor { }
public class DatabaseConnection { }

// Bad
public class customerservice { }  // lowercase
public class CUSTOMER_SERVICE { }  // snake_case
public class Cs { }  // too short/ambiguous
```

### Rules

1. Must be a noun or noun phrase
2. Use descriptive, meaningful names
3. Avoid abbreviations unless widely known
4. Do not use Hungarian notation

## Method Names

### Convention

- **Format**: camelCase
- **Pattern**: `[a-z][a-zA-Z0-9]*`
- **Length**: 2-30 characters

### Examples

```java
// Good
public void calculateTotal() { }
public String getCustomerName() { }
public boolean isValid() { }

// Bad
public void CalculateTotal() { }  // starts with capital
public void calculate_total() { }  // snake_case
public void ct() { }  // too short/ambiguous
```

### Accessor Methods

```java
// Getters
public String getName() { }
public boolean isActive() { }  // not getActive()

// Setters
public void setName(String name) { }
public void setActive(boolean active) { }

// Boolean methods often use is/has/can prefix
public boolean isEmpty() { }
public boolean hasChildren() { }
public boolean canProcess() { }
```

## Variable Names

### Convention

- **Format**: camelCase
- **Pattern**: `[a-z][a-zA-Z0-9]*`
- **Length**: 1-20 characters (context dependent)

### Examples

```java
// Good
String customerName;
int orderCount;
List<OrderItem> orderItems;

// Bad
String cn;  // unclear abbreviation
String CustomerName;  // capital C
String customer_name;  // snake_case
```

### Variable Naming Guidelines

1. Use meaningful, descriptive names
2. Single character variables only for:
   - Loop counters (i, j, k)
   - Coordinates (x, y, z)
   - Generic types (T, E, K, V)
3. Avoid abbreviations unless obvious
4. Use full words instead of shortened versions

## Constant Names

### Convention

- **Format**: UPPER_SNAKE_CASE
- **Pattern**: `[A-Z][A-Z0-9_]*`
- **Requirement**: Must be `static final`

### Examples

```java
// Good
public static final int MAX_RETRY_COUNT = 3;
public static final String DEFAULT_ENCODING = "UTF-8";
public static final double PI = 3.14159;

// Bad
public static final int maxRetryCount = 3;  // camelCase
public static final int MAXRETRYCOUNT = 3;  // no underscores
```

### When to Use Constants

1. Configuration values
2. Magic numbers
3. String literals used multiple times
4. Fixed mathematical constants

## Package Names

### Convention

- **Format**: Lowercase with dots
- **Pattern**: `[a-z]+(\.[a-z]+)*`
- **Requirement**: Reverse domain name for organizations

### Examples

```java
// Good
com.company.project
com.company.project.service
org.apache.commons.lang

// Bad
Com.company.project  // capital letters
com.company.project.Service  // capital in package name
comcompanyproject  // no dots
```

### Package Structure Guidelines

1. Use reverse domain name convention
2. All lowercase letters
3. Separate words with dots, not underscores
4. Logical grouping of related classes

## Interface Names

### Convention

- **Format**: PascalCase
- **Optional**: Sometimes prefixed with "I"

### Examples

```java
// Preferred (no I prefix)
public interface Repository { }
public interface Service { }
public interface Comparator<T> { }

// Alternative (with I prefix - less common)
public interface IRepository { }
public interface IService { }
```

## Enum Names

### Convention

- **Format**: PascalCase for enum name
- **Format**: UPPER_SNAKE_CASE for enum constants

### Examples

```java
// Good
public enum OrderStatus {
    PENDING,
    PROCESSING,
    SHIPPED,
    DELIVERED,
    CANCELLED
}

// Bad
public enum orderStatus { }  // camelCase
public enum OrderStatus { pending, processing }  // camelCase constants
```

## Generic Type Parameters

### Convention

- **Format**: Single uppercase letters
- **Common patterns**:
  - `T` - Type
  - `E` - Element
  - `K` - Key
  - `V` - Value
  - `N` - Number

### Examples

```java
public class Box<T> { }
public interface List<E> { }
public class Map<K, V> { }
```

## Annotation Names

### Convention

- **Format**: PascalCase
- **Common patterns**: Often end with specific suffixes

### Examples

```java
public @interface Override { }
public @interface Deprecated { }
public @interface Component { }
public @interface Service { }
public @interface Repository { }
```

## Test Method Names

### Convention

- **Format**: snake_case or camelCase with descriptive names
- **Pattern**: `test[MethodName][Scenario]`

### Examples

```java
// Good (snake_case)
public void test_calculateTotal_withValidOrder() { }
public void test_getCustomerName_returnsCorrectName() { }

// Good (camelCase)
public void calculateTotal_WithValidOrder_ReturnsCorrectTotal() { }
public void getCustomerName_WhenCalled_ReturnsCorrectName() { }

// Bad
public void test1() { }  // not descriptive
public void testTotal() { }  // unclear what's being tested
```

## Acronyms and Abbreviations

### Guidelines

1. Treat acronyms as words in camelCase
2. Use full words when possible
3. Only use widely-known abbreviations

### Examples

```java
// Good
public class HttpRequest { }  // not HTTPRequest
public String getXmlContent() { }  // not getXMLContent
public void parseHtml() { }  // not parseHTML

// Acceptable abbreviations
public int getId() { }  // ID is widely understood
public String getUrl() { }  // URL is standard
public void setupApi() { }  // API is common
```

## File Naming

### Java Source Files

- **Convention**: Same as class name with `.java` extension
- **Example**: `CustomerService.java` for `CustomerService` class

### Test Files

- **Convention**: `[ClassName]Test.java`
- **Example**: `CustomerServiceTest.java` for `CustomerService` tests

## Special Cases

### Boolean Variables

```java
// Good
boolean isValid;
boolean hasChildren;
boolean canProcess;
boolean shouldRetry;

// Bad
boolean valid;  // lacks verb
boolean flag;   // not descriptive
boolean check;  // unclear what is being checked
```

### Collection Variables

```java
// Good
List<Customer> customers;
Map<String, Order> orders;
Set<String> allowedUrls;

// Bad (add type information)
List<Customer> customerList;  // redundant
Map<String, Order> orderMap;   // redundant
```

### Temporal Variables

```java
// Good
Date startTime;
Date currentTime;
long timestamp;

// Bad
Date s;  // unclear
Date t;  // ambiguous
long time;  // could be many things
```

This naming convention guide ensures consistency and readability across Java codebases.
