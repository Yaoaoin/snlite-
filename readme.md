````md

\# SNLite



\*\*SNLite\*\* is a lightweight, local-first GenAI chat framework with a browser UI.

It runs on `localhost`, lets you load local models (via \*\*Ollama\*\*), and chat with streaming output, thinking trace (for supported models), image input, and file attachments.



\- ✅ Local only (no cloud by default)

\- ✅ Browser UI (localhost)

\- ✅ Streaming chat

\- ✅ Ollama native thinking support (`message.thinking`)

\- ✅ Image input (multimodal models)

\- ✅ File attachments (PDF / DOCX / TXT / MD) → extracted text injected into the prompt

\- ✅ Sessions + auto chat title



---



\## Quick Start



\### 1) Requirements



\- \*\*Python 3.10+\*\*

\- \*\*Ollama installed and running\*\*

&nbsp; - Install: https://ollama.com

&nbsp; - Verify:

&nbsp;   ```bash

&nbsp;   ollama --version

&nbsp;   ollama list

&nbsp;   ```



\### 2) Install SNLite



\#### Option A (recommended): editable install from source

```bash

git clone https://github.com/AyUkI-AYANO/snlite

cd snlite

pip install -e .

````



\#### Option B: install dependencies only (if you don’t want `-e`)



```bash

pip install .

```



\### 3) Run



```bash

snlite

```



Open in browser:



\* `http://127.0.0.1:8000`



> You can change host/port via env:

>

> \* `SNLITE\_HOST` (default: `127.0.0.1`)

> \* `SNLITE\_PORT` (default: `8000`)

> \* `OLLAMA\_BASE\_URL` (default: `http://127.0.0.1:11434`)

>

> Example:

>

> ```bash

> set SNLITE\_PORT=8010

> snlite

> ```



---



\## How to Use



\### Load a model



1\. Make sure Ollama is running

2\. In SNLite sidebar:



&nbsp;  \* Choose provider: `ollama`

&nbsp;  \* Select model from the list

&nbsp;  \* Click \*\*Load\*\*



If the model list is empty:



```bash

ollama list

```



If you don’t have models:



```bash

ollama pull qwen3

```



---



\## Streaming Chat



\* Messages stream token-by-token.

\* UI supports \*\*auto-scroll during generation\*\* (can be toggled).

\* If you scroll up manually, auto-scroll pauses automatically so it won’t “fight” your mouse wheel.



---



\## Thinking Trace (Ollama Native)



Some Ollama models emit a separate reasoning trace via:



\* `message.thinking` (trace)

\* `message.content` (final answer)



Supported thinking models (examples):



\* Qwen 3

\* DeepSeek R1 / v3.1

\* GPT-OSS (uses `think` levels `low/medium/high`)



\### In SNLite



\* \*\*Think mode\*\*:



&nbsp; \* `auto` = do not force `think`, use model defaults

&nbsp; \* `on/off` = boolean for most thinking models

&nbsp; \* `low/medium/high` = GPT-OSS only



\* \*\*Show trace in workspace\*\*:



&nbsp; \* Displays streaming thinking tokens in the \*\*right-side workspace\*\*

&nbsp; \* Does NOT store trace to session history



> Note: If your model does not support thinking fields, you won’t see trace output.



---



\## Image Input (Multimodal)



\* Click \*\*Attach Image\*\*

\* Choose an image file (<= 6MB)

\* Send message



✅ Works only if the model supports images (multimodal), e.g. LLaVA / Qwen-VL variants.



If you attach an image but get bad results:



\* You likely loaded a text-only model.



---



\## File Attachments (PDF / DOCX / TXT / MD)



SNLite v0.5.0 supports attaching documents to a message.



\### How it works



\* You attach files (up to \*\*3 files\*\*, each <= \*\*6MB\*\*)

\* Server extracts text:



&nbsp; \* PDF: first up to 20 pages (text PDFs only; scanned PDFs may extract nothing)

&nbsp; \* DOCX: paragraphs (truncated)

&nbsp; \* TXT/MD: decoded as plain text

\* Extracted text is injected into the \*\*current\*\* user message as a quoted excerpt:



&nbsp; \* `> \[File: xxx.pdf] ...`



\### Privacy / storage behavior



\* SNLite does \*\*NOT\*\* store raw file binaries/base64 in session history

\* Session history saves only:



&nbsp; \* file name

&nbsp; \* short excerpt marker (for reference)



\### Limitations



\* Scanned-image PDFs usually require OCR; v0.5.0 does not include OCR (to stay lightweight).

\* Large or complex PDFs may have incomplete extraction.



---



\## Sessions \& Auto Titles



\* Each chat is a session.

\* After the first user message, SNLite can auto-generate a short title:



&nbsp; \* If a model is loaded: it asks the model to generate a title

&nbsp; \* Otherwise: it falls back to the first user message snippet



---



\## Export



\* You can export a session as Markdown:



&nbsp; \* \*\*Export .md\*\* button

\* The export contains the conversation messages.



---



\## Troubleshooting



\### Model list is empty



\* Ensure Ollama is running:



&nbsp; ```bash

&nbsp; ollama list

&nbsp; ```

\* Ensure `OLLAMA\_BASE\_URL` is correct (default `http://127.0.0.1:11434`)



\### Thinking trace not showing



\* The model may not support thinking fields.

\* Try thinking-capable models like `qwen3` or `deepseek-r1`.

\* For GPT-OSS: use `low/medium/high` (boolean `true/false` is ignored).



\### PDF file extracts nothing



\* Likely a scanned PDF (image-only).

\* v0.5.0 does not ship OCR to keep it lightweight.



\### Auto-scroll annoys me



\* Toggle \*\*Auto-scroll during streaming\*\* in UI sidebar.

\* Auto-scroll pauses automatically when you manually scroll up.



---



\## Project Structure



Typical layout:



```

snlite/

├─ snlite/

│  ├─ main.py

│  ├─ web/

│  │  ├─ index.html

│  │  ├─ style.css

│  │  └─ app.js

│  ├─ providers/

│  │  └─ ollama.py

│  ├─ store.py

│  └─ registry.py

├─ pyproject.toml

└─ README.md

```



---



\## License



Recommended: MIT (add `LICENSE` if you plan to share / fork / release).

If you haven’t added one yet, do it before sharing publicly.



---



\# CHANGELOG



\## v0.5.0 (current)



\### Added



\* Auto-scroll during streaming (pauses when user scrolls up)

\* Strongly differentiated chat bubbles for User vs Assistant



&nbsp; \* left/right alignment, avatars, role chips, clearer visual separation

\* File attachments in chat (PDF / DOCX / TXT / MD)



&nbsp; \* text extraction on server

&nbsp; \* injected excerpts into the prompt

&nbsp; \* no raw file storage in session history



\### Improved



\* Message rendering stability during long streaming responses

\* UI clarity for reading long content



---



\## v0.4.2



\### Fixed



\* Markdown rendering issues (bold/italics/code blocks)

\* Better safe HTML escaping to prevent broken styling



---



\## v0.4.1



\### Added / Changed



\* Reworked “Deep thinking” display using \*\*Ollama native thinking fields\*\*



&nbsp; \* Supports `message.thinking` vs `message.content`

\* Thinking trace displayed in a dedicated right-side workspace

\* UI toggle to show/hide trace without affecting model behavior



---



\## v0.4.0



\### Added



\* Image input support (for multimodal models)

\* Image attachment preview + one-shot send behavior



---



\## v0.3.0



\### Added



\* Per-setting explanation (tooltips / help hints)

\* Auto chat title generation based on first user message



---



\## v0.2.1



\### Added



\* “Show deep thinking process” UI toggle (early version)



\### Fixed



\* Packaging/install issues (layout / discovery problems)



---



\## v0.2.0



\### Improved



\* UI refinement:



&nbsp; \* better sliders

&nbsp; \* clearer separation between system prompt and chat input



\### Added



\* “Deep thinking” feature (initial concept)



---



\## v0.1.0



\### Initial



\* Minimal local browser UI

\* Load model + chat via localhost

\* Lightweight baseline architecture





