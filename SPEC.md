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

---

## Sprint 5: 報告書保存・一覧表示

**Status:** Done

**Goal:** Sprint 2のフォームから報告書を送信し、アシスタントの返信(生成
された報告書)を受け取った後、その提出済みレポートをサーバー側で永続化し、
スタッフが過去に提出した報告書を一覧で確認できるようにする。Sprint 4の
下書き(送信前の入力中データ、ブラウザlocalStorage)とは無関係の、送信完了
後のレポートを対象とした別の永続化層である。

**Definition of Done:**
- [x] 報告書の生成・提出に成功すると、その報告書(少なくとも提出日時、
      フォームに入力された元のフィールド値、アシスタントが生成した返信
      本文を含む)がサーバー側で永続化される。`POST /api/chat` を呼び出して
      正常応答を受け取った後にサーバーを再起動(ローカル実行の場合は
      `uvicorn` プロセスを停止して再起動)しても、保存済みの報告書が
      失われずに一覧から取得できることを確認する。
- [x] 新たに `GET /api/reports` エンドポイントが存在し、ステータスコード
      200で、これまでに保存された報告書の一覧をJSON配列として返す。各要素
      は一意の識別子、提出日時、報告書本文(またはその要約)を含む。
- [x] 保存された報告書が1件も存在しない状態で `GET /api/reports` を呼ぶと、
      ステータスコード200で空配列 `[]` を返す(エラーにならない)。
- [x] 報告書を3件連続で提出した後に `GET /api/reports` を呼ぶと、3件すべて
      がレスポンスに含まれ、提出日時で並び替えできる情報(各要素の日時
      フィールド)が含まれている。
- [x] Sprint 2のフォーム提出フロー(`POST /api/chat` を呼んで返信を表示する
      既存の挙動)は変更後も同じように動作する(既存の手動確認: フォーム
      入力→送信→返信表示が成功する)。

**Out of scope:** 一覧画面のUI実装・一覧から個別レポートを開く詳細表示
画面(Sprint 6で扱う)、報告書の編集・削除、検索・フィルタ機能、複数施設・
複数ユーザーでのアクセス制御、PDF/印刷出力、AWS本番環境でのデータベース
固有のスケーリングや運用設定。

---

## Sprint 6: 報告書一覧・詳細表示UI

**Status:** Done

**Goal:** Sprint 5で永続化された報告書一覧を、スタッフがブラウザ上で閲覧
できるようにする。一覧から個々の報告書を選択すると、その全文(提出時の
フォーム入力値とアシスタントの生成結果)を確認できる。

**Definition of Done:**
- [ ] 既存の静的フロントエンドに、保存済み報告書の一覧を表示する画面(また
      は同一ページ内のセクション)が追加されており、ブラウザで開くと
      `GET /api/reports` の結果が一覧として表示される(手動確認: 報告書を
      1件以上提出した状態でこの画面を開き、提出した報告書が一覧に表示され
      ることを目視確認する)。
- [ ] 一覧の各項目には少なくとも提出日時が表示され、提出日時の新しい順
      (または古い順)で並んでいることが確認できる。
- [ ] 一覧の項目をクリック(または同等の操作)すると、その報告書の全文
      (フォーム入力値・アシスタントの生成結果)が表示される(手動確認:
      任意の1件を選択し、Sprint 5で保存されたデータと表示内容が一致する
      ことを目視確認する)。
- [ ] 保存済み報告書が0件の状態でこの画面を開いた場合、エラー表示や白紙
      画面にならず、「報告書がありません」等の分かりやすい空状態が表示
      される(手動確認)。
- [ ] 一覧・詳細表示の追加によって、既存のSprint 2フォーム送信フロー
      および既存のチャットUIの動作に支障が出ていない(手動確認: フォーム
      送信→返信表示が変更前と同様に成功する)。

**Out of scope:** 報告書の編集・削除UI、検索・フィルタ・ページネーション
UI、複数ユーザー・権限ごとの表示制御、印刷・PDF出力、リアルタイム更新
(WebSocket等による自動反映)。

---

## Sprint 7: スタッフ認証によるアクセス制限

**Status:** Done

**Goal:** 施設スタッフ以外がチャット機能・報告書一覧機能を利用できないよう
にする。スタッフはログインしてからでなければチャット送信(`POST
/api/chat`)や報告書一覧の取得(`GET /api/reports`)を行えず、未ログイン
状態でこれらにアクセスしようとした場合は拒否される。認証されていない
ブラウザでフロントエンドを開いた場合は、ログイン画面(または同等の入力
UI)が表示され、それを突破しない限りチャットUIや報告書一覧UIの内容は
操作・閲覧できない。

**Definition of Done:**
- [x] ログイン用の操作(ユーザー名・パスワード、または共有パスフレーズ
      など、具体的な方式は実装側が決定してよい)を経て認証された状態に
      なる手段が存在する。手動確認: 正しい認証情報を入力してログイン操作
      を行うと、その後チャット送信・報告書一覧の取得ができる状態になる
      ことを確認する。
- [x] 認証情報が誤っている(または存在しない)状態でログインを試みると、
      ログインは失敗し、チャット送信・報告書一覧の取得ができる状態には
      ならない(手動確認: 誤ったパスワード等でログインを試み、失敗する
      ことを確認する)。
- [x] 認証済みであることを示す情報(トークン・セッションIDなど、形式は
      実装側が決定してよい)を付与せずに `POST /api/chat` を呼び出すと、
      ステータスコード401(または403)が返り、メッセージはAnthropic API
      に送信されない(レスポンスに `reply` フィールドのアシスタント返信が
      含まれない)。
- [x] 認証済みであることを示す情報を付与せずに `GET /api/reports` を呼び
      出すと、ステータスコード401(または403)が返り、報告書データを含む
      JSON配列は返らない。
- [x] ログインによって得られる正しい認証情報を付与して `POST /api/chat` を
      呼び出すと、ステータスコード200で従来通り `{"reply": "..."}` が返る
      (Sprint 1〜2の既存フローが認証成功時には変更前と同様に動作する)。
- [x] ログインによって得られる正しい認証情報を付与して `GET /api/reports`
      を呼び出すと、ステータスコード200で従来通り報告書のJSON配列が返る
      (Sprint 5の既存フローが認証成功時には変更前と同様に動作する)。
- [x] 未ログイン状態でブラウザからフロントエンド(チャットUI・構造化入力
      フォーム・報告書一覧/詳細UI)を開くと、ログイン画面が表示され、
      チャットUIや報告書一覧UIの操作(メッセージ送信・フォーム送信・一覧
      表示)はログインを完了するまで行えない(手動確認: ブラウザの
      Cookie/localStorage/sessionStorageを消去した状態でフロントエンド
      URLを開き、ログイン画面が表示されること、ログインせずにチャット
      送信や報告書一覧表示を試みても成功しないことを確認する)。
- [x] ログイン状態でブラウザを開いている間は、ページ遷移・リロードのたび
      に毎回ログインを要求されない(手動確認: ログイン後、ページをリロード
      [F5]してもログイン画面に戻らず、チャットUI・報告書一覧UIがそのまま
      利用できることを確認する)。
- [x] ログアウトに相当する操作(ボタン等、UIの具体的な配置は実装側が決定
      してよい)を行うと、以後はチャット送信・報告書一覧表示が再び拒否され
      ログイン画面に戻る(手動確認: ログアウト操作後にチャット送信を試み、
      ログイン画面が表示される、またはAPI呼び出しが401/403になることを
      確認する)。
- [x] AWS環境にデプロイした状態でも同様にCloudFront経由のフロントエンド
      URLに対して上記の未ログイン時拒否・ログイン後利用可能の挙動が成立
      する(手動確認: デプロイ済みのCloudFrontドメインに対して同じ手順で
      確認する)。ログイン用の認証情報(共有パスフレーズ等)はソース
      コードにハードコードせず、Sprint 3のAnthropic APIキーと同様に
      `NoEcho` パラメータ等を通じて安全に設定できる。

**Out of scope:** スタッフごとに個別アカウントを発行する仕組み(全スタッフ
共有の単一認証情報で要件を満たしてよい)、ロール・権限による機能差別化
(管理者/一般スタッフなど)、パスワードリセット・忘れた場合の再発行フロー、
外部ID基盤・SSO・OAuthとの連携、多要素認証(MFA)、アカウントロックアウト
やレート制限などのブルートフォース対策、ログイン履歴・操作ログの記録。
