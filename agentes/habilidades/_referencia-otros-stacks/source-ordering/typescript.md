# TypeScript application

In `.ts` files, place external imports before internal imports, alphabetize both import lines and named specifiers, and separate present sections with comments. Before sorting, check side effects and initialization dependencies; preserve their required order. Inspect service and utility files for loose functions and move utility functions and service operations into appropriate class methods, except for required callbacks or entry points.

Source: [G-STRUCT-01 and G-STRUCT-02](../../../../rules/global-rules.md#L15); [professor feedback](../../../../knowledge/sources/professor-feedback.md#L34).
