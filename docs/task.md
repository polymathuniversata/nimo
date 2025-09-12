# TypeScript & ESLint Error Tasks

## Overview
This document tracks TypeScript compilation errors and ESLint warnings that need to be resolved in the Nimo frontend codebase.

## Error Summary
- **Total Errors:** 13
- **TypeScript Errors:** 6
- **ESLint Errors:** 7
- **Files Affected:** 2 (`errorService.ts`, `resizeObserver.ts`)

## Detailed Error List

### errorService.ts - TypeScript Errors

#### 1. Type Assignment Error (Line 46)
```typescript
// Current: Type incompatibility with exactOptionalPropertyTypes
const errorContext: ErrorContext = {
  ...context,
  timestamp: new Date(),
  userAgent: navigator.userAgent,
  url: window.location.href,
  stackTrace: stackTrace || undefined  // ← Issue here
};
```
**Error:** `Type 'string | undefined' is not assignable to type 'string'`
**Severity:** High
**Fix Required:** Update ErrorContext interface to allow optional stackTrace

#### 2. Window.Vue Property Access (Lines 226-227)
```typescript
// Current: Vue not defined on Window
if (window.Vue?.config) {
  window.Vue.config.errorHandler = (error, instance, info) => {
```
**Error:** `Property 'Vue' does not exist on type 'Window & typeof globalThis'`
**Severity:** Medium
**Fix Required:** Add Vue type declaration or use alternative approach

#### 3. Implicit Any Types (Line 227)
```typescript
// Current: Parameters have implicit any types
window.Vue.config.errorHandler = (error, instance, info) => {
```
**Error:** `Parameter 'error', 'instance', 'info' implicitly have an 'any' type`
**Severity:** Medium
**Fix Required:** Add explicit type annotations

### errorService.ts - ESLint Errors

#### 4. Redundant Type Constituents (Line 38)
```typescript
// Current: Error | unknown union
handleError(error: Error | unknown, ...)
```
**Error:** `'unknown' overrides all other types in this union type`
**Severity:** Low
**Fix Required:** Remove redundant `unknown` type

#### 5. Unexpected Any Usage (Line 153)
```typescript
// Current: Explicit any casting
const axiosError = error as any;
```
**Error:** `Unexpected any. Specify a different type`
**Severity:** Medium
**Fix Required:** Use proper Axios error type

#### 6. Unused Parameter (Line 344)
```typescript
// Current: showToUser parameter not used
private handleSesException(errorLog: ErrorLog, showToUser: boolean): string
```
**Error:** `'showToUser' is defined but never used`
**Severity:** Low
**Fix Required:** Remove unused parameter or use it

#### 7. Unexpected Any Usage (Line 390)
```typescript
// Current: app parameter typed as any
install(app: any) {
```
**Error:** `Unexpected any. Specify a different type`
**Severity:** Medium
**Fix Required:** Use proper Vue App type

#### 8. Unexpected Any Usage (Line 399)
```typescript
// Current: instance parameter typed as any
app.config.errorHandler = (error: Error, instance: any, info: string) => {
```
**Error:** `Unexpected any. Specify a different type`
**Severity:** Medium
**Fix Required:** Use proper Vue instance type

### resizeObserver.ts - ESLint Errors

#### 9. Unexpected Any Usage (Line 146)
```typescript
// Current: Generic function parameters
debounce<T extends (...args: any[]) => any>(func: T, wait: number)
```
**Error:** `Unexpected any. Specify a different type`
**Severity:** Medium
**Fix Required:** Use proper generic constraints

#### 10. Unused Parameter (Line 148)
```typescript
// Current: wait parameter not used
function debounce<T extends (...args: any[]) => any>(func: T, wait: number): (...args: Parameters<T>) => void {
```
**Error:** `'wait' is defined but never used`
**Severity:** Low
**Fix Required:** Remove unused parameter or implement it

## Priority Classification

### High Priority (Fix Immediately)
1. Type assignment error in errorService.ts (Line 46) - Breaking compilation

### Medium Priority (Fix Soon)
2. Window.Vue property access (Lines 226-227)
3. Implicit any types (Line 227)
4. Axios error type (Line 153)
5. Vue App type (Line 390)
6. Vue instance type (Line 399)
7. Generic function constraints (Line 146)

### Low Priority (Fix When Convenient)
8. Redundant type constituents (Line 38)
9. Unused parameters (Lines 344, 148)

## Fix Implementation Plan

### Phase 1: Critical TypeScript Fixes
1. [ ] Fix ErrorContext interface for optional stackTrace
2. [ ] Add Vue type declarations for window.Vue
3. [ ] Add explicit parameter types for error handler

### Phase 2: Type Safety Improvements
4. [ ] Replace `any` types with proper TypeScript types
5. [ ] Fix Axios error type casting
6. [ ] Update generic function constraints

### Phase 3: Code Cleanup
7. [ ] Remove redundant type constituents
8. [ ] Handle or remove unused parameters

## Testing Strategy

### Unit Tests
- [ ] Test error handling with different error types
- [ ] Test ResizeObserver utilities with various scenarios
- [ ] Verify type safety improvements

### Integration Tests
- [ ] Test error service integration with Vue components
- [ ] Test ResizeObserver in real component scenarios
- [ ] Verify no runtime errors after fixes

## Success Criteria

- [ ] Zero TypeScript compilation errors
- [ ] Zero ESLint errors (or acceptable warnings only)
- [ ] All type safety issues resolved
- [ ] Code maintains functionality while being type-safe
- [ ] No performance regressions from type fixes

## Resources Required

- TypeScript Developer: 2-4 hours
- Code Review: 1 hour
- Testing: 1-2 hours

## Notes

- Some `any` types may be acceptable in error handling contexts
- Vue 3 global properties may require special type declarations
- Consider using Vue's official types for better integration