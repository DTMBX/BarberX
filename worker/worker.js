// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

// Cloudflare Worker for Docket Upload (PR-based workflow)
// Deploy this to Cloudflare Workers and configure secrets

addEventListener("fetch", (event) => {
  event.respondWith(handleRequest(event.request));
});

async function handleRequest(request) {
  // CORS headers
  const corsHeaders = {
    "Access-Control-Allow-Origin": "https://faithfrontier.org",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
  };

  if (request.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  if (request.method !== "POST") {
    return new Response("Method not allowed", { status: 405 });
  }

  try {
    const data = await request.json();
    const { slug, date, type, title, notes, filename, content } = data;

    // Validate inputs
    if (!slug || !date || !type || !title || !filename || !content) {
      return new Response(JSON.stringify({ error: "Missing required fields" }), {
        status: 400,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // GitHub API credentials from environment
    const GITHUB_TOKEN = GITHUB_PAT; // Set this secret in Cloudflare Workers
    const REPO_OWNER = "XTX33";
    const REPO_NAME = "FaithFrontier";
    const BASE_BRANCH = "main";

    // Create a unique branch name
    const branchName = `docket/${slug}-${date}-${Date.now()}`;

    // Get the base branch SHA
    const baseRef = await fetch(
      `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/git/ref/heads/${BASE_BRANCH}`,
      {
        headers: {
          Authorization: `token ${GITHUB_TOKEN}`,
          "User-Agent": "FaithFrontier-DocketWorker",
        },
      }
    );
    const baseRefData = await baseRef.json();
    const baseSha = baseRefData.object.sha;

    // Create new branch
    await fetch(`https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/git/refs`, {
      method: "POST",
      headers: {
        Authorization: `token ${GITHUB_TOKEN}`,
        "User-Agent": "FaithFrontier-DocketWorker",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        ref: `refs/heads/${branchName}`,
        sha: baseSha,
      }),
    });

    // Prepare file path
    const sanitizedFilename = filename.replace(/[^a-zA-Z0-9._-]/g, "-");
    const pdfPath = `cases/${slug}/filings/${date}_${type}_${sanitizedFilename}`;

    // Upload PDF file
    await fetch(`https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/contents/${pdfPath}`, {
      method: "PUT",
      headers: {
        Authorization: `token ${GITHUB_TOKEN}`,
        "User-Agent": "FaithFrontier-DocketWorker",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: `chore(docket): add ${type} for ${slug}`,
        content: content,
        branch: branchName,
      }),
    });

    // Update docket YAML
    const docketPath = `_data/docket/${slug}.yml`;
    let docketYaml = "";

    // Try to get existing docket file
    const existingDocket = await fetch(
      `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/contents/${docketPath}?ref=${BASE_BRANCH}`,
      {
        headers: {
          Authorization: `token ${GITHUB_TOKEN}`,
          "User-Agent": "FaithFrontier-DocketWorker",
        },
      }
    );

    let docketSha = null;
    if (existingDocket.ok) {
      const existingData = await existingDocket.json();
      docketSha = existingData.sha;
      docketYaml = atob(existingData.content);
    }

    // Append new entry
    const id = `${date}-${title
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .substring(0, 40)}`;
    const newEntry = `
- id: ${id}
  date: ${date}
  type: ${type}
  title: ${title}
  file: /${pdfPath}${notes ? `\n  notes: ${notes}` : ""}`;

    docketYaml += newEntry + "\n";

    // Update/create docket file
    await fetch(`https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/contents/${docketPath}`, {
      method: "PUT",
      headers: {
        Authorization: `token ${GITHUB_TOKEN}`,
        "User-Agent": "FaithFrontier-DocketWorker",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: `chore(docket): update ${slug} docket with ${type}`,
        content: btoa(docketYaml),
        branch: branchName,
        ...(docketSha && { sha: docketSha }),
      }),
    });

    // Create pull request
    const prResponse = await fetch(
      `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/pulls`,
      {
        method: "POST",
        headers: {
          Authorization: `token ${GITHUB_TOKEN}`,
          "User-Agent": "FaithFrontier-DocketWorker",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          title: `chore(docket): add ${type} for ${slug}`,
          body: `## Docket Entry Submission\n\n- **Case:** ${slug}\n- **Date:** ${date}\n- **Type:** ${type}\n- **Title:** ${title}\n${notes ? `- **Notes:** ${notes}\n` : ""}\n- **File:** ${pdfPath}\n\nAutomatically generated from docket submission form.`,
          head: branchName,
          base: BASE_BRANCH,
        }),
      }
    );

    const prData = await prResponse.json();

    return new Response(
      JSON.stringify({
        success: true,
        pr_url: prData.html_url,
        pr_number: prData.number,
      }),
      {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      }
    );
  } catch (error) {
    return new Response(
      JSON.stringify({
        error: error.message,
      }),
      {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      }
    );
  }
}
