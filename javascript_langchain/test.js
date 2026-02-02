import "dotenv/config";
import { z } from "zod";

import { ChatOpenAI } from "@langchain/openai";
import { DynamicStructuredTool } from "@langchain/core/tools";
import { ChatPromptTemplate, MessagesPlaceholder } from "@langchain/core/prompts";
import { createToolCallingAgent } from "@langchain/core/agents";

async function main() {
  console.log("🤖 JS Tool-Calling Agent Test Starting...");

  const token = process.env.GITHUB_TOKEN;
  if (!token) throw new Error("GITHUB_TOKEN is not set in .env");
  console.log("✅ GITHUB_TOKEN loaded successfully!");

  // GitHub Models endpoint
  const llm = new ChatOpenAI({
    model: "openai/gpt-4o",
    temperature: 0,
    apiKey: token,
    configuration: {
      baseURL: "https://models.github.ai/inference",
      defaultHeaders: {
        Authorization: `Bearer ${token}`,
      },
    },
  });

  // Named + structured tool (avoids anonymous FunctionMessage)
  const calculator = new DynamicStructuredTool({
    name: "calculator",
    description: "Evaluate a basic arithmetic expression and return the numeric result.",
    schema: z.object({
      input: z.string().describe("A math expression like '25 * 4 + 10'"),
    }),
    func: async ({ input }) => {
      if (!/^[0-9+\-*/().\s]+$/.test(input)) {
        throw new Error("Invalid characters in expression.");
      }
      // eslint-disable-next-line no-new-func
      const result = Function(`"use strict"; return (${input});`)();
      return String(result);
    },
  });

  const tools = [calculator];

  const prompt = ChatPromptTemplate.fromMessages([
    ["system", "You are a helpful AI assistant."],
    ["human", "{input}"],
    new MessagesPlaceholder("agent_scratchpad"),
  ]);

  // Create tool-calling agent
  const agent = await createToolCallingAgent({ llm, tools, prompt });

  // Run a single turn manually (no AgentExecutor needed)
  const query = "What is 25 * 4 + 10?";
  console.log("📝 Query:", query);

  const result = await agent.invoke({ input: query });
  console.log("✅ Raw Agent Result:", result);
}

main().catch((err) => {
  console.error("❌ Error:", err);
});
