# FCSys: parallel session rules

1. Read AGENTS.md and the assigned task. Record owner, checkout, base revision,
   dirty inputs, exclusive files, checks, output path and execution limits.
2. Freeze the interface used by the task. Record producer/consumer versions,
   units, signs, frames, IDs, timing, operating limits and failure behavior.
3. Preserve compatibility. Propose interface changes to affected owners before
   implementation. Breaking changes need a new version and migration plan.
   Test the producer and consumer together; unavailable checks remain unverified.
4. Edit only assigned files. Separate chats share the same checkout and Git state.
   Use a separate development checkout for independent Git work or frozen integration
   runs. In shared checkouts, use one Git owner. Do not change sources during a run.
5. Use one owner per compiler/debugger/hardware session and separate output paths.
   Stop on ownership conflicts. Written ownership is not an enforced process lock.
6. Return changes, commit or dirty-source snapshot, commands/results, evidence,
   compatibility impact, unresolved issues and one next step in a task handoff.
7. Component owners accept internal work. The system integrator accepts the combined
   system and changes parent contracts, dependency pins and lock together. Publish
   referenced commits before release. Do not modify other repositories from this task.

These rules do not start work, authorize publication or resume paused implementation.
Preserve original sources and unrelated edits. Follow existing component governance.
