import { useState, useCallback, useRef } from "react";
import { Conversation, Message } from "./types";
import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";
import { sendMessage } from "./api";

function newConversation(): Conversation {
  return {
    id: Math.random().toString(36).slice(2),
    title: "Cuộc hội thoại mới",
    messages: [],
    createdAt: new Date(),
  };
}

function makeId() {
  return Math.random().toString(36).slice(2) + Date.now();
}

export default function App() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Ref luôn giữ giá trị mới nhất của activeId — tránh stale closure trong handleSend
  const activeIdRef = useRef<string | null>(null);
  activeIdRef.current = activeId;

  // Ref giữ conversations mới nhất để lấy history chính xác
  const conversationsRef = useRef<Conversation[]>([]);
  conversationsRef.current = conversations;

  const activeConv = conversations.find((c) => c.id === activeId) ?? null;

  function handleNew() {
    // Nếu conversation hiện tại chưa có tin nhắn nào thì không tạo thêm
    if (activeConv && activeConv.messages.length === 0) return;
    const c = newConversation();
    setConversations((prev) => [c, ...prev]);
    setActiveId(c.id);
  }

  const handleSend = useCallback(
    async (text: string) => {
      // Dùng ref để luôn có activeId mới nhất, tránh tạo conversation thừa
      let convId = activeIdRef.current;

      // Auto-create conversation if none active
      if (!convId) {
        const c = newConversation();
        convId = c.id;
        activeIdRef.current = convId; // cập nhật ref ngay lập tức
        setConversations((prev) => [c, ...prev]);
        setActiveId(convId);
      }

      const userMsg: Message = {
        id: makeId(),
        role: "user",
        content: text,
        timestamp: new Date(),
      };

      setConversations((prev) =>
        prev.map((c) => {
          if (c.id !== convId) return c;
          const updated = { ...c, messages: [...c.messages, userMsg] };
          if (c.title === "Cuộc hội thoại mới") {
            updated.title = text.slice(0, 30) + (text.length > 30 ? "…" : "");
          }
          return updated;
        })
      );

      setLoading(true);

      try {
        // Dùng conversationsRef để lấy history mới nhất, không bị stale
        const currentConv = conversationsRef.current.find((c) => c.id === convId);
        const history = [...(currentConv?.messages ?? []), userMsg];
        const reply = await sendMessage(history);

        const botMsg: Message = {
          id: makeId(),
          role: "assistant",
          content: reply,
          timestamp: new Date(),
        };

        setConversations((prev) =>
          prev.map((c) =>
            c.id === convId ? { ...c, messages: [...c.messages, botMsg] } : c
          )
        );
      } catch (err) {
        const message = err instanceof Error
          ? err.message
          : "Đã xảy ra lỗi không xác định.";
        const errMsg: Message = {
          id: makeId(),
          role: "assistant",
          content: `⚠️ **Lỗi:** ${message}`,
          timestamp: new Date(),
        };
        setConversations((prev) =>
          prev.map((c) =>
            c.id === convId ? { ...c, messages: [...c.messages, errMsg] } : c
          )
        );
      } finally {
        setLoading(false);
      }
    },
    [] // không cần deps vì dùng ref
  );

  return (
    <div className="flex flex-col h-screen bg-white overflow-hidden">

      {/* ── Drawer overlay ── */}
      {sidebarOpen && (
        <div className="drawer-overlay" onClick={() => setSidebarOpen(false)} />
      )}

      {/* ── Slide-out conversation drawer ── */}
      {sidebarOpen && (
        <div className="drawer">
          <Sidebar
            conversations={conversations}
            activeId={activeId}
            onSelect={(id) => { setActiveId(id); setSidebarOpen(false); }}
            onNew={() => { handleNew(); setSidebarOpen(false); }}
          />
        </div>
      )}

      {/* ── Top navbar ── */}
      <header className="flex items-center justify-between px-4 py-3 border-b border-gray-100 bg-white flex-shrink-0">
        {/* Left: hamburger + logo */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setSidebarOpen(true)}
            className="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 transition-colors"
            title="Lịch sử hội thoại"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M4 6h16M4 12h16M4 18h7" />
            </svg>
          </button>
          <span className="font-semibold text-gray-900 text-base tracking-tight">
            ✈️ TravelBot
          </span>
        </div>

        {/* Right: new chat */}
        <button
          onClick={handleNew}
          className="w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 transition-colors"
          title="Cuộc hội thoại mới"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M12 4v16m8-8H4" />
          </svg>
        </button>
      </header>

      {/* ── Chat area ── */}
      <div className="flex-1 overflow-hidden">
        <ChatWindow
          messages={activeConv?.messages ?? []}
          loading={loading}
          onSend={handleSend}
        />
      </div>
    </div>
  );
}
