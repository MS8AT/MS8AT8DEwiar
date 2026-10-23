# Dewiar code style

This style follows the existing Dewiar/MS8AT modules rather than introducing a new framework.

- Use the standard library unless an existing project dependency is necessary.
- Begin with a short module docstring that states responsibility and side effects.
- Keep constants uppercase, functions `snake_case`, and data JSON-compatible where practical.
- Prefer small pure helpers and explicit dictionaries over inheritance, registries, or hidden callbacks.
- Validate input at the boundary and refuse unknown actions or fields early.
- Fail closed: an unavailable check is `unknown` or `unavailable`, never a green result.
- Comments explain why a safety or compatibility rule exists; do not narrate obvious code.
- Keep adapters separate from the standalone core. The patch source must import without Dewiar.
- Tests use `unittest` or direct assertions, synthetic data, and the standard library.
- A unit test must not use the network, a model, an account, secrets, or real user files.
- Use Russian for local operator errors when it improves clarity; keep identifiers short English words consistent with the project.

Split a file when it gains a second responsibility, not merely because it reaches an arbitrary line count.
