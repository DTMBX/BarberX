// Docket submission via Cloudflare Worker
const form = document.getElementById("docket-form");
if (!form) {
  // Script may be loaded on pages without the form
  // (no-op)
} else {
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const status = document.getElementById("status");
    if (status) {
      status.textContent = "Submitting...";
      status.classList.remove("u-text-emerald", "u-text-accent");
      status.classList.add("u-text-muted");
    }

    const slug = document.getElementById("case-slug").value;
    const date = document.getElementById("entry-date").value;
    const type = document.getElementById("entry-type").value;
    const title = document.getElementById("entry-title").value;
    const notes = document.getElementById("entry-notes").value;
    const file = document.getElementById("pdf-file").files[0];

    if (!file) {
      if (status) {
        status.textContent = "Please select a PDF file.";
        status.classList.remove("u-text-muted", "u-text-emerald");
        status.classList.add("u-text-accent");
      }
      return;
    }

    // Read file as base64
    const reader = new FileReader();
    reader.onload = async () => {
      const base64 = reader.result.split(",")[1];

      try {
        // TODO: Replace with your Cloudflare Worker URL
        const workerUrl =
          "https://your-worker.your-subdomain.workers.dev/docket-upload";

        const response = await fetch(workerUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            slug,
            date,
            type,
            title,
            notes,
            filename: file.name,
            content: base64,
          }),
        });

        let result = null;
        try {
          result = await response.json();
        } catch (_err) {
          result = null;
        }

        if (response.ok) {
          if (status) {
            // DOM-safe message composition
            status.textContent = "";
            status.classList.remove("u-text-muted", "u-text-accent");
            status.classList.add("u-text-emerald");
            const prefix = document.createTextNode(
              "Success! Pull request created: ",
            );
            status.appendChild(prefix);
            if (result && result.pr_url) {
              const a = document.createElement("a");
              a.href = result.pr_url;
              a.target = "_blank";
              a.rel = "noopener";
              a.textContent = result.pr_url;
              status.appendChild(a);
            }
          }
          document.getElementById("docket-form").reset();
        } else {
          if (status) {
            status.textContent = `Error: ${result && result.error ? result.error : "Unknown error"}`;
            status.classList.remove("u-text-muted", "u-text-emerald");
            status.classList.add("u-text-accent");
          }
        }
      } catch (error) {
        if (status) {
          status.textContent = `Error: ${error.message}`;
          status.classList.remove("u-text-muted", "u-text-emerald");
          status.classList.add("u-text-accent");
        }
      }
    };

    reader.readAsDataURL(file);
  });
}
