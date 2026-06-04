import { useEffect, useRef } from "react";
import { Message } from "../types";
import MessageBubble from "./MessageBubble";
import TypingIndicator from "./TypingIndicator";
import ChatInput from "./ChatInput";

interface Props {
  messages: Message[];
  loading: boolean;
  onSend: (text: string) => void;
}

const SUGGESTIONS = [
  { label: "🗺️ Lên lịch Vinpearl",           prompt: "Tôi muốn lên lịch trình Vinpearl" },
  { label: "🏨 Tư vấn chọn khu phòng",        prompt: "Tư vấn chọn khu phòng Vinpearl phù hợp cho tôi" },
  { label: "🎁 Ưu đãi Vinpearl hiện tại",     prompt: "Vinpearl có ưu đãi gì đang áp dụng không?" },
  { label: "📍 Các điểm đến Vinpearl",        prompt: "Vinpearl có những điểm đến nào?" },
];

export default function ChatWindow({ messages, loading, onSend }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const isEmpty = messages.length === 0;

  return (
    <div className="flex flex-col h-full">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto py-6">
        {isEmpty ? (
          /* Welcome screen */
          <div className="max-w-3xl mx-auto px-4">
            <div className="flex gap-3 mb-5">
              <div className="w-7 h-7 rounded-full bg-green-700 flex items-center justify-center text-white text-xs flex-shrink-0 mt-0.5">
                🌴
              </div>
              <div className="text-sm text-gray-800 leading-relaxed">
                <p>Xin chào! Tôi là <strong>VinBot</strong> — trợ lý AI lên lịch Vinpearl. 🌴</p>
                <p className="mt-1 text-gray-500">Tôi hỗ trợ lập lịch trình tại 5 điểm đến Vinpearl: Phú Quốc, Nha Trang, Nam Hội An, Cửa Hội và Hải Phòng.</p>
              </div>
            </div>

            {/* Suggestion chips */}
            <div className="ml-10 flex flex-col gap-2">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s.label}
                  onClick={() => onSend(s.prompt)}
                  disabled={loading}
                  className="text-left text-sm text-gray-700 border border-gray-200 rounded-xl px-4 py-2.5 hover:bg-gray-50 hover:border-gray-300 transition-colors disabled:opacity-40"
                >
                  {s.label}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="max-w-3xl mx-auto">
            {messages.map((m) => <MessageBubble key={m.id} message={m} />)}
            {loading && <TypingIndicator />}
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="max-w-3xl mx-auto w-full pb-2">
        <ChatInput onSend={onSend} disabled={loading} />
      </div>
    </div>
  );
}
