import React, { useState } from "react";

export default function Chatbot() {
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([]);
  const [input, setInput] = useState("");

  const sendMessage = async () => {
    if (!input.trim()) return;

    const newMessages = [...messages, { role: "user", content: input }];
    setMessages(newMessages);
    setInput("");

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input }),
      });

      const data = await res.json();

      if (data.reply) {
        setMessages([...newMessages, { role: "assistant", content: data.reply }]);
      }
    } catch (error) {
      console.error("Chatbot error:", error);
    }
  };

  return (
    <div className="flex flex-col w-full max-w-lg mx-auto bg-black border border-white p-4 rounded-lg">
      <h2 className="text-lg font-bold text-white mb-2">RadiaTrade AI Chat</h2>
      <div className="h-64 overflow-y-auto bg-gray-900 p-2 rounded-lg">
        {messages.map((msg, index) => (
          <div key={index} className={`p-2 my-1 rounded ${msg.role === "user" ? "bg-blue-500 text-white" : "bg-gray-700 text-white"}`}>
            {msg.content}
          </div>
        ))}
      </div>
      <div className="flex mt-2">
        <input
          type="text"
          className="flex-grow p-2 rounded bg-gray-700 text-white"
          placeholder="Ask me anything..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button className="ml-2 px-4 py-2 bg-blue-500 text-white rounded border border-white" onClick={sendMessage}>
          Send
        </button>
      </div>
    </div>
  );
}
