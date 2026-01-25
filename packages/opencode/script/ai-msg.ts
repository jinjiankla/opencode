#!/usr/bin/env bun

import { Provider } from "../src/provider/provider"
import { generateText } from "ai"
import { $ } from "bun"
import { Instance } from "../src/project/instance"
import { Log } from "../src/util/log"

async function main() {
  await Log.init({ print: true, level: "ERROR" })
  const root = (await $`git rev-parse --show-toplevel`.text()).trim()
  
  const diff = await $`git diff --cached`.text()
  if (!diff.trim()) {
    console.error("No staged changes found.")
    process.exit(1)
  }

  await Instance.provide({
    directory: root,
    fn: async () => {
      const defaultModel = await Provider.defaultModel()
      const model = await Provider.getModel(defaultModel.providerID, defaultModel.modelID)
      const language = await Provider.getLanguage(model)

      const { text } = await generateText({
        model: language,
        prompt: `You are a professional software engineer. Generate a concise and meaningful git commit message for the following changes. 
Follow the Conventional Commits specification (e.g., feat: ..., fix: ..., docs: ..., style: ..., refactor: ..., test: ..., chore: ...).
Do not include any other text, explanations, or backticks. Just the commit message itself.

Changes:
${diff}`,
      })

      process.stdout.write(text.trim())
    }
  })
}

main().catch(err => {
  console.error(err)
  process.exit(1)
})
