'use client';

import { useChat } from '@ai-sdk/react';
import { useEffect, useRef, useState } from 'react';
import Link from 'next/link';

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [mounted, setMounted] = useState(false);
  const messagesEndRef = useRef(null);

  const { messages, input, setInput, sendMessage, status } = useChat({
    api: '/api/chat',
    initialMessages: [
      {
        id: 'welcome-1',
        role: 'assistant',
        content: 'Hi! I\'m your AI Tool Expert. Ask me anything about finding the perfect AI tool for your needs. For example: "What\'s the best tool for content writers?" or "I need real-time search capabilities".',
      },
    ],
  });

  const isLoading = status === 'streaming' || status === 'submitted';

  // Hydration fix
  useEffect(() => {
    setMounted(true);
  }, []);

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (!mounted) return null;

  return (
    <>
      {/* Floating Chat Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 z-40 bg-accent hover:bg-accent-hover text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-200 p-4 w-14 h-14 flex items-center justify-center text-2xl"
          aria-label="Open AI Tool Expert Chat"
          title="Ask about AI tools"
        >
          💬
        </button>
      )}

      {/* Chat Modal */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 z-50 w-96 max-w-[calc(100vw-32px)] bg-dark-surface border border-dark-border rounded-2xl shadow-2xl flex flex-col h-[600px] max-h-[80vh] animate-scale-in">
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-dark-border bg-gradient-to-r from-accent/10 to-transparent">
            <div>
              <h3 className="font-semibold text-dt text-lg">AI Tool Expert</h3>
              <p className="text-sm text-dt-muted">Powered by Claude</p>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-dt-muted hover:text-dt transition-colors p-2 hover:bg-dark-border rounded-lg"
              aria-label="Close chat"
            >
              ✕
            </button>
          </div>

          {/* Affiliate Disclosure */}
          <div className="px-6 py-2 bg-accent/5 border-b border-dark-border text-xs text-dt-muted">
            <p>
              💡 We earn affiliate commissions from some tool links.{' '}
              <Link href="/affiliate-disclosure/" className="text-accent hover:underline">
                Learn more
              </Link>
            </p>
          </div>

          {/* Messages Container */}
          <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] px-4 py-2 rounded-lg ${
                    message.role === 'user'
                      ? 'bg-accent text-white rounded-br-none'
                      : 'bg-dark-border text-dt rounded-bl-none'
                  }`}
                >
                  {/* Render message parts (text and other content types) */}
                  {Array.isArray(message.parts) ? (
                    message.parts.map((part, idx) => {
                      if (part.type === 'text') {
                        return (
                          <div key={idx} className="whitespace-pre-wrap">
                            {part.text}
                          </div>
                        );
                      }
                      return null;
                    })
                  ) : (
                    // Fallback for older message format
                    <div className="whitespace-pre-wrap">{message.content}</div>
                  )}
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-dark-border text-dt px-4 py-2 rounded-lg rounded-bl-none">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-dt-muted rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-dt-muted rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-dt-muted rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Form */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (input.trim()) {
                sendMessage({ text: input });
                setInput('');
              }
            }}
            className="border-t border-dark-border p-4 bg-dark-surface/50"
          >
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about AI tools..."
                className="flex-1 px-4 py-2 bg-dark-border text-dt rounded-lg border border-dark-border/50 focus:border-accent focus:outline-none transition-colors placeholder-dt-muted"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={isLoading || !input.trim()}
                className="px-4 py-2 bg-accent hover:bg-accent-hover text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                Send
              </button>
            </div>
          </form>
        </div>
      )}
    </>
  );
}

// Parse and render message content with tool links
function MessageContent({ content }) {
  // Simple regex to find tool names and convert them to links
  // This is a basic implementation; Claude will naturally mention tools by name
  const toolNames = [
    'ChatGPT', 'Claude', 'Jasper', 'Midjourney', 'Cursor', 'Writesonic',
    'Copy.ai', 'Synthesia', 'Grammarly', 'Notion AI', 'ElevenLabs', 'Canva',
    'Descript', 'Runway', 'Perplexity', 'Gemini', 'Cohere', 'Pika',
    'Gamma', 'Adobe Firefly'
  ];

  let enrichedContent = content;

  // Simple approach: let Claude naturally mention tools, then we display as-is
  // The affiliate links are handled on the backend if needed
  // For now, just display the conversational response

  return (
    <div className="prose prose-invert max-w-none prose-sm">
      <p className="whitespace-pre-wrap">{enrichedContent}</p>
    </div>
  );
}
