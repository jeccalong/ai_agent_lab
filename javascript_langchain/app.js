import readline from "readline";
import { z } from "zod";
import { initializeAgentExecutorWithOptions } from "@langchain/classic/agents";
import { DynamicStructuredTool } from "@langchain/core/tools";
import { DynamicTool } from "@langchain/core/tools";
import "dotenv/config";
import { ChatOpenAI } from "@langchain/openai";

async function main() {
    // === API Safety Flags ===
    const DRY_RUN = true; // Set to true to skip API calls
    const COOLDOWN_MS = 10000; // 10 seconds cooldown after each call

    // Helper for user confirmation
    function askUser(question) {
      const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
      return new Promise((resolve) => rl.question(question, (ans) => { rl.close(); resolve(ans); }));
    }
  console.log("🤖 JavaScript LangChain Agent Starting...");

  // Load GitHub Models token
  const token = process.env.GITHUB_TOKEN;

  if (!token) {
    throw new Error("GITHUB_TOKEN is not set in environment variables.");
  }

  console.log("✅ GITHUB_TOKEN loaded successfully!");

  // Create ChatOpenAI instance targeting GitHub Models
  const model = new ChatOpenAI({
    model: "openai/gpt-4o",
    temperature: 0,
    apiKey: token,

    // CRITICAL: GitHub Models endpoint
    configuration: {
      baseURL: "https://models.github.ai/inference",
      defaultHeaders: {
        Authorization: `Bearer ${token}`,
      },
    },
  });

  // Create tools array with DynamicStructuredTool for calculator using zod schema
  const tools = [
    new DynamicStructuredTool({
      name: "calculator",
      description: "Evaluate a basic arithmetic expression and return the numeric result.",
      schema: z.object({
        input: z.string().describe("A math expression like '25 * 4 + 10'")
      }),
      func: async ({ input }) => {
        if (!/^[0-9+\-*/().\s]+$/.test(input)) {
          throw new Error("Invalid characters in expression.");
        }
        // eslint-disable-next-line no-new-func
        const result = Function(`"use strict"; return (${input});`)();
        return String(result);
      }
    })
  ];

  // Create agent executor
  const executor = await initializeAgentExecutorWithOptions(
    tools,
    model,
    {
      agentType: "openai-functions",
      verbose: true,
    }
  );

  const query = "What is 25 * 4 + 10?";
  console.log("📝 Query:", query);

  if (DRY_RUN) {
    console.log("[DRY_RUN] Skipping API call. No request sent.");
    return;
  }

  const ans = await askUser("Proceed with API call? (y/N): ");
  if (ans.trim().toLowerCase() !== "y") {
    console.log("Aborted by user. No API call made.");
    return;
  }

  try {
    const result = await executor.invoke({ input: query });
    console.log("✅ Result:", result.output);
    if (COOLDOWN_MS > 0) {
      console.log(`Cooldown: Waiting ${COOLDOWN_MS / 1000} seconds before next call...`);
      await new Promise((res) => setTimeout(res, COOLDOWN_MS));
    }
  } catch (err) {
    if (err && err.status === 429) {
      console.error("❌ Rate limit hit. Stopping further requests.");
      process.exit(1);
    }
    console.error("❌ Error invoking agent executor:", err);
  }
}

main().catch((err) => {
  console.error("❌ Error invoking model:", err);
});
