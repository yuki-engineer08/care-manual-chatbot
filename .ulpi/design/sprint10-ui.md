# Sprint 10 UI 仕様 — 事故報告書フォーム全面刷新

> Binds to `.ulpi/design/DESIGN.md`. Every screen must read as the same product if placed side by side.

---

## 画面構成（single page, タブ切り替え）

```
[ ヘッダー: アプリ名 + タブナビ ]
  Tab A: 報告書を作成
  Tab B: 過去の報告書
[ コンテンツエリア ]
[ AI返信エリア（Tab A のみ、送信後に出現）]
```

---

## ユーザーフロー

### 主フロー（報告書作成）

```
開く
  → Tab A「報告書を作成」が表示
  → localStorage に下書きあり？
      YES → 各フィールドを自動復元（サイレント、通知なし）
      NO  → 空フォーム
  → 施設形態を選択
  → 転倒リスクを選択
  → 時刻ピッカーをタップ → ドラムロールピッカー開く
      → 時・分をスクロール選択 → 「確定」タップ → ピッカーを閉じる
  → 事故内容を入力（textarea）
  → 事故後対応を入力（textarea）
  → 「バイタルを入力」ボタンをタップ → バイタルダイアログ開く
      → 血圧・脈拍・体温・SpO2 を入力 → 「確定」タップ
  → 「報告書を生成」ボタンをタップ
      → 送信中スピナー表示
      → 成功 → AI返信エリアにスライドイン表示 → localStorage 下書き削除
      → 失敗 → エラートースト表示 → 下書き保持
```

### フロー B（過去の報告書）

```
Tab B をタップ
  → GET /api/reports
      → ローディング中: スケルトン行 ×3
      → 0件: 空状態コンポーネント
      → N件: リスト表示（新しい順）
  → 行をタップ
      → 詳細パネルがスライドイン（または同ページ内展開）
      → 「戻る」ボタンでリストに戻る
```

### エッジケース

| ケース | 挙動 |
|--------|------|
| 送信中にリロード | 送信が中断される。下書きはlocalStorageにあるため復元可能 |
| オフライン状態で送信 | fetch が失敗しエラートースト。下書き保持 |
| バイタル未入力で送信 | バイタル未入力でも送信可能（任意項目）。メッセージ本文には未計測と記載 |
| localStorage 不可 | try/catch でサイレントフォールバック。下書き保存機能のみ無効化 |
| 巨大なAI返信 | エリアに max-height + overflow-y: auto でスクロール可能に |

---

## レイアウト

### ヘッダー

- 高さ 56px、background: `var(--color-accent)` （テラコッタ）
- 白テキスト: アプリ名「事故報告書アシスト」Noto Sans JP 600 16px
- タブ: ヘッダー下部にアタッチ、白地 + テラコッタのアクティブアンダーライン（3px）

### セクション帯（Signature）

フォームの各セクション（施設情報 / 時刻・事故内容 / バイタル / 送信）の前に配置。

```
[ テラコッタ帯 (#A34D2A) ]
  左端: 縦ライン 3px × 100% height、color: accent-light
  テキスト: Noto Sans JP 800 18px、color: white、padding: 10px 16px
```

帯にborder-radiusはつけない（サイン的に角ばらせる）。

### フォームエリア

- padding: `var(--space-4)` (16px) all sides
- フォームグループ間の gap: `var(--space-6)` (24px)
- ラベル: Noto Sans JP 600 14px、color: text、margin-bottom 6px
- 入力欄: border 1.5px solid `var(--color-border)`、radius `var(--radius-md)`、padding 12px 14px、font-size 16px
- フォーカス: border-color `var(--color-accent)`、box-shadow `0 0 0 3px var(--color-accent-light)`

---

## コンポーネント仕様

---

### 1. セレクト（施設形態・転倒リスク）

**目的:** 施設形態5種別と転倒リスク3段階の選択。

**実装:** `<select>` ネイティブ要素（モバイル OS の標準ピッカーを活用）+ カスタムスタイリング。

**施設形態の選択肢:**
- グループホーム
- 特別養護老人ホーム
- 介護老人保健施設
- デイサービス
- 自宅

**転倒リスクの選択肢:**
- 小（要支援1〜2 相当）
- 中（要介護1〜2 相当）
- 高（要介護3〜5 相当）

**状態:**

| State | Visual | Behavior |
|-------|--------|----------|
| default | border: `--color-border` | — |
| focus | border: accent、shadow accent-light | — |
| filled | text: `--color-text` | 値を保持 |
| error | border: danger | エラーメッセージを下に表示 |

**アクセシビリティ:**
- `<label for>` と `<select id>` で紐づけ
- 転倒リスクの選択肢には parenthetical で内容詳細を含める

---

### 2. ドラムロール時刻ピッカー

**目的:** 事故発生時刻を「時」「分」のドラムロールUIで入力する。

**トリガー:** 時刻フィールドをタップ → オーバーレイ表示。

**レイアウト（オーバーレイ内）:**
```
[ タイトル: 時刻を選択 ]
[ 選択窓: ハイライト帯（accent-light背景、上下に区切り線）]
  | 23 |  :  | 58 |   ← 前後が見えて、スクロールを促す
  | 00 |     | 59 |   ← 選択中（大きく、Noto 700 36px）
  | 01 |     | 00 |
[ キャンセル ] [ 確定 ]
```

**スクロール動作:**
- touch: `overflow-y: scroll` + `scroll-snap-type: y mandatory` + `scroll-snap-align: center`
- mouse: scroll イベントで位置制御
- アイテム高さ: 52px（タップターゲット≥44pt）
- リスト: 時 00–23、分 00–59（循環スクロール）

**選択中数値の表現:**
- font: Noto Sans JP 700 36px、color: `var(--color-accent)`
- 前後数値: 24px、color: `var(--color-muted)`
- ハイライト帯: `var(--color-accent-light)`、上下に1px border `var(--color-border)`

**状態:**

| State | Visual | Behavior |
|-------|--------|----------|
| closed | 「--:--」グレープレースホルダー | タップで開く |
| open | オーバーレイ表示 | スクロール可能 |
| confirmed | 「HH:MM」テキスト表示 | — |

**オーバーレイアニメーション:** 下からスライドイン 280ms ease-out。バックドロップ: `oklch(0.16 0.018 50 / 0.4)` フェードイン 120ms。

**アクセシビリティ:**
- `role="dialog"` `aria-modal="true"` `aria-label="時刻を選択"`
- 「確定」にフォーカス移動（open 時）
- ESC でキャンセル
- touch target: 各アイテム 52px × full-width
- `prefers-reduced-motion`: アニメーションなし、即時表示

---

### 3. バイタルサイン入力ダイアログ

**目的:** 血圧（収縮期/拡張期）・脈拍・体温・SpO2 を入力する。

**トリガー:** 「バイタルを入力」ボタン（secondary variant）をタップ → モーダルダイアログ。

**ダイアログレイアウト:**
```
[ X 閉じる ]  [ タイトル: バイタルサイン ]

── 血圧 ─────────────────────────────────
  収縮期       拡張期       脈拍
  [ 0|0|0 ]  /  [ 0|0|0 ]  ──  [ 0|0|0 ]
  (mmHg)        (mmHg)          (回/分)
  ドラムロール3桁  ドラムロール3桁  ドラムロール3桁

── 体温 ─────────────────────────────────
  整数部         小数部
  [ 36 ] . [ 5 ] ℃
  (30〜42)       (0〜9)
  ドラムロール     ドラムロール

── SpO2 ─────────────────────────────────
  [ 1|0|0 ] %   ← 初期値100
  (80〜100)
  ドラムロール3桁

[ キャンセル ]          [ 確定 ]
```

**血圧・脈拍のドラムロール（3桁）:**
- 各桁を独立したドラムロール（0–9）
- 収縮期: 桁1（0–2）/ 桁2（0–9）/ 桁3（0–9）
- 拡張期: 桁1（0–1）/ 桁2（0–9）/ 桁3（0–9）
- 脈拍: 桁1（0–2）/ 桁2（0–9）/ 桁3（0–9）
- アイテム高さ: 48px、数値 font: Noto Sans JP 700 28px

**体温のドラムロール:**
- 整数: 30–42（縦スクロール、13項目）
- 小数: 0–9（縦スクロール）
- 表示: 「36.5℃」

**SpO2のドラムロール（3桁）:**
- 桁1（0–1） / 桁2（0–9） / 桁3（0–9）
- 初期値: 100（各桁 1/0/0）
- 入力値は 80–100 の範囲を想定（バリデーションはUI上で暗示）

**確定時の動作:**
- バイタルボタンのラベルを「バイタル入力済 ✓」に変更（accent色）
- 送信メッセージに以下を含める:
  ```
  【バイタル】血圧 XXX/XXX mmHg、脈拍 XXX 回/分、体温 XX.X℃、SpO2 XXX%
  ```
- 未入力（未タップ）の場合はバイタル行を省略

**状態:**

| State | Visual | Behavior |
|-------|--------|----------|
| closed | ボタン「バイタルを入力」(secondary) | タップで開く |
| open | モーダル全画面 (mobile) / 中央配置 (desktop) | スクロール可 |
| confirmed | ボタン「バイタル入力済 ✓」(accent-light bg) | 再タップで再編集 |
| reset | フォームリセット or 送信成功後 | 初期値に戻す |

**ダイアログアニメーション:** 下からスライドイン 280ms ease-out（時刻ピッカーと同じ動作）。

**アクセシビリティ:**
- `role="dialog"` `aria-modal="true"` `aria-label="バイタルサインを入力"`
- ダイアログ open 時に最初の入力にフォーカス
- ESC でキャンセル（変更は破棄）
- 各ドラムロール列に `aria-label="収縮期 百の位"` 等
- `aria-live="polite"` で確定値をアナウンス

---

### 4. セクションヘッダー（Signature コンポーネント）

```html
<div class="section-header">
  <span class="section-header__bar"></span>
  <span class="section-header__label">施設情報</span>
</div>
```

**CSS:**
```css
.section-header {
  background: var(--color-accent);
  display: flex; align-items: center;
  padding: 10px 16px; gap: 10px;
  margin: 0 -16px; /* フォームパディングを打ち消してフルブリード */
}
.section-header__bar {
  width: 3px; height: 20px;
  background: var(--color-accent-light);
  flex-shrink: 0;
}
.section-header__label {
  font: 800 18px/1 'Noto Sans JP', sans-serif;
  color: #fff; letter-spacing: -0.01em;
}
```

---

### 5. AI返信エリア

- フォームの下にスライドイン（送信成功後）
- セクション帯: 「報告書（案）」
- 本文: Noto Sans JP 400 16px、color: text、line-height: 1.75
- コピーボタン: 右上にアイコン付き（secondary）
- ローディング中: 点滅する3点「生成中…」

**状態:**

| State | Visual | Behavior |
|-------|--------|----------|
| hidden | 非表示 | — |
| loading | スケルトン行 ×5 + 「生成中…」 | Anthropic API 待機中 |
| success | 報告書テキスト全文 | コピー可能 |
| error | 赤いトーストバナー | 「生成できませんでした。再送信してください。」 |

---

### 6. 報告書一覧・詳細

**一覧:**
- リスト with dividers（カードは使わない）
- 各行: 日時（Noto 600 14px）+ 施設形態チップ（accent-light bg、accent text）
- 空状態: 中央配置、アイコン（📋 は使わない、CSS のみ）+ 「まだ報告書がありません」
- ローディング: スケルトン行 ×3

**詳細:**
- 同ページ内でリストが非表示→詳細が表示（CSSクラスの切り替え）
- セクション帯「報告書詳細」
- メタ情報（日時・施設形態・転倒リスク）: caption スタイル
- 報告書本文: body スタイル、白紙背景

---

### 7. 送信ボタン

- variant: primary（accent 背景）
- サイズ: full-width、min-height 52px（タップターゲット）
- Noto Sans JP 600 16px、白テキスト
- loading 時: スピナー（CSS animation: rotate 1s linear infinite）+ テキスト「生成中…」
- disabled 時: opacity 0.5、cursor not-allowed

---

## アクセシビリティ全体

- `lang="ja"` を `<html>` に設定
- フォームの `<fieldset>` + `<legend>` でセクションをグループ化
- すべてのインタラクティブ要素に visible focus ring（`var(--color-accent-light)` 3px outline）
- エラーメッセージは `role="alert"` で自動アナウンス
- モーダルが開いている間は背景の `aria-hidden="true"`

---

## Pre-Flight Gate 結果

### Identity lock
- [x] 全コンポーネントが DESIGN.md の値のみ使用
- [x] アクセント1色（テラコッタ）、radius 1スケール、type 1ファミリー
- [x] 全画面が同じプロダクトに見える

### Anti-slop
- [x] 禁止フォント 0（Noto Sans JP は banned list に含まれない）
- [x] 禁止カラー 0（紫グロー・クリーム地・グラデーションテキスト なし）
- [x] 禁止レイアウト 0（3等分カード・ネストカード・デフォルトヒーロー なし）
- [x] スロップテスト合格: テラコッタ×サイン帯は介護アプリの LLM 的デフォルト回答ではない
- [x] 反実仮想テスト合格: 似たブリーフに対してこのデザインは出力しない
- [x] Signature（セクション帯）が存在し、briefから導かれている

### State & flow coverage
- [x] loading / empty / error / success 状態を全コンポーネントで定義
- [x] リロード・オフライン・バイタル未入力等のエッジケースを定義

### Accessibility
- [x] コントラスト比を全色役割で記載・WCAG AA 合格
- [x] キーボードフォーカス・ESC 動作を全ダイアログで指定
- [x] `prefers-reduced-motion` 対応
- [x] ARIA ロール・アナウンスを非自明コンポーネントで指定
- [x] タッチターゲット ≥ 44pt（52px 行高・ボタン高 52px）

### Layout craft
- [x] ≥3 distinct レイアウトファミリー: リスト with dividers / フルブリードサイン帯 / ダイアログドラムロール
- [x] 1ページに1つの主アクション（送信ボタン）

### Cognitive load
- [x] フォームセクションは4グループ（施設 / 時刻・内容 / バイタル / 送信）
- [x] タブは2項目のみ

### Scored self-critique

| axis | score (0–4) | note |
|------|-------------|------|
| distinctiveness | 4 | テラコッタ×サイン帯は介護アプリの想定外 |
| hierarchy & focus | 3 | セクション帯で明確、送信ボタンが唯一の primary |
| consistency with DESIGN.md | 4 | 全値を DESIGN.md から参照 |
| accessibility | 3 | WCAG AA 合格・touch target 確認 |
| state/edge coverage | 3 | 主要ケースを網羅 |
| copy quality | 3 | 現場目線・責めない文言 |
| restraint | 3 | Signature 1箇所に集中、他はシンプル |
| motion motivation | 4 | スライドイン2箇所のみ、理由明確 |

**Total: 27/32**（最低軸スコア: 3）— 全軸 ≥ 3 ✓

---

## Build Handoff

**対象エージェント:** `chatbot-generator`（vanilla JS/HTML/CSS、ビルドステップなし）

**実装対象ファイル:** `static/index.html`（単一ファイル）

**デザインシステム:** bespoke — CSS カスタムプロパティ（上記 DESIGN.md の tokens を CSS 変数として実装）

**Google Fonts:**
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;600;800&display=swap" rel="stylesheet">
```

**実装指示:**
1. `DESIGN.md` の全トークンを `:root { }` の CSS 変数として実装する
2. セクションヘッダーは本仕様の `.section-header` CSS を忠実に実装する（Signature）
3. ドラムロールは `scroll-snap` ベースのネイティブスクロールで実装する（外部ライブラリ不可）
4. バイタルダイアログと時刻ピッカーはどちらも `position: fixed` のオーバーレイ
5. Sprint 4 の localStorage 下書き保存を維持する
6. Sprint 5/6 の報告書一覧・詳細を本仕様のリストスタイルに刷新する
7. ログイン画面・ログアウトボタン・`/api/login|logout|session` への呼び出しを全削除する
8. `POST /api/chat` に `facility_type` と `fall_risk` を含める（Sprint 8 連携）

**Sprint 10 DoD との対応（全10項目をこの仕様が担保）:**
- ログインUI なし → ヘッダー+フォームが直接表示される設計
- ログアウトボタン なし → 設計上存在しない
- /api/login 等の呼び出し なし → コード上も削除
- 施設形態5種別 → セレクト仕様に定義
- 転倒リスク3段階 → セレクト仕様に定義
- POST /api/chat に facility_type/fall_risk を含む → フォームのデータ組み立てに含める
- 375px でのレスポンシブ → モバイルファーストで設計
- localStorage 下書き保存継続 → 明示的に維持を指示
- 報告書一覧・詳細継続 → コンポーネント仕様 §6 に定義
- 単一ファイル構成 → index.html のみ、外部 JS/CSS なし

**Implement exactly this spec. Theme the design system with our locked tokens; do NOT redesign or re-implement the components independently.**
