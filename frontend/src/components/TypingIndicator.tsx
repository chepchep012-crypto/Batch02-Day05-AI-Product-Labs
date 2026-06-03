export default function TypingIndicator() {
  return (
    <div className="flex gap-3 mb-5 px-4">
      <div className="w-7 h-7 rounded-full bg-gray-900 flex items-center justify-center text-white text-xs flex-shrink-0 mt-0.5">
        ✈
      </div>
      <div className="flex items-center gap-1.5 pt-1.5">
        <div className="typing-dot" />
        <div className="typing-dot" />
        <div className="typing-dot" />
      </div>
    </div>
  );
}
