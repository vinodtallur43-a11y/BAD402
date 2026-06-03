"""
Academic Helper Bot
-------------------
An intelligent agent that accepts academic queries via a Tkinter
search box and returns responses from a locally-hosted Phi-3 Mini
LLM served by Ollama over the LAN.

Course : BAD402 - Artificial Intelligence (VTU)
Program: 10 - Build a bot which provides all the information
             related to text in search box
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import requests
import threading

# ---------------------------------------------------------------
# Configuration - update SERVER_IP to match your lab's host machine
# ---------------------------------------------------------------
SERVER_IP   = "172.27.80.1"          # <-- change to your server's IP
SERVER_PORT = 11434
MODEL_NAME  = "phi3:mini"
API_URL     = f"http://{SERVER_IP}:{SERVER_PORT}/api/generate"
TIMEOUT_SEC = 60


# ---------------------------------------------------------------
# Step 5: Prompt construction (light NLP pre-processing)
# ---------------------------------------------------------------
def build_prompt(query: str) -> str:
    """Wrap the user query in a domain-restricting instruction."""
    return (
        "You are an academic helper bot for engineering students. "
        "Answer the following query concisely and clearly. "
        "If the query is not academic in nature, politely decline.\n\n"
        f"Query: {query}"
    )


# ---------------------------------------------------------------
# Steps 6-8: Send query to LLM and handle the response
# ---------------------------------------------------------------
def query_llm(prompt: str) -> str:
    """Send the prompt to the Ollama server and return the response text."""
    payload = {
        "model":  MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(API_URL, json=payload, timeout=TIMEOUT_SEC)
        if response.status_code == 200:
            return response.json().get("response", "").strip()
        else:
            return f"[Server Error {response.status_code}] Please try again."
    except requests.exceptions.Timeout:
        return "[Error] The server took too long to respond."
    except requests.exceptions.ConnectionError:
        return "[Error] Unable to reach the LLM server. Check the connection."
    except Exception as e:
        return f"[Error] Unexpected: {e}"


# ---------------------------------------------------------------
# Step 4 & 8: Handle the Search-button click
# ---------------------------------------------------------------
def on_search():
    query = entry.get().strip()
    if not query:
        messagebox.showwarning("Empty Query", "Please enter a valid query.")
        return

    # Disable the button and show a "thinking" message while waiting
    search_btn.config(state=tk.DISABLED, text="Thinking...")
    output.config(state=tk.NORMAL)
    output.delete("1.0", tk.END)
    output.insert(tk.END, "Contacting the LLM server, please wait...\n")
    output.config(state=tk.DISABLED)

    # Run the network call in a background thread so the GUI stays responsive
    def worker():
        prompt = build_prompt(query)
        answer = query_llm(prompt)

        # Update the GUI from the main thread
        output.config(state=tk.NORMAL)
        output.delete("1.0", tk.END)
        output.insert(tk.END, answer)
        output.config(state=tk.DISABLED)
        search_btn.config(state=tk.NORMAL, text="Search")

    threading.Thread(target=worker, daemon=True).start()


# ---------------------------------------------------------------
# Step 2: Initialise the Tkinter GUI
# ---------------------------------------------------------------
root = tk.Tk()
root.title("Academic Helper Bot - BAD402")
root.geometry("700x500")
root.configure(bg="#f0f4f8")

# Title label
title = tk.Label(
    root,
    text="Academic Helper Bot",
    font=("Helvetica", 18, "bold"),
    bg="#f0f4f8",
    fg="#1f3a5f"
)
title.pack(pady=10)

# Search-box frame
frame = tk.Frame(root, bg="#f0f4f8")
frame.pack(pady=5, padx=10, fill=tk.X)

entry = tk.Entry(frame, font=("Helvetica", 12))
entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=6)
entry.bind("<Return>", lambda event: on_search())

search_btn = tk.Button(
    frame,
    text="Search",
    font=("Helvetica", 11, "bold"),
    bg="#1f3a5f",
    fg="white",
    command=on_search,
    width=10
)
search_btn.pack(side=tk.RIGHT)

# Output area
output = scrolledtext.ScrolledText(
    root,
    wrap=tk.WORD,
    font=("Consolas", 11),
    state=tk.DISABLED,
    bg="white",
    fg="#222"
)
output.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

# Step 3 & 9: Enter the GUI event loop
root.mainloop()