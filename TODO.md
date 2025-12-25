# MyTower TODO List

## From PR #107 Review Feedback

### Priority: Medium
- [ ] **Keyboard Accessibility**: Add `:focus-visible` styling to control buttons in `web/src/App.svelte`
  - Current issue: Buttons lack focus indicators for keyboard navigation
  - Solution: Add CSS for `:focus-visible` with outline/ring styling
  - Impact: Better accessibility for keyboard users

- [ ] **Rendering Order Clarification**: Fix shaft/floor rendering order or comment in `web/src/WebGameView.ts:261-262`
  - Current issue: Comment says "shafts appear behind" but code draws shafts AFTER floors (making them appear on top)
  - Options:
    1. Move `drawShafts()` before `drawFloors()` if shafts should be background
    2. Update comment if current order is intentional
  - Needs verification: Check visual output to determine intended layering

### Priority: Low
- [ ] **Error Handling Consistency**: Add `throw error;` to `addFloor` method in `web/src/WebGameView.ts:315`
  - Current: Other mutation methods re-throw errors, but `addFloor` doesn't
  - Impact: Consistent error propagation across all mutations

- [ ] **Log Message Clarity**: Replace "hCell" with "horizontal position" in log messages
  - Files: `web/src/WebGameView.ts:345`, `web/src/UI_IMPLEMENTATION_GUIDE.md`
  - Impact: Better code maintainability by avoiding domain-specific abbreviations

## Future Enhancements

### UI/UX
- [ ] Add visual feedback when buttons are clicked (loading states)
- [ ] Add confirmation dialogs for expensive operations
- [ ] Display error messages in UI instead of just console
- [ ] Add keyboard shortcuts for common actions

### Architecture
- [ ] Consider extracting mutation logic into a separate service class
- [ ] Add retry logic for failed GraphQL mutations
- [ ] Implement optimistic updates for better UX

### Testing
- [ ] Add unit tests for WebGameView mutation methods
- [ ] Add integration tests for GraphQL subscriptions
- [ ] Add E2E tests for UI buttons

### Documentation
- [ ] Create deployment troubleshooting guide
- [ ] Document S3 vs CloudFront deployment differences
- [ ] Add architecture diagram showing frontend/backend communication

---

**Note**: This TODO list tracks technical debt and enhancement ideas. For active sprint work, sync with your project management tool (Jira/Linear/etc).
