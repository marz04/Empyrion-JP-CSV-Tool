# Empyrion CSV Translation Tool

Empyrion - Galactic Survival のローカライゼーションCSVファイルを日本語化するためのツールです。

## このツールについて

ゲーム本体のバージョンアップに伴い、ローカライゼーションCSVの項目が増えた場合などに、
過去バージョンの翻訳ファイルから翻訳済み部分をマージしたCSVを作成します。

翻訳作業の際に、「過去の翻訳済み情報を最新バージョンのCSVに反映させて残りの部分だけ翻訳すればよい状態にする」という目的で作成しました。

未翻訳部分をGoogle翻訳で自動翻訳する機能も搭載しており、
「機械翻訳でいいからサッと翻訳して最新バージョンで使いたい」という場合にも使えるかと思います。
ですが、あくまで機械翻訳となるので、翻訳精度には期待できません。
また、ゲーム内で使用されるタグなどが上手く解釈できずにおかしな翻訳になる可能性もあります。


## 主な機能

- 既存の翻訳CSVファイルと新しいバージョンのCSVファイルをマージ
- 未翻訳部分の自動翻訳（オプション、Google翻訳使用）
- ゲーム内のタグ構造（`<color=#ffffff>text</color>`、`[b]text[/b]`など）を保持
- プレースホルダー変数（`{variable}`）を保護
- 翻訳エラーが発生した行を別ファイルに抽出

## ダウンロード
https://github.com/marz04/Empyrion-JP-CSV-Tool/releases/tag/v1.0

### 配布パッケージ（推奨）

`distribution/` フォルダに配布用のパッケージが含まれています：
- `Empyrion CSV Tool.exe` - Windows実行ファイル（Pythonインストール不要）
- `1_Original/` - 現行バージョンのCSVファイルを配置するフォルダ
- `2_Translated/` - 翻訳済みファイルを配置するフォルダ
- `readme.txt` - 使い方

### 開発者向け

Pythonスクリプトから実行する場合：
- [src/empyrion_csv_tool.py](src/empyrion_csv_tool.py)

## 使い方

### 1. CSVファイルの準備

#### 1_Original フォルダ
Empyrionのインストールフォルダから現行バージョンのCSVファイルをコピー：
```
Content\Configuration\Dialogues.csv
Content\Extras\Localization.csv
Content\Extras\PDA\PDA.csv
```

#### 2_Translated フォルダ
前バージョンなど、既に翻訳済みのCSVファイルを配置  
※同名のファイルがあれば自動的にマージされます

### 2. ツールの実行

1. `Empyrion CSV Tool.exe` をダブルクリックして起動
2. 自動翻訳の設定
   - ☑ 自動翻訳する → 未翻訳部分を機械翻訳で埋める
   - ☐ 自動翻訳する → マージのみ行い、未翻訳部分は空のまま
3. 「実行」ボタンをクリック
4. 完成したファイルは `3_Result/` に出力されます
5. 翻訳エラーがあった場合は `4_Error/` に出力されます

**推奨:** 精度の高い翻訳が必要な場合は、自動翻訳のチェックを外して、マージのみを行い、残りを手動で翻訳してください。

**注意:** Windows Defender SmartScreenの警告が表示された場合は、「詳細情報」→「実行」をクリックしてください。

### Pythonスクリプト版

#### 必要な環境
- Python 3.10.x（推奨）または 3.9.x
- pip

#### インストール

```bash
# リポジトリをクローン
git clone https://github.com/yourusername/empiryon_jp.git
cd empiryon_jp

# 依存パッケージをインストール
pip install -r requirements.txt
```

#### 実行

```bash
# GUI版を起動
python src/empyrion_csv_tool.py
```

## フォルダ構成

実行時のフォルダ構成：

```
作業フォルダ/
├─ Empyrion CSV Tool.exe
├─ 1_Original/       # 現行バージョンのCSVファイルを配置
│   ├─ Dialogues.csv      (Content\Configuration\Dialogues.csv)
│   ├─ Localization.csv   (Content\Extras\Localization.csv)
│   └─ PDA.csv            (Content\Extras\PDA\PDA.csv)
├─ 2_Translated/     # 翻訳済みファイルを配置（前バージョン等）
│   ├─ Dialogues.csv
│   ├─ Localization.csv
│   └─ PDA.csv
├─ 3_Result/         # 出力先（自動作成）
└─ 4_Error/          # 翻訳エラー行の出力先（自動作成）
```

## CSVファイルの形式

### 必須列
- `KEY`: 各行を識別するキー
- `English`: 英語の原文
- `Japanese`: 日本語訳（空の場合に翻訳・マージされます）

## 処理の流れ

1. `1_Original` フォルダの各CSVファイルをベースとする
2. `Japanese` 列が空白の行について、`2_Translated` 内の同名CSVから `KEY` で紐付けた `Japanese` をコピー（マージ）
3. `2_Translated` にもデータがない場合、かつ自動翻訳がONの場合は `googletrans` で翻訳
4. 完成したファイルを `3_Result` フォルダに保存
5. 翻訳エラーが発生した行を `4_Error` フォルダに保存

## 翻訳の仕様

### タグの保持

ゲーム内で特殊なタグとして使用される部分はそのまま保持し、テキストのみを翻訳します：

- `<color=#ffffff>text</color>` → `<color=#ffffff>テキスト</color>`
- `[b][c][ff0000]Important!![-][/c][/b]` → `[b][c][ff0000]重要!![-][/c][/b]`
- `{variable}` → `{variable}`（変数はそのまま）

### 制限事項

- `googletrans` は非公式APIのため、大量に使用すると一時的に制限がかかる場合があります
- レート制限対策として、各翻訳の間に0.5秒の待機時間を設けています

## 開発者向け

### exeファイルのビルド

Windows環境で：

```bash
# 必要なパッケージをインストール
pip install pyinstaller googletrans==4.0.0rc1

# exeファイルをビルド
pyinstaller --onefile --windowed --noupx --name="Empyrion CSV Tool" src/empyrion_csv_tool.py
```

※Python 3.10.x でのビルドで動作確認しています。
それ移行のバージョンでは上手く動作しない可能性があります。

## ライセンス

MIT License

## 制作

**marz04**

- GitHub: [marz04](https://github.com/marz04/Empyrion-JP-CSV-Tool)
- Twitter: [@marz04](https://x.com/marz04)
- Email: marz@marz04.net

## 謝辞

このツールは Empyrion - Galactic Survival の日本語化プロジェクトのために開発されました。
