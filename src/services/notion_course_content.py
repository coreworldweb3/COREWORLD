"""ユーザー提供の7回構成に基づく案内と、追加作成した第1回教材。"""

import discord

CURRICULUM = (
    ("AIだけで仕事を完結させる", 15, "議事録・タスク一覧を作り、Notionなしでどこまでできるか試す"),
    ("情報が増えると何が起きる？", 20, "案件・担当者・更新履歴が増えたときの検索と管理を体験"),
    ("Notionデータベース入門", 25, "同じ情報で案件管理表を作り、AIだけの場合と比較"),
    ("情報同士をつなげてみよう", 30, "案件・タスク・議事録をリレーションで関連付ける"),
    ("AIとNotionを組み合わせる", 25, "情報整理や更新を試し、連携の利点を検証"),
    ("Notion以外でもできる？", 30, "Google Sheetsなどで同じ仕組みを再現"),
    ("最終比較・採用判断", 20, "操作性・費用・検索性・共同作業を比較して採用を判断"),
)

SAMPLE_CSV = """ID,案件,担当,状態
P001,Webサイト改修,田中,進行中
P002,社内FAQ整備,佐藤,未着手
P003,セキュリティ点検,鈴木,確認待ち
"""

MEETING = """2026年10月12日の定例会議（架空データ）
P001：田中が10月16日までに改修案を作成する。山本が10月19日までにレビューする。
P002：佐藤が10月15日までに質問を収集する。FAQの公開日は未定。
P003：鈴木が10月14日までに点検項目を整理する。点検実施日は未定。
次回会議は10月19日。未定の事項は次回確認する。
"""

def course_embed() -> discord.Embed:
    embed = discord.Embed(
        title="📚 AI時代にNotionは本当に必要なのか？",
        description=(
            "AI・Notion・Google Sheetsを比較する実践型学習企画\n\n"
            "AIだけで十分なのか？ Notionを使う価値があるのか？ 別のツールが適しているのか？\n"
            "架空のIT企業を題材に、手を動かして自分で判断できるようになることを目指します。"
        ),
        color=0x5865F2,
    )
    embed.add_field(name="🎯 目的", value="情報の長期管理・共有・案件とタスクと議事録の関連付けを検証します。Notionを使うこと自体を結論にはしません。", inline=False)
    embed.add_field(
        name="🗓️ 全7回のカリキュラム",
        value="\n\n".join(f"**第{i}回：{title}（{minutes}分）**\n{summary}" for i, (title, minutes, summary) in enumerate(CURRICULUM, 1)),
        inline=False,
    )
    embed.add_field(name="🧪 実践課題", value="Webサイト改修・社内FAQ整備・セキュリティ点検の3案件。同じ情報をAIのみ、Notion、Google Sheetsで管理し比較します。コース全体では各案件5件のタスク、議事録、担当者・期限の変更を扱います。", inline=False)
    embed.add_field(name="📦 学習キット", value="初心者向け解説・手順付き演習・サンプルデータ・模範解答・理解度チェック・比較評価シート。無料機能を中心に進め、有料機能には代替方法を検討します。", inline=False)
    embed.add_field(name="🔍 評価の観点", value="初期構築、更新、検索の正確さ、情報の一貫性、共同作業、費用と保守を各1～5点で評価。未評価は集計から除外し、単純な合計だけで採用を決めません。", inline=False)
    embed.add_field(name="👥 参加・開始方法", value="初心者・IT経験者どちらも参加できます。下のボタンから第1回へ。教材は押した本人だけに表示されます。現在Discordで開始できる教材は第1回です。", inline=False)
    embed.set_footer(text="全7回・合計165分｜第1回は15分｜進捗の保存と第2～7回の配信は今後の実装対象")
    return embed


def lesson_embed() -> discord.Embed:
    embed = discord.Embed(title="第1回：AIだけで仕事を完結させる（15分）", description="目標：AIで議事録とタスク表を作り、原文と照合する。今回はNotion・Sheetsを使いません。", color=0x2ECC71)
    embed.add_field(name="1. 準備（2分）", value="普段使う対話型AIを開きます。添付CSVは3案件の初期状態です。以下はすべて架空データ。BotがAIを呼び出すのではなく、自分で文章をコピーして試します。", inline=False)
    embed.add_field(name="2. 会議メモ", value=f"```text\n{MEETING}```", inline=False)
    embed.add_field(name="3. AIへの指示（5分）", value="以下を会議メモと一緒にAIへ貼り付けます。\n```text\nこの会議メモから、議事録（決定事項・未決事項・次回予定）とタスク一覧を作ってください。タスクの列は案件ID、作業、担当、期限、状態とし、状態はすべて未着手にしてください。原文にない担当や期限は推測せず「未定」としてください。案件自体の状態とタスクの状態を区別してください。\n```", inline=False)
    embed.add_field(name="4. 照合・更新（5分）", value="① 担当・期限を原文と照合し、AIが補った情報がないか確認。\n② 同じAIチャットに「P001の改修案の担当を田中から高橋に変更し、期限を10月20日に変更。他は維持してタスク一覧を再表示」と指示。\n③ 「P001の現在の担当と期限、変更前の担当と期限を教えて」と質問し、正確さを確認。", inline=False)
    embed.add_field(name="5. 提出物・振り返り（3分）", value="議事録・更新前後のタスク表・照合で見つけた誤りを手元に保存。AIだけで便利だった点と、探す・更新する・共有する際の不安を各1つ記録します。最後に下のボタンで答え合わせ。", inline=False)
    embed.set_footer(text="15分で終わらなければ途中まででOK。表示が消えた場合は案内の開始ボタンから再開できます。")
    return embed


def answer_embed() -> discord.Embed:
    embed = discord.Embed(title="第1回：模範解答・理解度チェック", description="表現が違っていても、原文に沿った内容なら正解です。", color=0xF1C40F)
    embed.add_field(name="議事録の例", value="決定事項：P001の改修案・レビュー、P002の質問収集、P003の点検項目整理を進める。\n未決事項：FAQ公開日、点検実施日。\n次回会議：2026年10月19日。未決事項を確認する。", inline=False)
    embed.add_field(name="更新前のタスク一覧", value="```text\n案件 | 作業 | 担当 | 期限（2026年） | 状態\nP001 | 改修案作成 | 田中 | 10/16 | 未着手\nP001 | レビュー | 山本 | 10/19 | 未着手\nP002 | 質問収集 | 佐藤 | 10/15 | 未着手\nP003 | 点検項目整理 | 鈴木 | 10/14 | 未着手\n```\nFAQ公開と点検実施をタスクに含める場合は、担当・期限を推測せず未定とします。", inline=False)
    embed.add_field(name="更新後の正解", value="P001の改修案作成だけ、担当が高橋・期限が10月20日。他の3タスクは同じ。変更履歴は田中→高橋、10月16日→10月20日です。", inline=False)
    embed.add_field(name="理解度チェック（先に自分で答えてください）", value="Q1：FAQ公開日はいつ？\nQ2：P001のレビュー担当も高橋に変わる？\nQ3：AIが正しい表を作れたら、長期管理・共同編集にも十分と言える？", inline=False)
    embed.add_field(name="チェックの答え", value="||A1：未定。A2：山本のまま。A3：まだ判断できません。情報が増えた場合の検索・更新・履歴・共有を検証する必要があります。||", inline=False)
    embed.add_field(name="比較評価の記録", value="AIのみについて、初期構築・更新・検索・情報の一貫性を各1～5点で自己評価し、時間・誤り・理由も記録。共同作業と費用・保守、NotionとSheetsは未検証なら未評価にします。6項目が揃った場合の満点は30点です。", inline=False)
    embed.set_footer(text="今回の成果を保存して、第2回の情報増加の実験につなげます。自動採点・進捗保存は行いません。")
    return embed
