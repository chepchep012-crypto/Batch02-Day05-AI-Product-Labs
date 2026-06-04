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
  { label: "🗺️ Lên lịch 2N1Đ Vinpearl",    prompt: "Giúp tôi lên lịch trình 2 ngày 1 đêm Vinpearl Phú Quốc" },
  { label: "🎢 VinWonders hay Safari trước?", prompt: "Nên đi VinWonders hay Vinpearl Safari trước trong 2N1Đ?" },
  { label: "🏨 Chọn khu phòng Vinpearl",     prompt: "Tư vấn chọn khu phòng Vinpearl Phú Quốc cho gia đình" },
  { label: "🎁 Ưu đãi Vinpearl hiện tại",    prompt: "Vinpearl Phú Quốc có ưu đãi gì đang áp dụng không?" },
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
          <div className="max-w-xl mx-auto px-4">
            <div className="flex gap-3 mb-5">
              <div className="w-7 h-7 rounded-full bg-green-700 flex items-center justify-center text-white text-xs flex-shrink-0 mt-0.5">
                🌴
              </div>
              <div className="text-sm text-gray-800 leading-relaxed">
                <p>Xin chào! Tôi là <strong>VinBot</strong> — trợ lý AI lên lịch Vinpearl Phú Quốc. 🌴</p>
                <p className="mt-1 text-gray-500">Tôi sẽ hỏi bạn 3 câu ngắn, rồi đề xuất lịch trình 2N1Đ, khu phòng và ưu đãi thật phù hợp nhất!</p>
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
          <div className="max-w-xl mx-auto">
            {messages.map((m) => <MessageBubble key={m.id} message={m} />)}
            {loading && <TypingIndicator />}
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="max-w-xl mx-auto w-full pb-2">
        <ChatInput onSend={onSend} disabled={loading} />
      </div>
    </div>
  );
}
