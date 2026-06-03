import { useState, KeyboardEvent } from "react";

interface Props {
  onSend: (text: string) => void;
  disabled: boolean;
}

export default function ChatInput({ onSend, disabled }: Props) {
  const [value, setValue] = useState("");

  function handleSend() {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
  }

  function handleKey(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="px-4 pb-4">
      <div className="flex items-end gap-2 border border-gray-200 rounded-2xl px-4 py-2.5 bg-white shadow-sm focus-within:border-gray-400 transition-colors">
        {/* Attach icon */}
        <button
          disabled={disabled}
          className="text-gray-400 hover:text-gray-600 transition-colors flex-shrink-0 mb-0.5 disabled:opacity-40"
          title="Đính kèm"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
          </svg>
        </button>

        {/* Textarea */}
        <textarea
          rows={1}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKey}
          disabled={disabled}
          placeholder="Hỏi bất cứ điều gì…"
          className="flex-1 resize-none bg-transparent text-sm text-gray-900 placeholder-gray-400 focus:outline-none max-h-36 leading-relaxed"
          style={{ height: "24px" }}
          onInput={(e) => {
            const el = e.currentTarget;
            el.style.height = "24px";
            el.style.height = `${Math.min(el.scrollHeight, 144)}px`;
          }}
        />

        {/* Send button */}
        <button
          onClick={handleSend}
          disabled={disabled || !value.trim()}
          className="w-8 h-8 rounded-xl bg-gray-900 hover:bg-gray-700 disabled:bg-gray-200 text-white flex items-center justify-center transition-colors flex-shrink-0 mb-0.5"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M12 5l7 7-7 7" />
          </svg>
        </button>
      </div>
      <p className="text-center text-xs text-gray-400 mt-2">Enter để gửi · Shift+Enter xuống dòng</p>
    </div>
  );
}
