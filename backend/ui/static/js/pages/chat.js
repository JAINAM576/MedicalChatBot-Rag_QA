const chatWindow = document.getElementById("chatWindow");
const chatForm = document.getElementById("chatForm");
const queryInput = document.getElementById("queryInput");
const modelSelect = document.getElementById("modelSelect");
const clearChatBtn = document.getElementById("clearChatBtn");
const thinkingState = document.getElementById("thinkingState");
const pdfViewer = document.getElementById("pdfViewer");
const evidenceMeta = document.getElementById("evidenceMeta");
const evidenceChunk = document.getElementById("evidenceChunk");

const thinkingMessages = [
  "Retrieving relevant medical context...",
  "Reviewing pages for evidence...",
  "Composing grounded answer...",
  "Finalizing concise response...",
];
let thinkingTimer = null;

function nowTime() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function markdownToHtml(text) {
  const escaped = escapeHtml(text || "");
  const lines = escaped.split("\n");
  const out = [];
  let inUl = false;
  let inOl = false;

  const closeLists = () => {
    if (inUl) {
      out.push("</ul>");
      inUl = false;
    }
    if (inOl) {
      out.push("</ol>");
      inOl = false;
    }
  };

  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (!line) {
      closeLists();
      continue;
    }

    const hMatch = line.match(/^(#{1,4})\s+(.*)$/);
    if (hMatch) {
      closeLists();
      const level = hMatch[1].length;
      out.push(`<h${level}>${hMatch[2]}</h${level}>`);
      continue;
    }

    const ulMatch = line.match(/^[-*]\s+(.*)$/);
    if (ulMatch) {
      if (!inUl) {
        closeLists();
        out.push("<ul>");
        inUl = true;
      }
      out.push(`<li>${ulMatch[1]}</li>`);
      continue;
    }

    const olMatch = line.match(/^\d+\.\s+(.*)$/);
    if (olMatch) {
      if (!inOl) {
        closeLists();
        out.push("<ol>");
        inOl = true;
      }
      out.push(`<li>${olMatch[1]}</li>`);
      continue;
    }

    closeLists();
    out.push(`<p>${line}</p>`);
  }

  closeLists();

  return out
    .join("\n")
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/g, "<em>$1</em>")
    .replace(/`([^`]+)`/g, "<code>$1</code>");
}

function updateEvidencePanel(source, query) {
  if (!source || !source.title) {
    evidenceMeta.textContent = "No source selected yet.";
    evidenceChunk.textContent = "The matched source snippet will appear here.";
    pdfViewer.removeAttribute("src");
    return;
  }

  const pageLabel = source.page ? `Page ${source.page}` : "Page N/A";
  evidenceMeta.textContent = `${source.title} | ${pageLabel}`;
  evidenceChunk.innerHTML = highlightTerms(source.snippet || "", query || "");

  const pageFragment = source.page ? `#page=${source.page}` : "";
  pdfViewer.src = `/pdf/${encodeURIComponent(source.title)}${pageFragment}`;
}

function highlightTerms(text, query) {
  const words = query
    .toLowerCase()
    .split(/\s+/)
    .map((w) => w.replace(/[^a-z0-9]/g, ""))
    .filter((w) => w.length > 3)
    .slice(0, 6);

  if (!words.length) {
    return escapeHtml(text);
  }

  const escaped = escapeHtml(text);
  const pattern = new RegExp(`\\b(${words.join("|")})\\b`, "gi");
  return escaped.replace(pattern, "<mark>$1</mark>");
}

function appendMessage(role, content, extras = {}) {
  const wrapper = document.createElement("article");
  wrapper.className = `msg ${role}`;

  const meta = document.createElement("div");
  meta.className = "meta";
  meta.innerHTML = `<span>${role === "user" ? "You" : "Assistant"}</span><span class=\"time\">${extras.time || nowTime()}</span>`;

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  if (role === "assistant") {
    bubble.innerHTML = markdownToHtml(content);
  } else {
    bubble.textContent = content;
  }

  wrapper.appendChild(meta);
  wrapper.appendChild(bubble);

  if (role === "assistant" && typeof extras.responseTime === "number") {
    const rt = document.createElement("div");
    rt.className = "meta";
    rt.innerHTML = `<span>Model: ${escapeHtml(extras.model || "N/A")}</span><span>Response: ${extras.responseTime.toFixed(2)}s</span>`;
    wrapper.appendChild(rt);
  }

  if (Array.isArray(extras.sources) && extras.sources.length) {
    const sourcesBlock = document.getElementById("sourcesTemplate").content.cloneNode(true);
    const sourceList = sourcesBlock.querySelector(".source-list");

    extras.sources.forEach((source, index) => {
      const card = document.createElement("article");
      card.className = "source-card";

      const pageLabel = source.page ? `Page ${source.page}` : "Page N/A";
      const pageFragment = source.page ? `#page=${source.page}` : "";
      const sourceFile = source.title || "Unknown Source";

      card.innerHTML = `
        <div class="source-head">
          <span class="source-title">${escapeHtml(sourceFile)}</span>
          <span class="page-badge">${pageLabel}</span>
        </div>
        <div class="source-snippet">${highlightTerms(source.snippet || "", extras.query || "")}</div>
        <a class="source-link" href="/pdf/${encodeURIComponent(sourceFile)}${pageFragment}" target="_blank" rel="noopener noreferrer">Open PDF at source</a>
      `;

      card.addEventListener("click", () => {
        updateEvidencePanel(source, extras.query || "");
      });

      sourceList.appendChild(card);

      if (index === 0) {
        updateEvidencePanel(source, extras.query || "");
      }
    });

    wrapper.appendChild(sourcesBlock);
  }

  const copyBtn = document.createElement("button");
  copyBtn.className = "secondary";
  copyBtn.type = "button";
  copyBtn.textContent = "Copy";
  copyBtn.style.marginTop = "8px";
  copyBtn.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(content);
      copyBtn.textContent = "Copied";
      setTimeout(() => {
        copyBtn.textContent = "Copy";
      }, 1200);
    } catch (_err) {
      copyBtn.textContent = "Copy failed";
    }
  });

  if (role === "assistant") {
    wrapper.appendChild(copyBtn);
  }

  chatWindow.appendChild(wrapper);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function setThinking(active) {
  if (!active) {
    thinkingState.classList.add("hidden");
    clearInterval(thinkingTimer);
    thinkingTimer = null;
    thinkingState.textContent = "Thinking...";
    return;
  }

  let idx = 0;
  thinkingState.classList.remove("hidden");
  thinkingState.textContent = thinkingMessages[idx];
  thinkingTimer = setInterval(() => {
    idx = (idx + 1) % thinkingMessages.length;
    thinkingState.textContent = thinkingMessages[idx];
  }, 1300);
}

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const query = queryInput.value.trim();
  if (!query) {
    return;
  }

  appendMessage("user", query, { time: nowTime() });
  queryInput.value = "";
  setThinking(true);

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query,
        model: modelSelect.value,
      }),
    });

    const data = await response.json();
    if (!response.ok) {
      appendMessage("assistant", data.error || "Something went wrong while generating the answer.", {
        responseTime: 0,
        model: modelSelect.value,
      });
      return;
    }

    appendMessage("assistant", data.answer || "No answer generated.", {
      responseTime: data.response_time_seconds || 0,
      model: data.model || modelSelect.value,
      sources: data.sources || [],
      query,
    });
  } catch (_error) {
    appendMessage("assistant", "Network error. Please try again.", {
      responseTime: 0,
      model: modelSelect.value,
    });
  } finally {
    setThinking(false);
  }
});

queryInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    chatForm.requestSubmit();
  }
});

clearChatBtn.addEventListener("click", () => {
  chatWindow.innerHTML = "";
  updateEvidencePanel(null, "");
  appendMessage("assistant", "Chat cleared. Ask another question from the PDF whenever you are ready.", {
    time: nowTime(),
  });
});
