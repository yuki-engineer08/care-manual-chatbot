# SPEC.md

Sprint-by-sprint specification for care-manual-chatbot, a care-facility staff
chatbot for generating incident reports.

Fixed technology stack (not open for reconsideration in future sprints):
Python, FastAPI, Anthropic Claude API (Haiku model), AWS SAM, Lambda,
API Gateway, S3, CloudFront.

Each sprint below records WHAT was/should be built and its Definition of
Done. Implementation details belong in the code and commit history, not
here.

---

## Sprint 0: CLI chatbot

**Status:** Done

**Goal:** A staff member can have a conversational session in the terminal
with a care-practice assistant persona, with conversation history kept for
the session.

**Definition of Done:**
- [x] `python src/chat.py` starts an interactive session and accepts
      Japanese text input/output correctly on a Windows console (no mojibake).
- [x] The assistant's responses follow a care-practice assistant persona
      defined once and shared with any other entry point.
- [x] Conversation history persists across multiple turns within the same
      CLI session.

**Out of scope:** Web UI, persistence across CLI restarts, deployment.

---

## Sprint 1: FastAPI web-ification

**Status:** Done

**Goal:** The same assistant is reachable over HTTP so a browser-based UI
can be built on top of it, without duplicating the persona/model logic.

**Definition of Done:**
- [x] `POST /api/chat` accepts `{"messages": [{"role", "content"}, ...]}`
      and returns `{"reply": "..."}` reflecting the shared persona/model.
- [x] The persona and model configuration live in one shared module
      imported by both the CLI and the web API (no duplication).
- [x] Server is stateless: the same conversation history sent twice
      produces consistent behavior without server-side session storage.
- [x] A minimal static frontend is served from the same app and can send a
      message and display a reply end-to-end in a browser.

**Out of scope:** Structured incident-report input, authentication, AWS
deployment.

---

## Sprint 2: Structured incident-report input form

**Status:** Done

**Goal:** Staff can fill in a structured form (discovery time, location,
post-incident response, free-text notes, etc.) instead of free-typing the
incident report context, and submit it to generate a report via the
existing chat pipeline.

**Definition of Done:**
- [x] The web UI presents labeled fields for the incident-report context
      (time, place, after-response, supplementary notes, and other relevant
      fields) instead of requiring the user to type unstructured prose.
- [x] Submitting the form assembles the field values into a single message
      sent through the existing `POST /api/chat` flow and displays the
      assistant's reply.
- [x] Required structural sections (e.g. "事故発見時の状況") are clearly
      labeled in the generated message sent to the assistant.

**Out of scope:** Saving submitted reports, multi-incident history, PDF/
print export.

---

## Sprint 3: AWS SAM deployment

**Status:** Done

**Goal:** The chatbot runs in AWS so staff can reach it without anyone
running a local server: API on Lambda/API Gateway, static frontend on
S3/CloudFront, with the Anthropic API key supplied securely.

**Definition of Done:**
- [x] `template.yaml` defines a Lambda function (`lambda_handler.handler`)
      behind an API Gateway HTTP API that proxies `/api/*` requests.
- [x] The Anthropic API key is passed as a `NoEcho` SAM parameter and
      injected into the Lambda as an environment variable (not hardcoded).
- [x] A private S3 bucket serves the static frontend, reachable only via
      CloudFront (Origin Access Control; public access blocked on the
      bucket).
- [x] CloudFront routes `/api/*` to the API Gateway origin (cache disabled)
      and all other paths to the S3 frontend origin (cache enabled), over
      a single distribution/domain.
- [x] Stack outputs include the API base URL, the frontend bucket name,
      and the CloudFront distribution ID/domain needed for deploys.

**Out of scope:** Custom domain/ACM certificate, CI/CD pipeline, WAF/rate
limiting, multi-environment (staging/prod) stacks.

---

## Sprint 4: localStorage下書き保存

**Status:** Done

**Goal:** 事故報告書の構造化入力フォームに入力中、タブを閉じたりリロードし
たりしても入力内容が消えないようにする。入力はブラウザのlocalStorageに自動
保存され、報告書の送信が完了した時点で下書きはクリアされる。

**Definition of Done:**
- [x] フォームのいずれかのフィールド(時刻・場所・対応・補足など)に文字を
      入力すると、ページをリロードせずブラウザの開発者ツールで
      `localStorage` を確認した時点でその値が保存されていることが確認できる。
- [x] フォームに値を入力した状態でページをリロード(F5)すると、リロード後
      に各フィールドへ入力していた値がすべて復元されている(手動確認:
      時刻・場所・対応・補足の4項目以上に値を入れてリロードし、全項目が
      復元されることを目視確認する)。
- [x] 何も入力していない状態でページを開いた場合、フォームは空のまま表示
      される(過去の下書きが残っていないユーザーには何も復元されない)。
- [x] フォームを送信して `POST /api/chat` への送信が成功し、アシスタントの
      返信が表示された後、ページをリロードするとフォームは空に戻っている
      (下書きがクリアされたことの確認)。送信が失敗した場合は下書きは
      クリアされず、入力内容が残っていることも確認する。
- [x] 入力中の保存処理によって入力のタイピングが目に見えて重くなったり
      入力がカクついたりしない(手動確認: 任意のテキストフィールドに
      文章を連続して入力し、入力のラグを感じないことを目視確認する)。

**Out of scope:** 複数下書きの保存・履歴管理、サーバー側への下書き保存、
ブラウザ・デバイスをまたいだ下書きの同期、フォーム送信失敗時の自動リトライ。
