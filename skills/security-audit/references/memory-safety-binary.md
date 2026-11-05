# Memory Safety and Binary Hunting

Use when the target processes untrusted bytes in a memory-unsafe or
privileged context: C, C++, Objective-C, Rust `unsafe`, FFI, kernel
modules, parsers and decoders, network daemons, firmware, binary loaders,
runtimes, and JITs. Protocol authorization and state machines belong to
the protocols companion; this file covers process integrity, memory
safety, ABI boundaries, and loader behavior.

## Core Discipline

- Re-derive every bound and lifetime from attacker-controlled inputs and
  all callers. Validate against the worst accepted case, not a typical
  test vector.
- A panic, sanitizer finding, or crash proves a defect only when
  realistic untrusted input reaches it. Do not infer memory corruption,
  code execution, or shared availability impact from a label alone.
- Validate locally with sanitizers, deterministic concurrency tests,
  existing fuzz targets, and debugger-assisted fault classification. Stop
  after proving the violated invariant and the observable effect; no
  post-corruption technique development.
- Assembly, JIT code, custom allocators, intra-object accesses, and
  foreign libraries can escape sanitizer coverage — identify which
  faulting instructions are instrumented.
- `confirmed` only after source evidence plus bounded local validation
  establishes the defect and its effect. Unknown ABI, allocator,
  architecture, or deployment facts are `needs_validation`.

## Bounds and Representation Classes

- **Out-of-bounds read or write**: a length, offset, index, or terminator
  reaching a buffer without a correct bound. Recalculate headroom after
  prefixes, alignment, padding, and terminators; check source and
  destination capacity; check whether a short input is read before its
  declared length is trusted.
- **Integer overflow, underflow, truncation, signedness**:
  attacker-controlled arithmetic before allocation, copy, loop, indexing,
  and pointer operations. High-hit patterns: `a - b` with `b > a`,
  `count * element_size`, additions near the type maximum, negatives
  converted to unsigned, 64-bit lengths narrowed to 32-bit fields, `-1`
  sentinels becoming large sizes.
- **Unit and pointer-depth confusion**: code mixing bytes, elements, code
  units, pages, words, or nested pointer element sizes. Compare the unit
  at parse, validation, allocation, API boundary, and copy — a bounds
  check using the same wrong unit as the allocation is still wrong.
- **Uninitialized data**: a buffer, padding, field, or capacity returned,
  compared, hashed, serialized, or passed across a trust boundary before
  initialization. Require an observable consumer and realistic output
  length.

## Lifetime and Concurrency Classes

- **Use-after-free, stale view, double free**: owners released while
  callbacks, wait queues, timers, iterators, borrowed slices, or cached
  raw pointers can still use them. Review every error, cancellation,
  close, and realloc path; embedded notification anchors must drain or
  detach observers on every free path.
- **Type confusion and invalid downcast**: a tag, vtable, union
  discriminator, or object kind checked differently from the
  representation later read — unchecked dynamic casts, stale tags after
  reuse, validated elements differing from consumed elements.
- **Reference-count and ownership races**: non-atomic retain or release,
  check-then-use across an unlocked window, inconsistent ownership rules
  across threads. Compare fast, error, shutdown, and compatibility paths
  for the same lock and ownership rules.
- **Shared-state races and TOCTOU**: concurrent parser streams, global
  caches, lazy initialization, signal handlers, and teardown invalidating
  bounds or pointers established earlier. Verify with a repeatable local
  schedule or thread sanitizer; a hypothetical interleaving stays
  `needs_validation`.
- **Lock-order, deadlock, starvation**: externally reachable operations
  acquiring locks inconsistently or holding them across callbacks and
  blocking I/O. Availability impact only when bounded input stops shared
  progress.

## FFI and ABI Classes

- **Pointer-length and ownership mismatch**: caller and callee
  disagreeing on who allocates, frees, pins, or mutates a buffer; pointer
  validity lifetime; bytes versus elements. Trace both sides of every
  `extern`, CGo, JNI, and native binding; check null, zero length,
  aliasing, callback retention.
- **Layout and enum disagreement**: foreign code receiving a struct,
  bitfield, packed record, callback signature, integer width, or calling
  convention that differs by architecture or build flag. Verify `repr`,
  packing, alignment, endianness. In-repo declaration mismatches confirm
  locally; opaque foreign implementations need `needs_validation`.
- **Unwind and thread-affinity violations**: exceptions or panics
  crossing an ABI that forbids unwinding; callbacks after teardown;
  single-thread-runtime APIs invoked elsewhere. Confirm abort versus
  corrupted state before assigning impact.

## Loader and Runtime Classes

- **Search-order trust**: a privileged process loading a library, plugin,
  runtime image, or helper from a path writable by a less-trusted
  principal, or resolving a bare name through an attacker-influenceable
  working directory or environment. A user loading their own plugin into
  their own process is not a boundary violation.
- **Identity or signature binding gaps**: a loader verifying one file or
  metadata record but mapping a different image because path resolution,
  file replacement, architecture slices, or embedded resources are not
  bound to the check.
- **Malformed binary metadata**: offsets, counts, sections, relocations,
  symbols, or debug metadata trusted before range, overlap, and
  representation checks. Test with bounded local fixtures and
  sanitizers; separate memory corruption from a safely rejected
  malformed file.
- **JIT and generated-code consistency**: validator, interpreter,
  optimizer, and generated code disagreeing about types, bounds, side
  effects, or lifetime. Diff optimized and unoptimized paths on the same
  local input; output variance within language semantics is not a
  finding.
- **Unload and teardown safety**: live function pointers, callbacks,
  worker threads, or data views surviving module unload or runtime reset.
  Review shutdown and failed-load cleanup as closely as startup.

## Kernel and Privileged Interfaces

- **User-copy bounds and repeated reads**: a syscall, ioctl, or driver
  deriving a trusted fact from user memory then reading the same mutable
  address again — copy the full request once or revalidate the later
  copy; audit size, direction, and access checks at each primitive.
- **Object lifecycle and dispatch consistency**: externally reachable
  objects with unbalanced retain and release, teardown without observer
  drain, unchecked selector or table indices, duplicated compatibility
  paths omitting a guard.
- **Under-authorized powerful interfaces**: a device node, admin socket,
  helper, or management API validating shape but not caller authority.
  Permissions or sandbox policy outside the repository make it
  `needs_validation`.

## Moves and Validation

Audit fixes and duplicated paths for the same source-to-sink shape: a
check in one caller, architecture, protocol role, feature flag, or
compatibility path does not protect its siblings. Build a table for every
parser or FFI boundary — accepted length and type, checked
representation, allocation owner, consumer, thread, teardown — most
native findings are one disagreement in that table. Use existing corpora
and small boundary fixtures; save exact sanitizer output and the input
property that triggers it.

Before reporting: establish a realistic untrusted entry and the exact
violated invariant; classify the observable effect — invalid read, write,
stale alias, wrong object, uninitialized output, unauthorized image load,
deadlock, safe termination — and never claim a stronger effect than
observed; run the narrowest local harness, test, sanitizer, or fuzzer,
verifying sanitizer coverage of the faulting operation and recording
architecture and build conditions.
