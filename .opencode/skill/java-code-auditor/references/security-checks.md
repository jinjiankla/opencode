# Security Vulnerability Detection

This document outlines the security vulnerabilities that the Java code auditor detects and their remediation strategies.

## SQL Injection (Critical)

### Detection Patterns

```java
// Dangerous patterns
String query = "SELECT * FROM users WHERE id = " + userId;
statement.executeQuery("SELECT * FROM users WHERE name = '" + userName + "'");
Statement stmt = conn.createStatement("DELETE FROM users WHERE id = " + id);
```

### Safe Alternatives

```java
// Use PreparedStatement
String query = "SELECT * FROM users WHERE id = ?";
PreparedStatement stmt = conn.prepareStatement(query);
stmt.setInt(1, userId);
ResultSet rs = stmt.executeQuery();

// Use ORM frameworks
List<User> users = entityManager.createQuery(
    "SELECT u FROM User u WHERE u.id = :id", User.class)
    .setParameter("id", userId)
    .getResultList();
```

### Remediation Steps

1. Replace string concatenation in SQL with parameterized queries
2. Use PreparedStatement for all dynamic SQL
3. Consider using ORM frameworks (JPA, Hibernate)
4. Implement input validation and sanitization

## Path Traversal (Critical)

### Detection Patterns

```java
// Dangerous patterns
File file = new File(basePath + userInput);
String path = "/var/www/" + request.getParameter("file");
Files.copy(Paths.get(userPath), targetPath);
```

### Safe Alternatives

```java
// Validate and normalize paths
String input = request.getParameter("file");
Path inputPath = Paths.get(input);
Path basePath = Paths.get("/var/www");
Path resolved = basePath.resolve(inputPath).normalize();

if (!resolved.startsWith(basePath)) {
    throw new SecurityException("Path traversal attempt detected");
}
```

### Remediation Steps

1. Validate all file paths against an allowlist
2. Use canonical/normalized paths
3. Restrict access to specific directories
4. Never concatenate user input into file paths

## Hardcoded Credentials (Critical)

### Detection Patterns

```java
// Dangerous patterns
String password = "admin123";
String apiKey = "sk-1234567890abcdef";
String dbUrl = "jdbc:mysql://user:password@localhost/db";
String secretKey = "mySecretKey123";
```

### Safe Alternatives

```java
// Use environment variables
String password = System.getenv("DB_PASSWORD");
String apiKey = System.getenv("API_KEY");

// Use configuration files
Properties props = new Properties();
props.load(new FileInputStream("config.properties"));
String password = props.getProperty("db.password");

// Use secret management services
String secret = secretManager.getSecret("database-password");
```

### Remediation Steps

1. Remove all hardcoded credentials from code
2. Use environment variables for configuration
3. Implement proper secret management
4. Use secure key stores (Java KeyStore)
5. Rotate credentials regularly

## Command Injection (Critical)

### Detection Patterns

```java
// Dangerous patterns
Runtime.getRuntime().exec("ls " + userInput);
ProcessBuilder pb = new ProcessBuilder("cmd", userInput);
String command = "ping " + ipAddress;
```

### Safe Alternatives

```java
// Use parameterized commands
String[] cmd = {"ping", ipAddress};
ProcessBuilder pb = new ProcessBuilder(cmd);

// Validate input thoroughly
if (!isValidHostname(ipAddress)) {
    throw new SecurityException("Invalid hostname");
}
```

### Remediation Steps

1. Avoid shell command execution with user input
2. Use parameterized ProcessBuilder
3. Implement strict input validation
4. Use allowlists for commands and parameters

## Weak Cryptography (High)

### Detection Patterns

```java
// Weak algorithms
Cipher.getInstance("DES");           // 56-bit key
Cipher.getInstance("RC4");          // Stream cipher, broken
MessageDigest.getInstance("MD5");   // Collisions possible
MessageDigest.getInstance("SHA1");  // Collisions possible

// Hardcoded keys/IVs
byte[] key = "secretkey".getBytes();
byte[] iv = "initvector".getBytes();
```

### Safe Alternatives

```java
// Strong algorithms
Cipher.getInstance("AES/GCM/NoPadding");  // AEAD cipher
MessageDigest.getInstance("SHA-256");      // Strong hash
KeyGenerator.getInstance("AES").initKey(256); // Strong key size

// Proper key management
SecretKey key = KeyGenerator.getInstance("AES").generateKey();
byte[] iv = new byte[16];  // Generate random IV
SecureRandom random = new SecureRandom();
random.nextBytes(iv);
```

### Remediation Steps

1. Replace DES, 3DES, RC4 with AES-256
2. Use SHA-256 or better instead of MD5/SHA-1
3. Generate cryptographically secure random keys and IVs
4. Implement proper key lifecycle management
5. Use authenticated encryption (AEAD) modes

## XML External Entity (XXE) (High)

### Detection Patterns

```java
// Dangerous XML parsing
DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
DocumentBuilder db = dbf.newDocumentBuilder();
Document doc = db.parse(new File("user_input.xml"));

SAXParserFactory spf = SAXParserFactory.newInstance();
SAXParser sp = spf.newSAXParser();
sp.parse(new File("user_input.xml"), handler);
```

### Safe Alternatives

```java
// Disable external entities
DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
dbf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
dbf.setFeature("http://xml.org/sax/features/external-general-entities", false);
dbf.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
dbf.setXIncludeAware(false);
dbf.setExpandEntityReferences(false);

DocumentBuilder db = dbf.newDocumentBuilder();
Document doc = db.parse(new File("user_input.xml"));
```

### Remediation Steps

1. Disable DOCTYPE declarations in XML parsers
2. Disable external entity resolution
3. Use secure XML configuration
4. Consider using JSON when possible
5. Validate XML against strict schemas

## Insecure Deserialization (High)

### Detection Patterns

```java
// Dangerous deserialization
ObjectInputStream ois = new ObjectInputStream(inputStream);
Object obj = ois.readObject();

// JSON deserialization without validation
ObjectMapper mapper = new ObjectMapper();
User user = mapper.readValue(json, User.class);
```

### Safe Alternatives

```java
// Use safe serialization formats
// JSON with strict typing
ObjectMapper mapper = new ObjectMapper();
mapper.enableDefaultTyping(ObjectMapper.DefaultTyping.NON_FINAL); // Disable this!
mapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, true);

// Input validation
if (!isValidObjectType(input)) {
    throw new SecurityException("Invalid object type");
}
```

### Remediation Steps

1. Avoid Java serialization when possible
2. Use safe data formats (JSON, XML with validation)
3. Implement strict input validation
4. Use integrity checks and digital signatures
5. Consider using serialization frameworks with security features

## Insufficient Input Validation (Medium)

### Detection Patterns

```java
// Missing validation
String email = request.getParameter("email");
String phone = request.getParameter("phone");
String number = request.getParameter("amount");

// Weak validation
if (userInput != null && !userInput.isEmpty()) {
    // Too permissive
}
```

### Safe Alternatives

```java
// Strong validation with allowlists
private static final Pattern EMAIL_PATTERN =
    Pattern.compile("^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+$");

public boolean isValidEmail(String email) {
    return EMAIL_PATTERN.matcher(email).matches() && email.length() <= 254;
}

// Numeric validation
public boolean isValidAmount(String amount) {
    try {
        BigDecimal value = new BigDecimal(amount);
        return value.compareTo(BigDecimal.ZERO) > 0 &&
               value.compareTo(new BigDecimal("1000000")) <= 0;
    } catch (NumberFormatException e) {
        return false;
    }
}
```

### Remediation Steps

1. Implement allowlist validation
2. Use regular expressions for format validation
3. Validate ranges and business rules
4. Sanitize input before processing
5. Use validation frameworks (Hibernate Validator)

## Sensitive Data Exposure (Medium)

### Detection Patterns

```java
// Logging sensitive data
logger.info("User login: " + username + ", password: " + password);
System.out.println("Credit card: " + creditCardNumber);
System.err.println("SSN: " + socialSecurityNumber);

// Error messages revealing information
catch (SQLException e) {
    throw new RuntimeException("Database error: " + e.getMessage()); // May leak schema
}
```

### Safe Alternatives

```java
// Mask sensitive data in logs
logger.info("User login: " + username + ", password: ********");

// Generic error messages
catch (SQLException e) {
    logger.error("Database error occurred", e); // Log full error
    throw new RuntimeException("Internal server error"); // Generic message
}

// Data masking
public String maskCreditCard(String cardNumber) {
    return "****-****-****-" + cardNumber.substring(cardNumber.length() - 4);
}
```

### Remediation Steps

1. Never log sensitive data
2. Mask or redact sensitive information
3. Use generic error messages to users
4. Implement proper logging levels
5. Regular expressions for data masking

## Missing Security Headers (Low)

### Detection Patterns

```java
// Missing security headers in web applications
// Should check for:
// - Content-Security-Policy
// - X-Frame-Options
// - X-Content-Type-Options
// - Strict-Transport-Security
// - X-XSS-Protection
```

### Safe Implementation

```java
// In servlet filter
response.setHeader("X-Frame-Options", "DENY");
response.setHeader("X-Content-Type-Options", "nosniff");
response.setHeader("X-XSS-Protection", "1; mode=block");
response.setHeader("Strict-Transport-Security", "max-age=31536000; includeSubDomains");
response.setHeader("Content-Security-Policy", "default-src 'self'");
```

### Remediation Steps

1. Implement security headers in web applications
2. Use security frameworks (Spring Security)
3. Configure servers with proper headers
4. Regular security header testing

## Additional Security Measures

### Code Reviews

- Peer review of security-sensitive code
- Security-focused code review checklist
- Regular security training for developers

### Security Testing

- Static analysis security testing (SAST)
- Dynamic application security testing (DAST)
- Penetration testing
- Dependency vulnerability scanning

### Compliance Standards

- OWASP Top 10
- CWE (Common Weakness Enumeration)
- Security development lifecycle (SDL)
- Industry-specific compliance (PCI DSS, HIPAA)

### Tools and Libraries

- OWASP ESAPI (Enterprise Security API)
- Apache Shiro for authentication/authorization
- Spring Security framework
- Dependency check tools (OWASP Dependency-Check)

This security guide provides comprehensive coverage of common Java security vulnerabilities and their prevention strategies.
