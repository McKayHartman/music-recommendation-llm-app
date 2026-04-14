import { useState } from "react";

export default function App() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Ask for music and I will recommend songs."
    }
  ]);
  const [input, setInput] = useState("");
  const [useRag, setUseRag] = useState(true);
  const [useSystemPrompt, setUseSystemPrompt] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  async function sendMessage(text) {
    const message = text.trim();
    if (!message || isLoading) {
      return;
    }

    setError("");
    setMessages((current) => [...current, { role: "user", content: message }]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          message,
          useRag,
          useSystemPrompt
        })
      });

      const rawBody = await response.text();
      let data = {};

      if (rawBody) {
        try {
          data = JSON.parse(rawBody);
        } catch (parseError) {
          throw new Error(
            response.ok
              ? "The server returned a non-JSON response."
              : rawBody
          );
        }
      }

      if (!response.ok) {
        throw new Error(data.error || rawBody || "Something went wrong while fetching a reply.");
      }

      setMessages((current) => [
        ...current,
        { role: "assistant", content: data.reply || "No reply was returned by the server." }
      ]);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }

  function handleSubmit(event) {
    event.preventDefault();
    sendMessage(input);
  }

  return (
    <main className="app">
      <h1 className="title">Music Chat</h1>

      <div className="chat-log">
        {messages.map((message, index) => (
          <article
            key={`${message.role}-${index}`}
            className={`message message-${message.role}`}
          >
            <p>{message.content}</p>
          </article>
        ))}

        {isLoading ? (
          <article className="message message-assistant">
            <p>Thinking...</p>
          </article>
        ) : null}
      </div>

      {error ? <p className="error-banner">{error}</p> : null}

      <form className="composer" onSubmit={handleSubmit}>
        <div className="toggle-row">
          <label className="toggle">
            <input
              type="checkbox"
              checked={useRag}
              onChange={(event) => setUseRag(event.target.checked)}
              disabled={isLoading}
            />
            <span>Use RAG</span>
          </label>

          <label className="toggle">
            <input
              type="checkbox"
              checked={useSystemPrompt}
              onChange={(event) => setUseSystemPrompt(event.target.checked)}
              disabled={isLoading}
            />
            <span>Use system prompt</span>
          </label>
        </div>

        <textarea
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Ask for a mood, genre, or type of song"
          rows={4}
          disabled={isLoading}
        />
        <button className="send-button" type="submit" disabled={isLoading || !input.trim()}>
          Send
        </button>
      </form>
    </main>
  );
}
