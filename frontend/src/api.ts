import axios, { AxiosError } from "axios";
import { Message } from "./types";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function sendMessage(messages: Message[]): Promise<string> {
  const payload = messages.map((m) => ({ role: m.role, content: m.content }));

  try {
    const { data } = await axios.post(
      `${API_BASE}/api/chat/`,
      { messages: payload },
      { timeout: 30000 },
    );

    if (!data?.reply) {
      throw new Error("Server trả về phản hồi rỗng");
    }

    return data.reply as string;
  } catch (err) {
    const axiosErr = err as AxiosError;

    if (axiosErr.code === "ERR_NETWORK" || axiosErr.code === "ECONNREFUSED") {
      throw new Error(`Không kết nối được server (${API_BASE}). Hãy kiểm tra backend đã chạy chưa.`);
    }

    if (axiosErr.code === "ECONNABORTED") {
      throw new Error("Server phản hồi quá lâu (timeout 30s). Thử lại sau.");
    }

    if (axiosErr.response) {
      const status = axiosErr.response.status;
      const detail = (axiosErr.response.data as { detail?: string })?.detail ?? axiosErr.message;
      throw new Error(`Lỗi server ${status}: ${detail}`);
    }

    throw err;
  }
}
