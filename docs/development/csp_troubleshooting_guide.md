# CSP Troubleshooting Guide - Nimo Platform

## Content Security Policy (CSP) Issues

### Understanding CSP Errors
If you encounter CSP errors like:
```
Refused to execute inline script because it violates the following Content Security Policy directive: "script-src 'self' 'wasm-unsafe-eval' 'inline-speculation-rules' chrome-extension://...". Either the 'unsafe-inline' keyword, a hash ('sha256-...'), or a nonce ('nonce-...') is required to enable inline execution.
```

This typically happens when:
- Browser extensions inject inline scripts
- Third-party libraries use inline scripts
- Development tools inject debugging scripts

### Current CSP Configuration
The Nimo Platform uses a strict CSP policy defined in both `index.html` and `vite.config.ts`:

```javascript
// CSP Headers include:
default-src 'self';
script-src 'self' 'unsafe-inline' 'unsafe-eval' 'wasm-unsafe-eval' 'sha256-kPx0AsF0oz2kKiZ875xSvv693TBHkQ/0SkMJZnnNpnQ=' chrome-extension://* blob:;
style-src 'self' 'unsafe-inline' data: chrome-extension://*;
img-src 'self' data: https: blob: chrome-extension://*;
connect-src 'self' http://localhost:3000 http://localhost:5000 http://localhost:8081 https: wss: blob: chrome-extension://* ws:;
```

### Solutions for CSP Issues

#### 1. For Browser Extension Conflicts
- The CSP already allows Chrome extensions: `chrome-extension://*`
- If specific extensions cause issues, add their IDs: `chrome-extension://extension-id/`

#### 2. For Inline Scripts in Development
- Use Vite's built-in handling for inline scripts
- Avoid manual inline `<script>` tags in HTML
- Use ES6 modules instead of inline scripts

#### 3. For Third-Party Libraries
- Check if libraries support CSP-compliant loading
- Use Subresource Integrity (SRI) when possible
- Consider alternatives that don't require inline scripts

#### 4. Debugging CSP Issues
```javascript
// Add to vite.config.ts for development debugging
export default defineConfig({
  // ... other config
  server: {
    headers: {
      'Content-Security-Policy-Report-Only': `default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; report-uri /csp-report`,
    }
  }
});
```

#### 5. Production CSP Considerations
- Remove `'unsafe-inline'` and `'unsafe-eval'` if possible
- Use specific hashes for all inline scripts
- Implement CSP violation reporting
- Consider using a CSP nonce for dynamic scripts

### Framework Alternatives for Better CSP Compliance

#### Vue.js + Quasar vs React Comparison

| Aspect | Vue + Quasar | React + Vite |
|--------|-------------|--------------|
| **CSP Compliance** | Excellent | Good |
| **Inline Script Usage** | Minimal | Moderate |
| **Build Tool** | Vite (same) | Vite |
| **Component Library** | Quasar (Material Design) | shadcn/ui (Radix) |
| **Learning Curve** | Gentle | Moderate |
| **Ecosystem** | Growing | Mature |
| **TypeScript Support** | Excellent | Excellent |

#### Why Vue + Quasar might solve CSP issues:
- Vue's template compilation reduces inline script needs
- Quasar has built-in CSP-friendly components
- Less reliance on third-party libraries with inline scripts
- Better tree-shaking and code splitting

#### Migration Considerations:
- Similar Vite setup and configuration
- TypeScript support maintained
- Component structure differences
- State management (Pinia vs Context API)
- Routing (Vue Router vs React Router)

### Quick Fixes for Common CSP Errors

1. **Extension-related errors**: Usually harmless, can be ignored in development
2. **Missing hashes**: Add specific script hashes to CSP headers
3. **Inline styles**: Ensure `'unsafe-inline'` is present for style-src
4. **WebAssembly**: Keep `'wasm-unsafe-eval'` for Web3 functionality

### Testing CSP Compliance

```bash
# Check for CSP violations in browser console
# Use CSP evaluator tools online
# Test with different browsers and extensions
```

**Last Updated:** August 28, 2025
**Version:** 1.0.0