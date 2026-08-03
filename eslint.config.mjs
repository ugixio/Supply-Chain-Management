// The TypeScript lint bar (WORKFLOW U12). Flat config, which is the only format ESLint 10
// accepts — the backlog said "eslint 9" because that was current when it was written.
//
// WHY THIS IS A MERGE-GATE CHECK AND NOT A PER-LAYER ONE. `make verify` is the loop a session
// runs after every layer; `make verify-full` is the boundary. Linting sits in the second for the
// same reason `lint-rs` does: it earns its cost at integration, not on every edit.
//
// WHY IT IS NOT TYPE-AWARE YET. `typescript-eslint` can run rules that need the type checker
// (`projectService`), which catches a strictly larger class of defect and costs a full program
// build per run. Today the estate has two TypeScript files, so the extra classes would find
// nothing and the cost would be pure. The recommended non-type-aware set is the honest bar for
// this surface; **turning it on belongs to M4**, when apps/api and apps/web arrive and there is
// real code for it to reason about. Recorded here rather than left as a silent omission.
//
// The warnings-as-errors bar lives in the Makefile as `--max-warnings 0`, not in this file: a
// severity written here can be argued down per rule, while a count at the invocation cannot.

import tseslint from "typescript-eslint";

export default tseslint.config(
  {
    // Nothing generated, vendored or built is ours to lint. `target/` is Cargo's, and it holds
    // vendored crate READMEs that a path sweep has already mistaken for repository documents once.
    ignores: ["node_modules/**", "target/**", "dist/**", "build/**", ".turbo/**"],
  },
  {
    files: ["**/*.ts", "**/*.mts", "**/*.tsx"],
    extends: [tseslint.configs.recommended],
    rules: {
      // The standards module exports frozen reference data (ISO 4217, UN/ECE Rec 20, GS1 keys).
      // `as const` assertions on that data are the point, not a smell.
      "@typescript-eslint/prefer-as-const": "error",

      // ENG-R4/R5 and SCM-R14: money is minor units with explicit quantization, never a float.
      // No lint rule can enforce that — it is a design constraint over types, not a syntax
      // pattern — so this comment is a pointer, not a substitute. The Rust core and the golden
      // vectors are what actually hold that line.
    },
  },
);
