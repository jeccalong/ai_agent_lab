import "dotenv/config";
import { ChatOpenAI } from "@langchain/openai";
import { createToolCallingAgent, AgentExecutor } from "@langchain/classic/agents";
import { Calculator } from "@langchain/community/tools/calculator";
import { DynamicTool } from "@langchain/core/tools";
import { ChatPromptTemplate, MessagesPlaceholder } from "@langchain/core/prompts";

/**
 * Main function to initialize and run the AI Agent
 */
async function main() {
  console.log("🤖 Starting JavaScript LangChain AI Agent...");

  // 1. Load and verify GitHub Token
  const token = process.env.GITHUB_TOKEN;
  if (!token) {
    console.error("❌ ERROR: GITHUB_TOKEN is not set in your .env file.");
    console.log("Please add GITHUB_TOKEN=your_token_here to the .env file in the project root.");
    process.exit(1);
  }
  console.log("✅ GITHUB_TOKEN loaded successfully.");

  // 2. Initialize the Model (GitHub Models API)
  const llm = new ChatOpenAI({
    model: "openai/gpt-4o",
    temperature: 0,
    apiKey: token,
    configuration: {
      baseURL: "https://models.github.ai/inference",
    },
  });

  // 3. Define the Tools
  const tools = [
    new Calculator(),
    new DynamicTool({
      name: "get_current_time",
      description: "Returns the current date in yyyy-MM-dd format.",
      func: async () => {
        const now = new Date();
        // Pad month and day to two digits
        const yyyy = now.getFullYear();
        const mm = String(now.getMonth() + 1).padStart(2, '0');
        const dd = String(now.getDate()).padStart(2, '0');
        return `${yyyy}-${mm}-${dd}`;
      },
    }),
    new DynamicTool({
      name: "get_weather",
      description: "Returns mock weather for a given date (yyyy-MM-dd). If the date is today, returns 'Sunny, 72°F'. Otherwise, returns 'Rainy, 55°F'. Input should be a string date in yyyy-MM-dd format.",
      func: async (date) => {
        const now = new Date();
        const yyyy = now.getFullYear();
        const mm = String(now.getMonth() + 1).padStart(2, '0');
        const dd = String(now.getDate()).padStart(2, '0');
        const today = `${yyyy}-${mm}-${dd}`;
        if (date === today) {
          return "Sunny, 72°F";
        } else {
          return "Rainy, 55°F";
        }
      },
    }),
    new DynamicTool({
      name: "reverse_string",
      description: "Reverses a string. Input should be a single string.",
      func: async (input) => input.split("").reverse().join(""),
    }),
  ];

  // 4. Create the Prompt Template
  // Note: 'agent_scratchpad' is required for the agent to track its thoughts and tool outputs
  const prompt = ChatPromptTemplate.fromMessages([
    ["system", "You are a professional and succinct AI assistant."],
    ["human", "{input}"],
    new MessagesPlaceholder("agent_scratchpad"),
  ]);

  // 5. Initialize the Agent and Executor
  // We use createToolCallingAgent and AgentExecutor from @langchain/classic/agents
  // to ensure compatibility with the GitHub Models API formatting requirements.
  const agent = await createToolCallingAgent({ llm, tools, prompt });
  const executor = new AgentExecutor({ 
    agent, 
    tools, 
    verbose: true 
  });

  // 6. Run Example Queries
  const queries = [
    "What's the weather like today?",
    "What time is it right now?",
    "What is 25 * 4 + 10?",
    "Reverse the string 'Hello World'"
  ];

  console.log("\n🚀 Running example queries:");
  
  for (const query of queries) {
    console.log("─".repeat(50));
    console.log(`📝 Query: ${query}`);
    
    try {
      const result = await executor.invoke({ input: query });
      console.log(`✅ Result: ${result.output}`);
    } catch (err) {
      console.error(`❌ Error during query: ${err.message}`);
    }
  }

  console.log("─".repeat(50));
  console.log("\n✅ All tasks completed!");
}

// Start the application
main().catch((err) => {
  console.error("❌ Fatal Error:", err);
});

