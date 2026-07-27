//! The SCM core — business rules, invariants, state machines, lifecycle and identity for the
//! 14 SCOR-DS departments (ADR-0035, ENG-R10).
//!
//! # What this crate is, and what it deliberately is not
//!
//! It is the innermost ring (ENG-R1). It holds **law**: what a document may become, what may
//! never be true, which transition is legal from which state. It holds no transport, no
//! persistence, no framework — the adapters do that (`napi-rs` toward NestJS, `tonic` toward
//! the Python tools).
//!
//! It also holds **no mathematics beyond exact arithmetic** (ENG-R10.3). Forecast fitting,
//! statistical inference, optimization and simulation live in `services/calc` because that is
//! Python's exclusive lane (ENG-R8). The core *calls* those; it never reimplements them.
//!
//! # Purity: the core has no clock and no identity source
//!
//! Timestamps and identifiers are **supplied by the caller**. The TypeScript aggregates this
//! crate replaces called `uuidv4()` and `nowUTC()` inside the constructor, which made every
//! creation non-deterministic and untestable without freezing global state. Here, identity and
//! time are inputs — so a rule is a pure function of its arguments, and a test states the
//! expected result instead of mocking the world.
//!
//! # Module layout
//!
//! One module per department, named `dNN_<key>` — Rust-legal snake_case that preserves the
//! stable department number from the id-registry (`crates/scm-core/src/d01_procurement/`
//! mirrors `packages/domain/src/01-procurement/` and
//! `services/calc/01_procurement/`). The gate reads that path to attribute symbols to a
//! department (G10).
//!
//! # Catalogue convention (G10)
//!
//! **Calculations are free functions; lifecycle transitions are `impl` methods.** This mirrors
//! the convention already documented for TypeScript, where G10 reads top-level
//! `export function` and aggregates publish their lifecycle through a namespace object. A
//! formula therefore needs a `CPT-*` concept node; a state transition is governed by the
//! department's `rule.md` instead.

#![forbid(unsafe_code)]

pub mod d01_procurement;

pub use scm_money::{Money, MoneyError};
