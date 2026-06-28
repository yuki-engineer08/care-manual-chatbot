---
project: care-manual-chatbot
register: product
aesthetic_direction: industrial / signage
color_strategy: restrained
design_system: bespoke (vanilla JS/HTML/CSS — no framework; CSS custom properties)
design_variance: 6
motion_intensity: 3
visual_density: 5
---

## Design Read

現場のサイン板と、使い込まれた業務日誌の交差点。速くて迷わない、でも冷たくない。

## Signature

各フォームセクションの見出しを**部署サイン帯**として表現する。テラコッタ色の横帯に白の重量級テキスト、左端に細い縦ライン。入力箇所の区切りが一目でわかり、病院とも一般アプリとも違う「ここは介護の現場だ」という空気を作る。ドラムロール時刻ピッカーはその帯の延長で、大きな数字を中央に配置した「時計盤」として開く。

## Counterfactual test

介護アプリのデフォルト回答：淡いミントグリーン／ブルー＋丸みのあるカード。このデザインはテラコッタ×ダークウォームグレー×サイン帯レイアウトを使い、その回答を外す。

---

## Color (locked)

ハブ色: テラコッタ（hue 35–42）に向けてニュートラルをすべてチント。

| role | OKLCH | hex | use |
|------|-------|-----|-----|
| background | oklch(0.96 0.010 50) | #F7F4F0 | ページ背景 |
| surface | oklch(0.99 0.005 50) | #FDFCFB | カード・フォーム背景 |
| elevated | oklch(1.00 0.000 0) | #FFFFFF | ダイアログ・ポップオーバー |
| text | oklch(0.16 0.018 50) | #231E19 | 本文・ラベル (contrast on bg: ≥7:1 ✓) |
| muted | oklch(0.44 0.016 50) | #6B6058 | プレースホルダー・補助テキスト (contrast on bg: ≥4.7:1 ✓) |
| subtle | oklch(0.70 0.012 50) | #B5ADA5 | 区切り線・非アクティブ |
| border | oklch(0.87 0.010 50) | #DDD8D2 | 入力枠・カード境界 |
| accent | oklch(0.52 0.17 38) | #A34D2A | プライマリアクション・セクション帯 (on white: 5.5:1 ✓) |
| accent-hover | oklch(0.44 0.17 38) | #883D20 | ホバー・押下 |
| accent-light | oklch(0.93 0.04 38) | #F5E8E1 | アクセントの薄い背景 |
| success | oklch(0.52 0.13 148) | #2E7A52 | 送信成功 (on white: 5.3:1 ✓) |
| warning | oklch(0.68 0.16 72) | #C08700 | 警告 (on white: 4.6:1 ✓) |
| danger | oklch(0.50 0.20 27) | #B83030 | エラー (on white: 5.8:1 ✓) |
| info | oklch(0.52 0.12 228) | #2E5E9A | 情報 (on white: 5.6:1 ✓) |

**60-30-10 配分:** background/surface が60%、text/border/muted が30%、accent が10%。

---

## Type (locked)

日本語対応のため、Noto Sans JP 一本でウェイト変化により役割を分ける（1ファミリー複数ウェイト方式）。サイン的な視覚強度は font-size × font-weight の組み合わせで表現する。

| role | family | weight | size | use |
|------|--------|--------|------|-----|
| display | Noto Sans JP | 800 | 20–24px | セクション帯の見出し |
| label | Noto Sans JP | 600 | 14–16px | フォームラベル・ボタン |
| body | Noto Sans JP | 400 | 16px | テキストエリア本文・AI返信 |
| caption | Noto Sans JP | 400 | 13px | 補助テキスト・エラーメッセージ |
| data | Noto Sans JP | 700 | 36–48px | ドラムロールの選択中数値 |

- body measure: 最大60ch（モバイル）、textarea はフル幅
- 見出しのletter-spacing: −0.02em（表示サイズ20px以上）
- Google Fonts CDN: `?family=Noto+Sans+JP:wght@400;600;800`

---

## Scales (locked)

**Spacing (4px base):**
`--space-1: 4px` `--space-2: 8px` `--space-3: 12px` `--space-4: 16px` `--space-5: 20px` `--space-6: 24px` `--space-8: 32px` `--space-10: 40px` `--space-12: 48px` `--space-16: 64px`

**Radius:**
`--radius-sm: 4px` `--radius-md: 8px` `--radius-lg: 12px` `--radius-full: 9999px`
フォーム入力: `--radius-md`、セクション帯: `0`（サイン感）、ダイアログ: `--radius-lg`、タグ/チップ: `--radius-full`

**Shadow / elevation:**
`--shadow-sm: 0 1px 2px oklch(0.16 0.018 50 / 0.08)` — 入力フォーカス
`--shadow-md: 0 4px 12px oklch(0.16 0.018 50 / 0.12)` — カード
`--shadow-lg: 0 8px 32px oklch(0.16 0.018 50 / 0.18)` — ダイアログ

**Motion:**
`--duration-fast: 120ms` `--duration-base: 280ms` `--duration-emphasis: 480ms`
easing: `cubic-bezier(0.16, 1, 0.3, 1)` (ease-out)
`@media (prefers-reduced-motion: reduce)` → duration を 0ms に上書き
すべてのモーションに理由を要求する。反射的な animation は使わない。

**Breakpoints:**
`sm: 640px` `md: 768px` — 最小ターゲット幅 375px

---

## Voice

register: 簡潔・丁寧・現場目線
action vocabulary: 「送信する」→「送信中…」→「報告書を保存しました」（一貫した動詞チェーン）
エラー: 「送信できませんでした。もう一度お試しください。」（責める表現を避ける）
空状態: 「まだ報告書がありません」（シンプル、問題提起なし）

---

*Every screen must read as the same product if placed side by side.*
