# TypeScript tooling

- Inspect `package.json` scripts and the project's shared ESLint and formatter configuration before choosing checks. Run the relevant existing scripts and report their results; a Nest project may configure an ESLint script over `src`, `apps`, `libs`, and `test`. [Evidence: Nest notes, lines 66?75](../../../../knowledge/books/T07-book-nest.md).
- Search changed lines for `eslint-disable` and review each new suppression. Check whether rules such as `no-param-reassign` and `no-underscore-dangle` were disabled merely to silence lint. [Evidence: MEVN notes, lines 428?442](../../../../knowledge/books/T06-book-mevn.md).
- Inspect `package.json`, the applicable lockfile, and available audit output for changed dependencies; assess compatibility and known vulnerabilities. [Evidence: G-TOOL-02](../../../../rules/global-rules.md#g-tool-02-maintain-dependencies-deliberately).
