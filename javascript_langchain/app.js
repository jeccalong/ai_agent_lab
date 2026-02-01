// app.js
// JavaScript LangChain AI Agent - Starter
// Follows project and Copilot JS guidelines for clarity and maintainability.

import "dotenv/config";
import { ChatOpenAI } from "@langchain/openai";

/**
 * Main entry point for the AI agent demo.
 * Loads config, checks for token, runs a test query.
 */
async function main() {
  console.log("🤖 JavaScript LangChain Agent Starting...");

  // Check for GITHUB_TOKEN in environment variables
  const token = process.env.GITHUB_TOKEN;
  if (!token) {
    console.error("❌ GITHUB_TOKEN not found in environment variables.");
    console.error("👉 Please create a .env file in your project root with:");
    console.error("   GITHUB_TOKEN=your_token_here");
    console.error("🔒 Never commit your .env file to version control!");
    process.exit(1);
  }
  console.log("✅ GITHUB_TOKEN loaded successfully!");

  // Create ChatOpenAI instance
  const model = new ChatOpenAI({
    model: "openai/gpt-4o",
    temperature: 0,
    baseURL: "https://models.github.ai/inference",
    apiKey: token,
  });

  // Run a test query
  const query = "What is 25 * 4 + 10?";
  console.log(`📝 Query: ${query}`);
  try {
    const response = await model.invoke(query);
    console.log("🤖 Response:");
    console.log(response.content);
  } catch (err) {
    console.error("❌ Error invoking model:", err);
  }
}

main().catch(console.error);
