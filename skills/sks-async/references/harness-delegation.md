# Harness delegation mapping

The fan-out contract is harness-neutral: one child per leaf, the goal carries
the contract, the parent re-verifies every gate. Skill bodies never name the
dispatch primitive; resolve it here.

| Harness     | Dispatch primitive                                              |
| ----------- | --------------------------------------------------------------- |
| Hermes      | `delegate_task(tasks=[…])` — `goal` carries the contract        |
| DSH         | `subagent` / `subagent_fork` (fresh-context child); `spawn_teammate` + `send_message` for durable teammates |
| Claude Code | Task tool subagent, one task per leaf                           |
| Other       | Any primitive that runs a child agent in its own context and returns a result |

Rules that hold everywhere:

- One child per leaf; never bundle two leaves (defeats isolation).
- The child receives the contract (workspace path, unit gates, commit shape),
  not the parent's session context.
- The parent re-verifies every gate against real output — child self-reports
  are claims, not evidence.
