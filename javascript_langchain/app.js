import "dotenv/config";
import { ChatOpenAI } from "@langchain/openai";

async function main() {
  console.log("🤖 JavaScript LangChain Agent Starting...");

  const token = process.env.GITHUB_TOKEN;

  if (!token) {
    throw new Error("GITHUB_TOKEN is not set in environment variables.");
  }

  console.log("✅ GITHUB_TOKEN loaded successfully!");

  // IMPORTANT:
  // We must explicitly override BOTH the baseURL AND defaultHeaders
  // or the OpenAI client will silently route to api.openai.com
  const model = new ChatOpenAI({
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

  const query = "What is 25 * 4 + 10?";
  console.log("📝 Query:", query);

  const response = await model.invoke(query);
  console.log("✅ Response:", response.content);
}

main().catch((err) => {
  console.error("❌ Error invoking model:", err);
});
