#!/usr/bin/env python3
"""
Empyrion CSV Tool GUI版

処理フロー:
1. 1_Originalフォルダの各CSVファイルをベースとする
2. Japaneseの列が空白の場合、2_Translated内の同名CSVから「KEY」で紐付けた「Japanese」をコピー
3. 2_Translated内にもデータがない場合は、googletransで翻訳して埋める
4. 完成したファイルを3_Resultフォルダに保存
"""

import csv
import os
import re
import time
import sys
import threading
from pathlib import Path
from googletrans import Translator
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

# ディレクトリ設定（PyInstaller対応）
if getattr(sys, 'frozen', False):
    # PyInstallerでexe化された場合
    BASE_DIR = Path(sys.executable).parent
else:
    # 通常のPythonスクリプトとして実行された場合
    BASE_DIR = Path(__file__).parent

ORIGINAL_DIR = BASE_DIR / '1_Original'
TRANSLATED_DIR = BASE_DIR / '2_Translated'
RESULT_DIR = BASE_DIR / '3_Result'
ERROR_DIR = BASE_DIR / '4_Error'

translator = Translator()

def translate_with_structure(text):
    """
    タグ構造を保持しながらテキストのみ翻訳
    
    Args:
        text: 翻訳対象のテキスト
    
    Returns:
        翻訳後のテキスト
    """
    if text is None or not str(text).strip():
        return ''
    
    text = str(text)
    
    # プレースホルダー変数を一時保護
    placeholder_pattern = r'(\{[^}]+\})'
    placeholders = re.findall(placeholder_pattern, text)
    protected_text = re.sub(placeholder_pattern, '{{PLACEHOLDER}}', text)
    
    # タグパターンを検出して一時置換
    tag_patterns = [
        (r'<color=[^>]+>', '</color>'),
        (r'\[b\]\[c\]\[[^\]]+\]', r'\[\-\]\[/c\]\[/b\]'),
        (r'\[c\]\[[^\]]+\]', r'\[\-\]\[/c\]'),
        (r'\[b\]', r'\[/b\]'),
        (r'\[u\]', r'\[/u\]'),
        (r'\[i\]', r'\[/i\]'),
        (r'\[sup\]', r'\[/sup\]'),
    ]
    
    # タグで区切られたセグメントを抽出
    segments = []
    temp_text = protected_text
    segment_id = 0
    
    # タグ付きセグメントを抽出
    tag_full_patterns = [
        r'<color=[^>]+>.*?</color>',
        r'\[b\]\[c\]\[[^\]]+\].*?\[\-\]\[/c\]\[/b\]',
        r'\[c\]\[[^\]]+\].*?\[\-\]\[/c\]',
        r'\[b\].*?\[/b\]',
        r'\[u\].*?\[/u\]',
        r'\[i\].*?\[/i\]',
        r'\[sup\].*?\[/sup\]',
    ]
    
    # タグ付きセグメントを抽出
    for pattern in tag_full_patterns:
        for match in re.finditer(pattern, temp_text, re.DOTALL):
            marker = f'__TAG_SEGMENT_{segment_id}__'
            segments.append((marker, match.group(0)))
            temp_text = temp_text.replace(match.group(0), marker, 1)
            segment_id += 1
    
    # 残りのテキストを翻訳
    try:
        if temp_text.strip() and temp_text != protected_text:
            translated_text = translator.translate(temp_text, src='en', dest='ja').text
        else:
            translated_text = temp_text
            
        # セグメント内のテキストを翻訳
        for marker, original_segment in segments:
            # タグ内のテキストのみを抽出
            inner_text = original_segment
            for pattern in tag_full_patterns:
                match = re.match(pattern, original_segment, re.DOTALL)
                if match:
                    # タグの開始と終了を検出
                    if '<color=' in original_segment:
                        inner_match = re.search(r'<color=[^>]+>(.+?)</color>', original_segment, re.DOTALL)
                        if inner_match:
                            inner = inner_match.group(1)
                            translated_inner = translator.translate(inner, src='en', dest='ja').text
                            translated_segment = original_segment.replace(inner, translated_inner)
                            translated_text = translated_text.replace(marker, translated_segment, 1)
                            break
                    elif '[b][c][' in original_segment:
                        inner_match = re.search(r'\[b\]\[c\]\[[^\]]+\](.+?)\[\-\]\[/c\]\[/b\]', original_segment, re.DOTALL)
                        if inner_match:
                            inner = inner_match.group(1)
                            translated_inner = translator.translate(inner, src='en', dest='ja').text
                            translated_segment = original_segment.replace(inner, translated_inner)
                            translated_text = translated_text.replace(marker, translated_segment, 1)
                            break
                    elif '[c][' in original_segment:
                        inner_match = re.search(r'\[c\]\[[^\]]+\](.+?)\[\-\]\[/c\]', original_segment, re.DOTALL)
                        if inner_match:
                            inner = inner_match.group(1)
                            translated_inner = translator.translate(inner, src='en', dest='ja').text
                            translated_segment = original_segment.replace(inner, translated_inner)
                            translated_text = translated_text.replace(marker, translated_segment, 1)
                            break
                    elif '[b]' in original_segment:
                        inner_match = re.search(r'\[b\](.+?)\[/b\]', original_segment, re.DOTALL)
                        if inner_match:
                            inner = inner_match.group(1)
                            translated_inner = translator.translate(inner, src='en', dest='ja').text
                            translated_segment = original_segment.replace(inner, translated_inner)
                            translated_text = translated_text.replace(marker, translated_segment, 1)
                            break
                    elif '[u]' in original_segment:
                        inner_match = re.search(r'\[u\](.+?)\[/u\]', original_segment, re.DOTALL)
                        if inner_match:
                            inner = inner_match.group(1)
                            translated_inner = translator.translate(inner, src='en', dest='ja').text
                            translated_segment = original_segment.replace(inner, translated_inner)
                            translated_text = translated_text.replace(marker, translated_segment, 1)
                            break
                    elif '[i]' in original_segment:
                        inner_match = re.search(r'\[i\](.+?)\[/i\]', original_segment, re.DOTALL)
                        if inner_match:
                            inner = inner_match.group(1)
                            translated_inner = translator.translate(inner, src='en', dest='ja').text
                            translated_segment = original_segment.replace(inner, translated_inner)
                            translated_text = translated_text.replace(marker, translated_segment, 1)
                            break
                    elif '[sup]' in original_segment:
                        inner_match = re.search(r'\[sup\](.+?)\[/sup\]', original_segment, re.DOTALL)
                        if inner_match:
                            inner = inner_match.group(1)
                            translated_inner = translator.translate(inner, src='en', dest='ja').text
                            translated_segment = original_segment.replace(inner, translated_inner)
                            translated_text = translated_text.replace(marker, translated_segment, 1)
                            break
            else:
                # マッチしなかった場合はそのまま
                translated_text = translated_text.replace(marker, original_segment, 1)
        
        # プレースホルダーを復元
        for placeholder in placeholders:
            translated_text = translated_text.replace('{{PLACEHOLDER}}', placeholder, 1)
        
        return translated_text
    
    except Exception as e:
        raise e

def process_csv_file(original_file, translated_file, output_file, error_file, auto_translate, log_callback):
    """
    CSVファイルを処理（翻訳・マージ）
    
    Args:
        original_file: 1_Originalのファイルパス
        translated_file: 2_Translatedのファイルパス
        output_file: 3_Result出力先パス
        error_file: 4_Errorエラー行出力先パス
        auto_translate: 自動翻訳を行うかどうか
        log_callback: ログ出力用コールバック関数
    """
    log_callback(f"処理開始: {original_file.name}\n")
    
    # 2_TranslatedからKEY -> Japanese マッピングを読み込み
    japanese_dict = {}
    if translated_file.exists():
        try:
            with open(translated_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'KEY' in row and 'Japanese' in row:
                        key = row['KEY']
                        japanese = row.get('Japanese', '')
                        if japanese and japanese.strip():
                            japanese_dict[key] = japanese
            log_callback(f"  既存翻訳データ: {len(japanese_dict)}件\n")
        except Exception as e:
            log_callback(f"  既存翻訳ファイル読込エラー: {e}\n")
    else:
        log_callback(f"  既存翻訳ファイルなし\n")
    
    # 1_Originalファイルを読み込んで処理
    rows = []
    error_rows = []
    merged_count = 0
    translated_count = 0
    error_count = 0
    
    with open(original_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        
        if 'KEY' not in fieldnames or 'Japanese' not in fieldnames:
            log_callback(f"  エラー: KEYまたはJapanese列が見つかりません\n")
            return
        
        for i, row in enumerate(reader, 1):
            key = row.get('KEY', '')
            japanese = row.get('Japanese', '')
            
            # Japanese列が空の場合
            if not japanese or not japanese.strip():
                # 2_Translatedから取得を試みる
                if key in japanese_dict:
                    row['Japanese'] = japanese_dict[key]
                    merged_count += 1
                elif auto_translate:
                    # 翻訳を実行
                    english = row.get('English', '')
                    if english and english.strip():
                        try:
                            translated_text = translate_with_structure(english)
                            if translated_text and translated_text.strip():
                                row['Japanese'] = translated_text
                                translated_count += 1
                                log_callback(f"  {i}行目 (KEY: {key}): 翻訳完了\n")
                            else:
                                # 翻訳結果が空の場合はエラーとして扱う
                                row['Japanese'] = ''
                                error_rows.append(row.copy())
                                error_count += 1
                                log_callback(f"  {i}行目 (KEY: {key}): 翻訳結果が空\n")
                            time.sleep(0.5)  # レート制限対策
                        except Exception as e:
                            log_callback(f"  {i}行目 (KEY: {key}): 翻訳失敗 - {e}\n")
                            row['Japanese'] = ''
                            error_rows.append(row.copy())
                            error_count += 1
                    else:
                        log_callback(f"  {i}行目 (KEY: {key}): 英語テキストなし、スキップ\n")
            
            rows.append(row)
    
    # 結果を出力
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    # エラー行を出力
    if error_rows:
        with open(error_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(error_rows)
        log_callback(f"  エラー行を出力: {error_file}\n")
    
    log_callback(f"  処理完了:\n")
    log_callback(f"    - 総行数: {len(rows)}\n")
    log_callback(f"    - 既存翻訳マージ: {merged_count}件\n")
    log_callback(f"    - 新規翻訳: {translated_count}件\n")
    log_callback(f"    - 翻訳エラー: {error_count}件\n")
    log_callback(f"  出力: {output_file}\n\n")

class TranslationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Empyrion CSV Tool")
        self.root.geometry("800x600")
        
        # 自動翻訳チェックボックス
        self.auto_translate_var = tk.BooleanVar(value=True)
        self.check_frame = ttk.Frame(root, padding="10")
        self.check_frame.pack(fill=tk.X)
        
        self.auto_translate_check = ttk.Checkbutton(
            self.check_frame,
            text="自動翻訳する（googletrans使用）",
            variable=self.auto_translate_var
        )
        self.auto_translate_check.pack(side=tk.LEFT)
        
        # ボタンフレーム
        self.button_frame = ttk.Frame(root, padding="10")
        self.button_frame.pack(fill=tk.X)
        
        self.execute_button = ttk.Button(
            self.button_frame,
            text="実行",
            command=self.execute_processing
        )
        self.execute_button.pack(side=tk.LEFT, padx=5)
        
        self.exit_button = ttk.Button(
            self.button_frame,
            text="終了",
            command=self.root.quit
        )
        self.exit_button.pack(side=tk.LEFT, padx=5)
        
        # ログ表示エリア
        self.log_frame = ttk.Frame(root, padding="10")
        self.log_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(self.log_frame, text="実行ログ:").pack(anchor=tk.W)
        
        self.log_text = scrolledtext.ScrolledText(
            self.log_frame,
            wrap=tk.WORD,
            width=90,
            height=30
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 初期メッセージ
        self.log("Empyrion CSV Toolを起動しました。\n")
        self.log(f"作業ディレクトリ: {BASE_DIR}\n")
        self.log("「実行」ボタンを押して処理を開始してください。\n\n")
        
        # 処理中フラグ
        self.is_processing = False
    
    def log(self, message):
        """ログテキストエリアにメッセージを追加"""
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)
        self.log_text.update()
    
    def execute_processing(self):
        """処理実行"""
        if self.is_processing:
            messagebox.showwarning("警告", "処理中です。完了までお待ちください。")
            return
        
        # ディレクトリ確認
        if not ORIGINAL_DIR.exists():
            messagebox.showerror("エラー", f"{ORIGINAL_DIR} が存在しません。")
            return
        
        csv_files = list(ORIGINAL_DIR.glob('*.csv'))
        if not csv_files:
            messagebox.showerror("エラー", f"{ORIGINAL_DIR} にCSVファイルが見つかりません。")
            return
        
        # 別スレッドで処理実行
        thread = threading.Thread(target=self._run_processing, args=(csv_files,))
        thread.daemon = True
        thread.start()
    
    def _run_processing(self, csv_files):
        """処理実行（別スレッド）"""
        self.is_processing = True
        self.execute_button.config(state=tk.DISABLED)
        
        try:
            # ディレクトリ作成
            RESULT_DIR.mkdir(exist_ok=True)
            ERROR_DIR.mkdir(exist_ok=True)
            
            auto_translate = self.auto_translate_var.get()
            
            self.log(f"処理対象: {len(csv_files)}ファイル\n")
            self.log("=" * 60 + "\n\n")
            
            for original_file in csv_files:
                filename = original_file.name
                translated_file = TRANSLATED_DIR / filename
                output_file = RESULT_DIR / filename
                error_file = ERROR_DIR / filename
                
                try:
                    process_csv_file(
                        original_file,
                        translated_file,
                        output_file,
                        error_file,
                        auto_translate,
                        self.log
                    )
                except Exception as e:
                    self.log(f"エラー ({filename}): {e}\n")
                    continue
            
            self.log("=" * 60 + "\n")
            self.log("全処理完了!\n")
            messagebox.showinfo("完了", "処理が完了しました。")
        
        except Exception as e:
            self.log(f"エラー: {e}\n")
            messagebox.showerror("エラー", f"処理中にエラーが発生しました:\n{e}")
        
        finally:
            self.is_processing = False
            self.execute_button.config(state=tk.NORMAL)

def main():
    """メイン処理"""
    root = tk.Tk()
    app = TranslationApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
