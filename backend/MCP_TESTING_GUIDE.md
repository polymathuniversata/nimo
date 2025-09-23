# Nimo System MCP Testing Guide

This guide demonstrates how to use Model Context Protocol (MCP) servers to comprehensively test the Nimo decentralized identity and contribution platform.

## 🏗️ System Architecture

The Nimo system uses two MCP servers for comprehensive testing:

1. **Nimo MCP Server** (`mcp-server.js`) - Provides blockchain context and MeTTa integration testing
2. **Playwright MCP Server** (`@playwright/mcp`) - Provides browser automation and frontend testing

## 🚀 Quick Start

### 1. Start All Services

```bash
# Terminal 1: Start Nimo MCP Server
cd backend
npm start

# Terminal 2: Start Playwright MCP Server
cd backend
npm run playwright-mcp

# Terminal 3: Start Frontend Development Server
cd frontend
npm run dev
```

### 2. Run MCP Tests

```bash
# Run comprehensive MCP test demo
cd backend
npm run test:mcp:demo

# Run actual MCP integration tests (requires running servers)
npm run test:mcp
```

## 🧪 Testing Scenarios

### Blockchain Integration Tests

Test blockchain context and smart contract interactions:

```javascript
// Test identity contract context
await mcpClient.callTool({
  name: 'get_blockchain_context',
  arguments: {
    contract_type: 'identity',
    network: 'cardano-preprod'
  }
});

// Test token contract context
await mcpClient.callTool({
  name: 'get_blockchain_context',
  arguments: {
    contract_type: 'token',
    network: 'cardano-preprod'
  }
});
```

### MeTTa Integration Tests

Test autonomous agent logic and rule-based validation:

```javascript
// Test identity creation rules
await mcpClient.callTool({
  name: 'get_metta_context',
  arguments: {
    context_type: 'identity_creation'
  }
});

// Test contribution verification
await mcpClient.callTool({
  name: 'get_metta_context',
  arguments: {
    context_type: 'contribution_verification'
  }
});
```

### Frontend UI Tests

Test user interface and user experience:

```javascript
// Navigate to pages
await playwrightClient.callTool({
  name: 'navigate',
  arguments: { url: 'http://localhost:5173/login' }
});

// Interact with elements
await playwrightClient.callTool({
  name: 'click',
  arguments: { selector: 'button:has-text("Login")' }
});

// Fill forms
await playwrightClient.callTool({
  name: 'fill',
  arguments: {
    selector: '[placeholder="Enter your email"]',
    value: 'test@example.com'
  }
});

// Take screenshots
await playwrightClient.callTool({
  name: 'screenshot',
  arguments: {
    fullPage: true,
    path: 'test_screenshot.png'
  }
});
```

### End-to-End Flow Tests

Complete user journey testing combining all components:

1. **User Registration Flow**
   - Navigate to registration page
   - Fill registration form with valid data
   - Submit form and verify success
   - Check email verification process

2. **Authentication Flow**
   - Navigate to login page
   - Enter valid credentials
   - Submit and verify dashboard access
   - Test session persistence and logout

3. **Contribution Submission Flow**
   - Login to system
   - Navigate to contribution page
   - Fill contribution details
   - Upload supporting documentation
   - Submit for MeTTa validation

4. **Token Claiming Flow**
   - Check contribution verification status
   - Verify MeTTa validation results
   - Claim earned tokens
   - Confirm blockchain transaction

## 📋 Available MCP Tools

### Nimo MCP Server Tools

- `get_blockchain_context` - Get blockchain contract information
- `get_metta_context` - Get MeTTa integration context
- `validate_mcp_context` - Validate MCP context hashes
- `read_resource` - Read contract and integration resources

### Playwright MCP Server Tools

- `navigate` - Navigate to URLs
- `click` - Click elements
- `fill` - Fill form fields
- `get_text` - Extract text content
- `get_attribute` - Get element attributes
- `screenshot` - Capture screenshots
- `wait_for_selector` - Wait for elements
- `query_selector_all` - Find multiple elements
- `get_url` - Get current URL
- `get_title` - Get page title
- `reload` - Reload page
- `go_back` - Navigate back
- `go_forward` - Navigate forward

## 🔧 Configuration

### Environment Variables

```bash
# Playwright MCP Configuration
PLAYWRIGHT_BROWSER=chrome
PLAYWRIGHT_HEADLESS=false
PLAYWRIGHT_HOST=localhost
PLAYWRIGHT_PORT=3001
PLAYWRIGHT_TIMEOUT_ACTION=10000
PLAYWRIGHT_TIMEOUT_NAVIGATION=30000
PLAYWRIGHT_VIEWPORT=1280,720

# Nimo MCP Configuration
BLOCKCHAIN_NETWORK=cardano-preprod
```

### Custom Test Scripts

Create custom test scripts in the `backend/` directory:

```javascript
// custom-test.js
const { Client } = require('@modelcontextprotocol/sdk/client/index.js');

class CustomTester {
  async runTests() {
    // Initialize MCP clients
    // Run custom test scenarios
    // Generate reports
  }
}

const tester = new CustomTester();
tester.runTests();
```

## 📊 Test Reporting

### Screenshots and Evidence

Tests automatically capture screenshots and save them to the project root:

- `login_form_before.png` - Before login attempt
- `login_form_after.png` - After login attempt
- `home_page.png` - Home page screenshot
- `test_screenshot.png` - Custom test screenshots

### Console Output

Test results are logged to console with clear indicators:

- ✅ Success indicators
- ❌ Error indicators
- 📋 Test descriptions
- 🔗 URLs and selectors
- 📸 Screenshot confirmations

## 🚨 Troubleshooting

### Common Issues

1. **MCP Server Connection Failed**
   ```bash
   # Check if servers are running
   ps aux | grep mcp
   # Restart servers
   npm start
   npm run playwright-mcp
   ```

2. **Frontend Server Not Responding**
   ```bash
   # Check frontend server
   cd frontend && npm run dev
   # Verify port 5173 is accessible
   curl http://localhost:5173
   ```

3. **Browser Automation Issues**
   ```bash
   # Run in headless mode
   PLAYWRIGHT_HEADLESS=true npm run playwright-mcp
   # Use different browser
   PLAYWRIGHT_BROWSER=firefox npm run playwright-mcp
   ```

4. **Port Conflicts**
   ```bash
   # Check port usage
   netstat -tlnp | grep 5173
   # Kill conflicting processes
   kill -9 <PID>
   ```

### Debug Mode

Enable detailed logging:

```bash
# Run with debug output
DEBUG=* npm run test:mcp
```

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: MCP System Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd backend && npm install
          cd ../frontend && npm install
      - name: Start services
        run: |
          cd backend && npm start &
          npm run playwright-mcp &
          cd ../frontend && npm run dev &
      - name: Run MCP tests
        run: cd backend && npm run test:mcp
```

## 📈 Performance Testing

### Load Testing with MCP

```javascript
// Load test example
async function loadTest() {
  const clients = [];
  for (let i = 0; i < 10; i++) {
    const client = new PlaywrightClient();
    clients.push(client);
    await client.navigate('http://localhost:5173');
  }
  // Run concurrent operations
  // Measure response times
  // Generate performance reports
}
```

## 🎯 Best Practices

1. **Test Isolation** - Each test should be independent
2. **Resource Cleanup** - Always close browser contexts
3. **Error Handling** - Implement proper error handling
4. **Screenshot Evidence** - Capture screenshots for debugging
5. **Performance Monitoring** - Track test execution times
6. **Cross-browser Testing** - Test on multiple browsers
7. **Mobile Testing** - Test responsive design
8. **Accessibility Testing** - Include a11y checks

## 🔮 Future Enhancements

- **Visual Regression Testing** - Compare screenshots
- **Performance Monitoring** - Track page load times
- **API Testing Integration** - Test backend endpoints
- **Database Testing** - Validate data persistence
- **Security Testing** - Automated security scans
- **Multi-environment Testing** - Test staging/production
- **Parallel Test Execution** - Run tests concurrently
- **Test Result Analytics** - Generate detailed reports

## 📞 Support

For issues or questions:

1. Check the troubleshooting section
2. Review server logs for error messages
3. Verify all services are running
4. Check network connectivity
5. Review MCP protocol documentation

---

**🎉 Ready to test your Nimo system with MCP!**

The MCP testing framework provides comprehensive coverage of your decentralized identity platform, from blockchain integration to user experience validation.</content>
<parameter name="filePath">e:\Polymath Universata\Projects\Nimo\backend\MCP_TESTING_GUIDE.md