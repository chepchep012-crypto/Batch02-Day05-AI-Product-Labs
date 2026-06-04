import ReactMarkdown from "react-markdown";
import { useState } from "react";
import { Message } from "../types";

interface Props {
  message: Message;
}

export default function MessageBubble({ message }: Props) {
  const isUser = message.role === "user";
  const [copied, setCopied] = useState(false);

  function handleCopy() {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  if (isUser) {
    return (
      <div className="flex justify-end mb-4 px-4">
        <div className="max-w-[70%] bg-gray-100 text-gray-900 rounded-2xl rounded-br-sm px-4 py-2.5 text-sm leading-relaxed">
          <p className="whitespace-pre-wrap">{message.content}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex gap-3 mb-5 px-4 group">
      {/* Bot avatar */}
      <div className="w-7 h-7 rounded-full bg-green-700 flex items-center justify-center text-white text-xs flex-shrink-0 mt-0.5">
        🌴
      </div>

      {/* Bot message — plain text, no bubble */}
      <div className="flex-1 min-w-0">
        <div className="text-sm text-gray-800 leading-relaxed prose-chat">
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>
        {/* Copy button — hiện khi hover */}
        <button
          onClick={handleCopy}
          className="mt-1.5 flex items-center gap-1 text-xs text-gray-400 hover:text-gray-600 transition-colors opacity-0 group-hover:opacity-100"
        >
          {copied ? (
            <>
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Đã sao chép
            </>
          ) : (
            <>
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              Sao chép
            </>
          )}
        </button>
      </div>
    </div>
  );
}
