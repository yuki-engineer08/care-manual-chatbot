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

---

## Sprint 8: 施設形態・転倒リスク別システムプロンプト切り替え（バックエンド）

**Status:** Done

**Goal:** `POST /api/chat` に施設形態と転倒リスクレベルを指定することで、
その組み合わせに最適化されたシステムプロンプトがアシスタントに適用される
ようにする。既存の（パラメータなし）リクエストは引き続き動作する。

**Definition of Done:**
- [ ] `POST /api/chat` のリクエストボディに省略可能なフィールド
      `facility_type`（文字列）と `fall_risk`（文字列）が追加されており、
      認証済みトークンを付与した上で
      `{"messages": [{"role": "user", "content": "テスト"}], "facility_type": "グループホーム", "fall_risk": "小"}`
      を送ると、ステータスコード200と `{"reply": "..."}` が返る。
- [ ] `facility_type` に受け付ける値は以下の5種別のみである。
      「グループホーム」「特別養護老人ホーム」「介護老人保健施設」
      「デイサービス」「自宅」。上記以外の文字列（例: `"病院"`）を指定して
      `POST /api/chat` を呼び出すと、ステータスコード422が返り `reply`
      フィールドは含まれない。
- [ ] `fall_risk` に受け付ける値は以下の3段階のみである。「小」「中」「高」。
      上記以外の文字列（例: `"最大"`）を指定して `POST /api/chat` を呼び
      出すと、ステータスコード422が返り `reply` フィールドは含まれない。
- [ ] 施設形態5種別 × 転倒リスク3段階の全15通りの組み合わせに対して、
      それぞれ認証済みで `POST /api/chat` を呼び出したとき、すべてステータス
      コード200が返る（手動またはスクリプトで15リクエストを順番に送り、
      全件のHTTPステータスが200であることを確認する）。
- [ ] `facility_type` と `fall_risk` を両方省略したリクエスト
      `{"messages": [{"role": "user", "content": "テスト"}]}` を認証済みで
      送ると、ステータスコード200と `{"reply": "..."}` が返り、Sprint 7
      までと同等の動作が維持される（後方互換性の確認）。
- [ ] `facility_type` のみを省略、または `fall_risk` のみを省略したリクエスト
      を認証済みで送った場合も、それぞれステータスコード200と
      `{"reply": "..."}` が返り、エラーにならない（片方だけ省略した場合も
      デフォルト値で動作する）。
- [ ] 施設形態が異なると適用されるシステムプロンプトが切り替わることを手動
      確認する。認証済みで
      `{"messages": [{"role": "user", "content": "あなたが対応する施設の種別と、その施設の特徴を教えてください"}], "facility_type": "グループホーム", "fall_risk": "中"}`
      と
      `{"messages": [{"role": "user", "content": "あなたが対応する施設の種別と、その施設の特徴を教えてください"}], "facility_type": "特別養護老人ホーム", "fall_risk": "中"}`
      をそれぞれ `POST /api/chat` に送り、両レスポンスの `reply` フィールドが
      互いに異なる施設種別の特徴に言及していることを目視確認する。
- [ ] 転倒リスクレベルが異なると適用されるシステムプロンプトが切り替わること
      を手動確認する。認証済みで
      `{"messages": [{"role": "user", "content": "この利用者の転倒リスクに対してどのような対応方針を取りますか"}], "facility_type": "デイサービス", "fall_risk": "小"}`
      と
      `{"messages": [{"role": "user", "content": "この利用者の転倒リスクに対してどのような対応方針を取りますか"}], "facility_type": "デイサービス", "fall_risk": "高"}`
      をそれぞれ `POST /api/chat` に送り、両レスポンスの `reply` フィールドが
      異なるリスクレベルの対応方針（介助度・見守り方法など）に言及している
      ことを目視確認する。
- [ ] 未認証（Sprint 7のトークンなし）で `facility_type` と `fall_risk` を
      指定して `POST /api/chat` を呼び出すと、従来通りステータスコード401
      または403が返り、`reply` フィールドは含まれない。

**Out of scope:** フロントエンドUIへの施設形態・転倒リスク選択欄の追加
（Sprint 10で実装）、施設ごとの追加フォームフィールドや入力画面の変更、
ユーザーが選択した施設形態・リスクレベルの保存・履歴管理、プロンプト内容
のバージョン管理・管理者画面からの編集機能。

---

## Sprint 9: Sprint 7認証コードの撤去（Cognito移行前クリーンアップ）

**Status:** Done

**Goal:** Sprint 7 で実装した共有パスフレーズ方式の認証を完全に撤去し、
`POST /api/chat` および `GET /api/reports` が認証チェックなしで直接応答する
クリーンな中間状態を確立する。Sprint 11 での AWS Cognito 認証導入の
準備として、現行の認証コード・依存設定を残さない。

**Definition of Done:**
- [ ] `cd src && uvicorn api:app` でサーバーを起動した後、
      `curl -s -o /dev/null -w "%{http_code}" -X POST http://127.0.0.1:8000/api/login -H "Content-Type: application/json" -d "{}"` を実行すると
      ステータスコード404が返る（`POST /api/login` エンドポイントが
      存在しないことの確認）。
- [ ] 認証ヘッダー・Cookie・トークンを一切付与せずに
      `curl -s -w "\n%{http_code}" -X POST http://127.0.0.1:8000/api/chat -H "Content-Type: application/json" -d '{"messages":[{"role":"user","content":"テスト"}]}'`
      を実行すると、ステータスコード200でレスポンスボディに `"reply"` キーが
      含まれる（401・403が返らないことの確認）。
- [ ] 認証ヘッダー・Cookie・トークンを一切付与せずに
      `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/api/reports`
      を実行すると、ステータスコード200が返る（401・403が返らないことの確認）。
- [ ] Sprint 8 で追加した `facility_type` と `fall_risk` パラメータが
      引き続き動作する。認証なしで
      `curl -s -w "\n%{http_code}" -X POST http://127.0.0.1:8000/api/chat -H "Content-Type: application/json" -d '{"messages":[{"role":"user","content":"テスト"}],"facility_type":"グループホーム","fall_risk":"中"}'`
      を実行すると、ステータスコード200でレスポンスボディに `"reply"` キーが
      含まれる。
- [ ] Sprint 8 のバリデーションが引き続き動作する。認証なしで
      `facility_type` に `"病院"` を指定して `POST /api/chat` を呼び出すと
      ステータスコード422が返り、`"fall_risk"` に `"最大"` を指定して
      `POST /api/chat` を呼び出すと同じくステータスコード422が返る。
- [ ] `facility_type` と `fall_risk` を両方省略した
      `{"messages":[{"role":"user","content":"テスト"}]}` を認証なしで
      `POST /api/chat` に送ると、ステータスコード200でレスポンスボディに
      `"reply"` キーが含まれる（後方互換性の確認）。

**Out of scope:** フロントエンド（`static/index.html`）のログイン画面・
ログアウトボタン等の認証UIの撤去（Sprint 10 のUI刷新でまとめて対応）、
AWS Cognito 認証の導入（Sprint 11 で対応）、報告書の保存・一覧取得の
ビジネスロジックの変更。

---

## Sprint 10: フロントエンド全面刷新

**Status:** Done

**Goal:** `static/index.html` を全面的に刷新し、Sprint 9 で撤去済みのバック
エンド認証に合わせてログインUI・ログアウトボタンを削除する。あわせて
Sprint 8 のバックエンドに対応した施設形態・転倒リスク選択欄を追加し、
時刻・バイタルサイン入力をモバイルフレンドリーなUI（ドラムロール式・
ダイアログ式）に刷新し、介護施設スタッフが実務で日常的に使えるレスポン
シブデザインに改善する。

**Definition of Done:**
- [ ] `cd src && uvicorn api:app` でサーバーを起動してブラウザで
      `http://127.0.0.1:8000/` を開いたとき、ログイン画面・ログインフォームが
      一切表示されず、報告書入力フォームまたはチャットUIが直接表示される
      （手動確認）。
- [ ] 同じブラウザ画面を全スクロールしたとき、ログアウトボタンまたはログ
      アウトに相当するUI要素がどこにも存在しない（手動確認）。
- [ ] ブラウザの開発者ツール「ネットワーク」タブを開いた状態でページを読み
      込み、フォームへの入力・送信操作を一通り行ったとき、フロントエンドから
      `/api/login`・`/api/logout`・`/api/session` へのHTTPリクエストが
      1件も記録されていない（手動確認）。
- [ ] フォーム画面に「施設形態」選択欄があり、「グループホーム」
      「特別養護老人ホーム」「介護老人保健施設」「デイサービス」「自宅」の
      5種別がすべて選択肢として表示される（手動確認: 選択欄を開き5種別を
      目視確認する）。
- [ ] フォーム画面に「転倒リスク」選択欄があり、「小」「中」「高」の3段階が
      すべて選択肢として表示される（手動確認: 選択欄を開き3段階を目視確認
      する）。
- [ ] 施設形態を「特別養護老人ホーム」、転倒リスクを「高」に設定してフォーム
      を送信したとき、ブラウザの開発者ツール「ネットワーク」タブで
      `POST /api/chat` のリクエストペイロードを確認すると
      `"facility_type": "特別養護老人ホーム"` と `"fall_risk": "高"` が
      両方含まれており、レスポンスのHTTPステータスコードが200である
      （手動確認）。
- [ ] ブラウザの開発者ツールでデバイスモードを有効にし、幅375px・高さ667px
      （iPhone SE相当）に設定してページを表示したとき、入力フォームの全フィー
      ルド・送信ボタン・報告書一覧の各行がいずれも画面横幅を超えてはみ出さず、
      縦スクロールで全要素にアクセスできる（手動確認）。
- [ ] Sprint 4 のlocalStorage下書き保存機能が引き続き動作する。フォームに
      4項目以上入力してからページをリロード（F5）すると、リロード後にすべて
      の入力値が復元されている（手動確認）。さらに送信成功後にリロードすると
      フォームが空になっていることも確認する。
- [ ] Sprint 5・6 の報告書保存・一覧・詳細表示が引き続き動作する。フォームを
      送信してアシスタントの返信が表示された後、報告書一覧UIを開くと当該報告
      書が一覧に表示され、その行をクリックすると全文が確認できる（手動確認）。
- [ ] `static/` ディレクトリ配下に新たなローカルの `.js` ファイルおよび
      `.css` ファイルが追加されておらず、`static/index.html` 単一ファイルで
      フロントエンドの全機能が成立している（手動確認: ブラウザの開発者ツール
      「ネットワーク」タブで、オリジンが `127.0.0.1:8000` である `.js`・`.css`
      リクエストが `index.html` 以外に存在しないことを確認する）。

- [ ] フォームのラベル「転倒時対応」が「事故内容」に、「転倒後対応」が
      「事故後対応」に変更されている（手動確認: フォームを開いてラベルを
      目視確認する）。
- [ ] 時刻入力欄がドラムロール式（スクロール選択）で「時」「分」を個別に
      選択できる（手動確認: 時刻欄をタップ/クリックするとドラムロール型の
      ピッカーが表示され、時・分を選択できることを確認する）。
- [ ] バイタルサイン（血圧・脈拍・体温・SpO2）の入力がダイアログ式UIで
      行える（手動確認: バイタル入力ボタンをタップするとダイアログが開く
      ことを確認する）。
      - 血圧: 収縮期(000)/拡張期(000)/脈拍(000) の形式で各桁をドラムロール
        またはスピナーで入力できる
      - 体温: 整数部30〜42℃をドラムロール等で選択し、小数点以下0〜9を
        別選択で入力できる
      - SpO2: 80〜100%の範囲で選択でき、初期値が100%になっている
- [ ] バイタルサインで入力した値がフォーム送信時に `POST /api/chat` の
      メッセージ本文に含まれてアシスタントに渡される（手動確認: バイタルを
      入力して送信後、返信内容にバイタル値への言及が含まれることを目視確認
      する）。

**Out of scope:** `src/api.py` および `src/bot.py` への変更、施設形態・転倒
リスクの選択値のlocalStorageへの保存や次回アクセス時への引き継ぎ、AWS
Cognito 認証の導入（Sprint 11 で対応）、施設形態・転倒リスクによる報告書
一覧のフィルタリング。
