import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
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

      {/* Bot message */}
      <div className="flex-1 min-w-0 overflow-x-auto">
        <div className="text-sm text-gray-800 leading-relaxed markdown-body">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              table: ({ children }) => (
                <div className="overflow-x-auto my-3">
                  <table className="min-w-full border-collapse text-xs">{children}</table>
                </div>
              ),
              thead: ({ children }) => (
                <thead className="bg-gray-100 text-gray-700">{children}</thead>
              ),
              tbody: ({ children }) => <tbody>{children}</tbody>,
              tr: ({ children }) => (
                <tr className="border-b border-gray-200 hover:bg-gray-50">{children}</tr>
              ),
              th: ({ children }) => (
                <th className="px-3 py-2 text-left font-semibold whitespace-nowrap border border-gray-200">{children}</th>
              ),
              td: ({ children }) => (
                <td className="px-3 py-1.5 border border-gray-200 align-top">{children}</td>
              ),
              h2: ({ children }) => (
                <h2 className="text-base font-bold text-green-800 mt-4 mb-2">{children}</h2>
              ),
              h3: ({ children }) => (
                <h3 className="text-sm font-semibold text-gray-700 mt-3 mb-1">{children}</h3>
              ),
              hr: () => <hr className="my-3 border-gray-200" />,
              blockquote: ({ children }) => (
                <blockquote className="border-l-4 border-green-300 pl-3 text-gray-500 italic my-2">{children}</blockquote>
              ),
              code: ({ children }) => (
                <code className="bg-gray-100 text-green-700 rounded px-1 py-0.5 font-mono text-xs">{children}</code>
              ),
              a: ({ href, children }) => (
                <a href={href} target="_blank" rel="noopener noreferrer" className="text-green-700 underline hover:text-green-900">{children}</a>
              ),
            }}
          >
            {message.content}
          </ReactMarkdown>
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
