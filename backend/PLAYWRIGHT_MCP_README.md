# Playwright MCP Server for Nimo

This directory contains the Playwright MCP (Model Context Protocol) server integration for the Nimo project, providing browser automation and testing capabilities through the MCP protocol.

## Installation

The Playwright MCP server is already installed as a dependency. If you need to reinstall it:

```bash
npm install @playwright/mcp
```

## Usage

### Basic Usage

Start the Playwright MCP server with default configuration:

```bash
npm run playwright-mcp
```

### Configuration Options

You can customize the server behavior using environment variables:

- `PLAYWRIGHT_BROWSER`: Browser to use (`chrome`, `firefox`, `webkit`, `msedge`) - default: `chrome`
- `PLAYWRIGHT_HEADLESS`: Run in headless mode (`true`/`false`) - default: `false`
- `PLAYWRIGHT_HOST`: Host to bind to - default: `localhost`
- `PLAYWRIGHT_PORT`: Port to listen on - default: `3001`
- `PLAYWRIGHT_TIMEOUT_ACTION`: Action timeout in milliseconds - default: `10000`
- `PLAYWRIGHT_TIMEOUT_NAVIGATION`: Navigation timeout in milliseconds - default: `30000`
- `PLAYWRIGHT_VIEWPORT`: Browser viewport size (e.g., `1280,720`) - default: `1280,720`
- `PLAYWRIGHT_DEVICE`: Device to emulate (e.g., `iPhone 15`)
- `PLAYWRIGHT_CAPS`: Additional capabilities (comma-separated, e.g., `vision,pdf`)

### Example Usage

```bash
# Run with Firefox in headless mode
PLAYWRIGHT_BROWSER=firefox PLAYWRIGHT_HEADLESS=true npm run playwright-mcp

# Run with mobile device emulation
PLAYWRIGHT_DEVICE="iPhone 15" npm run playwright-mcp

# Run with custom timeouts
PLAYWRIGHT_TIMEOUT_ACTION=5000 PLAYWRIGHT_TIMEOUT_NAVIGATION=20000 npm run playwright-mcp
```

### Available Scripts

- `npm run playwright-mcp`: Start with custom configuration wrapper
- `npm run playwright-mcp:direct`: Start with direct npx command
- `npm run playwright-mcp:headless`: Start in headless mode
- `npm run playwright-mcp:chrome`: Start with Chrome browser
- `npm run playwright-mcp:firefox`: Start with Firefox browser

## MCP Tools Available

The Playwright MCP server provides the following tools through the MCP protocol:

- **Browser Navigation**: Navigate to URLs, go back/forward, reload pages
- **Element Interaction**: Click elements, type text, select options
- **Page Inspection**: Get page content, take screenshots, extract text
- **Form Handling**: Fill forms, submit forms, handle file uploads
- **Waiting**: Wait for elements, network requests, page loads
- **Assertions**: Verify element presence, text content, page state
- **Screenshots**: Capture full page or element screenshots
- **PDF Generation**: Generate PDFs from pages
- **Network Monitoring**: Intercept and monitor network requests
- **Cookie Management**: Get, set, and delete cookies
- **Local Storage**: Access and modify local storage
- **Session Storage**: Access and modify session storage

## Integration with MCP Clients

To use this server with MCP-compatible clients (like Claude Desktop or other MCP clients):

1. Configure your MCP client to connect to `http://localhost:3001` (or your configured port)
2. The server will automatically provide the available tools and resources
3. Use the MCP client's interface to interact with web pages through Playwright

## Testing Integration

The Playwright MCP server is particularly useful for:

- End-to-end testing of the Nimo frontend application
- Automated browser interactions for development workflows
- Web scraping and data extraction tasks
- Accessibility testing and validation
- Performance monitoring and analysis

## Troubleshooting

### Connection Issues
- Ensure the server is running on the expected port
- Check that the host binding allows connections from your MCP client
- Verify firewall settings allow the configured port

### Browser Issues
- Make sure the selected browser is installed and accessible
- Try running in headless mode if GUI issues occur
- Check browser version compatibility

### Performance Issues
- Adjust timeout values for slower network conditions
- Use headless mode for better performance in CI/CD environments
- Consider viewport size for different testing scenarios

## Development

To extend or modify the Playwright MCP server:

1. Edit `playwright-mcp-server.js` for custom configuration logic
2. Modify environment variables for different deployment scenarios
3. Add custom scripts to `package.json` for specific use cases

The server uses the official `@playwright/mcp` package under the hood, so all Playwright features and capabilities are available.