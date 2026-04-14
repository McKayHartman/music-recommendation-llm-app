import os
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext

import env
from langchain.messages import HumanMessage, SystemMessage
from langchain_litellm import ChatLiteLLM
from system_prompt import SYSTEM_PROMPT_TEMPLATE

from rag import format_recommendations_for_prompt


MODEL_NAME = "litellm_proxy/js2/gpt-oss-120b"
API_BASE = "https://llm-api.cyverse.ai"
RAG_RESULTS = 5
DATASET_LENGTH = None


def normalize_response_text(content: str) -> str:
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                if item.get("type") == "thinking":
                    continue
                text_value = item.get("text") or item.get("content") or ""
                parts.append(text_value)
            else:
                item_type = getattr(item, "type", None)
                if item_type == "thinking":
                    continue
                text_value = getattr(item, "text", None) or getattr(item, "content", None)
                parts.append(text_value if text_value is not None else str(item))
        content = "\n".join(parts)
    elif content is None:
        content = ""
    else:
        content = str(content)

    cleaned = content.replace("\\n", "\n").replace("\r\n", "\n").strip()
    lines = [line.strip() for line in cleaned.split("\n")]
    return "\n".join(line for line in lines if line)


def build_messages(user_query: str):
    rag_context = format_recommendations_for_prompt(
        query=user_query,
        n_results=RAG_RESULTS,
        dataset_length=DATASET_LENGTH,
    )
    return [
        SystemMessage(
            content=SYSTEM_PROMPT_TEMPLATE.format(rag_context=rag_context)
        ),
        HumanMessage(content=user_query),
    ]


class RagChatUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Music Recommendation Chatbot")
        self.root.geometry("900x700")

        api_key = os.environ.get("AIVERDE_API_KEY")
        if not api_key:
            raise RuntimeError("AIVERDE_API_KEY is not set.")

        self.llm = ChatLiteLLM(
            model=MODEL_NAME,
            api_key=api_key,
            api_base=API_BASE,
        )

        self.is_loading = False

        self.chat_history = scrolledtext.ScrolledText(
            root,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=("Helvetica", 12),
        )
        self.chat_history.pack(fill=tk.BOTH, expand=True, padx=16, pady=(16, 8))

        controls = tk.Frame(root)
        controls.pack(fill=tk.X, padx=16, pady=(0, 16))

        self.prompt_input = tk.Text(controls, height=4, font=("Helvetica", 12))
        self.prompt_input.pack(fill=tk.X, side=tk.LEFT, expand=True)
        self.prompt_input.bind("<Control-Return>", self.submit_with_shortcut)

        send_button = tk.Button(
            controls,
            text="Send",
            width=12,
            command=self.on_submit,
        )
        send_button.pack(side=tk.LEFT, padx=(12, 0))

        self.status_label = tk.Label(
            root,
            text="Ready",
            anchor="w",
            font=("Helvetica", 10),
        )
        self.status_label.pack(fill=tk.X, padx=16, pady=(0, 12))

        self.append_message(
            "Assistant",
            "Describe the mood, setting, or kind of song you want, and I’ll use RAG plus AI-VERDE to recommend music.",
        )

    def append_message(self, sender: str, content: str) -> None:
        self.chat_history.configure(state=tk.NORMAL)
        self.chat_history.insert(tk.END, f"{sender}:\n{content}\n\n")
        self.chat_history.configure(state=tk.DISABLED)
        self.chat_history.see(tk.END)

    def set_loading(self, is_loading: bool, status_text: str) -> None:
        self.is_loading = is_loading
        self.status_label.config(text=status_text)

    def submit_with_shortcut(self, event):
        self.on_submit()
        return "break"

    def on_submit(self) -> None:
        if self.is_loading:
            return

        user_query = self.prompt_input.get("1.0", tk.END).strip()
        if not user_query:
            return

        self.prompt_input.delete("1.0", tk.END)
        self.append_message("You", user_query)
        self.set_loading(True, "Retrieving music context and querying AI-VERDE...")

        worker = threading.Thread(target=self.fetch_response, args=(user_query,), daemon=True)
        worker.start()

    def fetch_response(self, user_query: str) -> None:
        try:
            response = self.llm.invoke(build_messages(user_query))
            self.root.after(0, self.finish_response, response.content)
        except Exception as exc:
            self.root.after(0, self.handle_error, str(exc))

    def finish_response(self, content: str) -> None:
        self.append_message("Assistant", normalize_response_text(content))
        self.set_loading(False, "Ready")

    def handle_error(self, error_message: str) -> None:
        self.set_loading(False, "Error")
        messagebox.showerror("Chatbot Error", error_message)


def main() -> None:
    root = tk.Tk()
    app = RagChatUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
