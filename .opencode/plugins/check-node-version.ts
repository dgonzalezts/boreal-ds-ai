import { Plugin } from "@opencode/plugin"
import { spawnSync } from "node:child_process"

export default Plugin.define({
  id: "boreal.check-node-version",
  async setup(ctx) {
    await ctx.shell.hook("create.before", (event) => {
      const command = event.command
      if (command === undefined) return

      const payload = JSON.stringify({ tool_input: { command } })
      const scriptPath = `${ctx.location.directory}/.agents/scripts/check-node-version.sh`

      const result = spawnSync("bash", [scriptPath], {
        input: payload,
        encoding: "utf-8",
      })

      const warning = result.stderr?.trim()
      if (warning) {
        console.warn(warning)
      }
    })
  },
})
