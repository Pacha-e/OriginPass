# TypeScript testing

- For a pure calculation, assert inputs and expected outputs in a focused unit test. For a repository or HTTP boundary, exercise the actual boundary in an integration test; avoid mocking every participating layer. Cover critical user paths end to end. [Evidence: T10, lines 47?72](../../../../knowledge/research/T10-best-practices-b.md#1-test-pyramid-unit--integration--end-to-end).
- For a defect, capture a failing test or repeatable reproduction of the reported symptom before changing implementation; record the subsequent passing result. [Evidence: global rules, G-TEST-02](../../../../rules/global-rules.md#g-test-02-reproduce-defects-before-fixing).
