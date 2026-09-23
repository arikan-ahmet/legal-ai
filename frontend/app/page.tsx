"use client";

import { useEffect, useRef, useState } from "react";

type Message = {
  role: "user" | "assistant";
  content: string;
};

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [conversationId] = useState(() => crypto.randomUUID());

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages]);


  async function handleSend() {
    if (!input.trim()) {
      return;
    }
    setIsLoading(true);
    setError("");
    const message = input;

    const userMessage: Message = {
      role: "user",
      content: message,
    };

    const assistantMessage: Message = {
      role: "assistant",
      content: "",
    };

    setMessages((currentMessages) => [
      ...currentMessages,
      userMessage,
      assistantMessage,
    ]);

    setInput("");
    try{
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          conversation_id: conversationId,
          message: message,
        }),
      });

      if (!response.ok) {
        throw new Error("Backend request failed.");
      }

      if (!response.body) {
        throw new Error("Response body is empty.");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          break;
        }

        const chunk = decoder.decode(value, { stream: true });

        setMessages((currentMessages) => {
          const lastIndex = currentMessages.length - 1;

          return currentMessages.map((message, index) => {
            if (index !== lastIndex || message.role !== "assistant") {
              return message;
            }

            return {
              ...message,
              content: message.content + chunk,
            };
          });
        });
      }
    }catch (error) {
      setMessages((currentMessages) => {
        return currentMessages.slice(0, -1);
      });

      setError("Bir hata oluştu. Lütfen tekrar deneyin.");
    }finally {
    setIsLoading(false);
    }
  }

  
  return (
    <main className="h-screen overflow-hidden bg-gray-100">
      <div className="mx-auto flex h-full max-w-4xl flex-col bg-white shadow-lg">

        <header className="border-b px-6 py-4">
          <h1 className="text-2xl font-bold">Legal AI</h1>
          <p className="text-sm text-gray-500">
            Türkçe Hukuk Asistanı
          </p>
        </header>

        <div className="min-h-0 flex-1 space-y-4 overflow-y-auto p-6">
          {messages.map((message, index) => (
            <div
              key={index}
              className={
                message.role === "user"
                  ? "flex justify-end"
                  : "flex justify-start"
              }
            >
              <div
                className={
                  message.role === "user"
                    ? "max-w-[75%] rounded-2xl bg-blue-600 px-4 py-3 text-white"
                    : "max-w-[75%] rounded-2xl bg-gray-100 px-4 py-3 text-gray-900"
                }
              >
                {message.content}
              </div>
            </div>
          ))}
          {error && (
            <div className="rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="border-t p-4">
          <div className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  handleSend();
                }
              }}
              placeholder="Mesajınızı yazın..."
              className="flex-1 rounded-xl border border-gray-300 px-4 py-3 outline-none focus:border-blue-500"
            />
            <button
              onClick={handleSend}
              disabled={isLoading}
              className="rounded-xl bg-blue-600 px-5 py-3 font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isLoading ? "Yanıtlıyor..." : "Gönder"}
            </button>
          </div>
        </div>

      </div>
    </main>
  );
}