import type { Plugin } from "@opencode-ai/plugin"
import { spawnSync } from "node:child_process"

export const CheckNodeVersion: Plugin = async ({ worktree }) => {
  return {
    "tool.execute.before": async (input, output) => {
      if (input.tool !== "bash") return

      const payload = JSON.stringify({ tool_input: { command: output.args.command } })
      const scriptPath = `${worktree}/.agents/scripts/check-node-version.sh`

      const result = spawnSync("bash", [scriptPath], {
        input: payload,
        encoding: "utf-8",
      })

      const warning = result.stderr?.trim()
      if (warning) {
        console.warn(warning)
      }
    },
  }
}
