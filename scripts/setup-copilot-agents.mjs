#!/usr/bin/env node

/**
 * Evident Custom Copilot Agents - Setup Script
 * Validates and registers custom agents for the legal tech platform
 */

import { readFileSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load agents configuration
const agentsPath = join(__dirname, "..", ".github", "copilot-agents.yml");
console.log("📋 Loading agents from:", agentsPath);

try {
  const agentsConfig = readFileSync(agentsPath, "utf8");
  console.log("✅ Successfully loaded copilot-agents.yml");
  console.log("\n🤖 Registered Agents:\n");

  // Parse and display agent names (simple regex for YAML parsing)
  const agentMatches = agentsConfig.matchAll(/^  ([a-z-]+):/gm);
  const agents = Array.from(agentMatches).map((match) => match[1]);

  agents.forEach((agent, index) => {
    console.log(`  ${index + 1}. ${agent}`);
  });

  console.log(`\n✨ Total agents registered: ${agents.length}`);
  console.log("\n📖 Usage:");
  console.log(
    "  Use @agent-name in GitHub Copilot Chat to invoke specific agents",
  );
  console.log('  Example: @legal-compliance "Review this export function"');
  console.log("\n🎯 Available Agents:");
  console.log("  • @legal-compliance - Copyright & data rights expert");
  console.log("  • @bwc-forensics - BWC video analysis specialist");
  console.log("  • @flask-backend - Flask API & backend developer");
  console.log("  • @frontend-dev - React/UI component expert");
  console.log("  • @database-architect - Database schema designer");
  console.log("  • @security-devops - Security & deployment expert");
  console.log("  • @documentation - Technical writing specialist");
} catch (error) {
  console.error("❌ Error loading agents configuration:", error.message);
  process.exit(1);
}
