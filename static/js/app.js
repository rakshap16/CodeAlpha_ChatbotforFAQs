document.addEventListener("DOMContentLoaded", () => {
  const chatForm = document.getElementById("chat-form");
  const userInput = document.getElementById("user-input");
  const messagesContainer = document.getElementById("messages-container");
  const typingIndicator = document.getElementById("typing-indicator");
  const clearChatBtn = document.getElementById("clear-chat-btn");
  const toggleDiagnosticsBtn = document.getElementById("toggle-diagnostics-btn");
  const closeDiagnosticsBtn = document.getElementById("close-diagnostics-btn");
  const diagnosticsPanel = document.getElementById("diagnostics-panel");

  const toggleFaqsBtn = document.getElementById("toggle-faqs-btn");
  const closeModalBtn = document.getElementById("close-modal-btn");
  const faqsModal = document.getElementById("faqs-modal");
  const faqsList = document.getElementById("faqs-list");
  const faqSearchInput = document.getElementById("faq-search-input");

  let allFaqsData = {};

  // Scroll messages container to the bottom
  function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  // Append a user message bubble
  function appendUserMessage(text) {
    const row = document.createElement("div");
    row.className = "message-row user-row";

    const avatar = document.createElement("div");
    avatar.className = "msg-avatar user-avatar-small";
    avatar.innerText = "👤";

    const bubble = document.createElement("div");
    bubble.className = "bubble user-bubble";
    const p = document.createElement("p");
    p.innerText = text;
    bubble.appendChild(p);

    row.appendChild(avatar);
    row.appendChild(bubble);
    messagesContainer.appendChild(row);
    scrollToBottom();
  }

  // Append a bot message bubble
  function appendBotMessage(data) {
    const row = document.createElement("div");
    row.className = "message-row bot-row";

    const avatar = document.createElement("div");
    avatar.className = "msg-avatar bot-avatar-small";
    avatar.innerText = "🤖";

    const bubble = document.createElement("div");
    bubble.className = "bubble bot-bubble";

    const p = document.createElement("p");
    p.innerText = data.response;
    bubble.appendChild(p);

    // Metadata & Confidence badge
    const meta = document.createElement("div");
    meta.className = "bubble-meta";

    if (data.type === "faq_match") {
      const confPct = (data.confidence * 100).toFixed(1);
      meta.innerHTML = `
        <span class="badge-confidence">🎯 ${confPct}% Match</span>
        <span>Matched: "${escapeHtml(data.matched_question || "")}"</span>
        <span>&bull; ${escapeHtml(data.category || "")}</span>
      `;
      bubble.appendChild(meta);
    } else if (data.type === "intent") {
      meta.innerHTML = `<span class="badge-confidence">Intent: ${escapeHtml(data.intent || "Conversational")}</span>`;
      bubble.appendChild(meta);
    }

    // Suggestions box if provided
    if (data.suggestions && data.suggestions.length > 0) {
      const sugBox = document.createElement("div");
      sugBox.className = "suggestions-box";
      const title = document.createElement("div");
      title.className = "suggestions-title";
      title.innerText = "Related Questions:";
      sugBox.appendChild(title);

      data.suggestions.slice(0, 3).forEach((sugText) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "suggestion-btn";
        btn.innerText = `💡 ${sugText}`;
        btn.addEventListener("click", () => {
          submitQuery(sugText);
        });
        sugBox.appendChild(btn);
      });
      bubble.appendChild(sugBox);
    }

    row.appendChild(avatar);
    row.appendChild(bubble);
    messagesContainer.appendChild(row);
    scrollToBottom();
  }

  function escapeHtml(str) {
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // Update NLP Diagnostics Panel
  function updateDiagnostics(data) {
    const diag = data.diagnostics || {};
    document.getElementById("diag-raw").innerText = data.query || "-";
    document.getElementById("diag-tokens").innerText = JSON.stringify(diag.tokens || [], null, 2);
    document.getElementById("diag-stopwords").innerText = JSON.stringify(diag.after_stopwords || [], null, 2);
    document.getElementById("diag-lemmas").innerText = JSON.stringify(diag.lemmatized_tokens || [], null, 2);
    document.getElementById("diag-normalized").innerText = diag.normalized_string || "-";

    const matchInfo = {
      type: data.type,
      confidence: data.confidence,
      matched_question: data.matched_question,
      category: data.category
    };
    document.getElementById("diag-matching").innerText = JSON.stringify(matchInfo, null, 2);
  }

  // Send query to server
  async function submitQuery(queryText) {
    const cleanText = queryText.trim();
    if (!cleanText) return;

    appendUserMessage(cleanText);
    userInput.value = "";
    userInput.focus();

    // Show typing indicator
    typingIndicator.classList.remove("hidden");
    scrollToBottom();

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: cleanText })
      });

      const data = await response.json();
      typingIndicator.classList.add("hidden");

      if (response.ok) {
        appendBotMessage(data);
        updateDiagnostics(data);
      } else {
        appendBotMessage({
          type: "error",
          response: data.response || "Something went wrong. Please try again.",
          confidence: 0.0
        });
      }
    } catch (err) {
      typingIndicator.classList.add("hidden");
      appendBotMessage({
        type: "error",
        response: "Network error: Unable to connect to NovaBot server. Please ensure the server is running.",
        confidence: 0.0
      });
      console.error(err);
    }
  }

  // Form submit handler
  chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    submitQuery(userInput.value);
  });

  // Quick topics chips
  document.querySelectorAll(".topic-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      const query = chip.getAttribute("data-query");
      submitQuery(query);
    });
  });

  // Clear chat
  clearChatBtn.addEventListener("click", () => {
    messagesContainer.innerHTML = `
      <div class="message-row bot-row">
        <div class="msg-avatar bot-avatar-small">🤖</div>
        <div class="bubble bot-bubble">
          <p>Chat history cleared. How can I help you today?</p>
        </div>
      </div>
    `;
  });

  // Toggle Diagnostics Panel
  toggleDiagnosticsBtn.addEventListener("click", () => {
    diagnosticsPanel.classList.toggle("hidden");
  });

  closeDiagnosticsBtn.addEventListener("click", () => {
    diagnosticsPanel.classList.add("hidden");
  });

  // FAQ Modal Handling
  async function loadFaqs() {
    try {
      const res = await fetch("/api/faqs");
      const data = await res.json();
      if (data.status === "success") {
        allFaqsData = data.categories;
        renderFaqsList();
      }
    } catch (err) {
      console.error("Failed to load FAQs", err);
    }
  }

  function renderFaqsList(filter = "") {
    faqsList.innerHTML = "";
    const filterLower = filter.toLowerCase();

    for (const [category, items] of Object.entries(allFaqsData)) {
      const matchingItems = items.filter(
        (item) =>
          item.question.toLowerCase().includes(filterLower) ||
          item.answer.toLowerCase().includes(filterLower) ||
          category.toLowerCase().includes(filterLower)
      );

      if (matchingItems.length > 0) {
        const catTitle = document.createElement("div");
        catTitle.className = "faq-group-title";
        catTitle.innerText = category;
        faqsList.appendChild(catTitle);

        matchingItems.forEach((faq) => {
          const itemDiv = document.createElement("div");
          itemDiv.className = "faq-item";
          itemDiv.innerHTML = `
            <div class="faq-item-q">${escapeHtml(faq.question)}</div>
            <div class="faq-item-a">${escapeHtml(faq.answer)}</div>
          `;
          itemDiv.addEventListener("click", () => {
            faqsModal.classList.add("hidden");
            submitQuery(faq.question);
          });
          faqsList.appendChild(itemDiv);
        });
      }
    }

    if (faqsList.children.length === 0) {
      faqsList.innerHTML = `<p style="color: #64748b; padding: 10px;">No FAQs match your search.</p>`;
    }
  }

  toggleFaqsBtn.addEventListener("click", () => {
    faqsModal.classList.remove("hidden");
    if (Object.keys(allFaqsData).length === 0) {
      loadFaqs();
    }
  });

  closeModalBtn.addEventListener("click", () => {
    faqsModal.classList.add("hidden");
  });

  faqSearchInput.addEventListener("input", (e) => {
    renderFaqsList(e.target.value);
  });

  // Close modal when clicking outside modal-content
  faqsModal.addEventListener("click", (e) => {
    if (e.target === faqsModal) {
      faqsModal.classList.add("hidden");
    }
  });
});
