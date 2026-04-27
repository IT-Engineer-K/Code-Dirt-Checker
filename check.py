import sys
import os
import collections

def check_redundancy(filepath, min_lines=4):
    """
    指定されたファイルのコードの冗長性（重複ブロック）をチェックします。
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"エラー: {e}")
        return

    # 実質的なコード行（空行やコメント行を除外）とその元の行番号を取得
    # 簡単のため、行頭が '#' の行も除外対象とします
    valid_lines = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped and not stripped.startswith('#'):
            valid_lines.append((i + 1, stripped))

    if len(valid_lines) < min_lines:
        print("ファイルが短すぎるか、有効なコード行が少なすぎます。")
        return

    # n行の連続したパターンのハッシュと、その出現位置（行番号）を記録
    blocks = collections.defaultdict(list)

    for i in range(len(valid_lines) - min_lines + 1):
        window = valid_lines[i:i + min_lines]
        block_text = tuple(line for _, line in window)
        start_line_num = window[0][0]
        blocks[block_text].append(start_line_num)

    # 2回以上出現するブロックを重複とみなす
    duplicates = {text: starts for text, starts in blocks.items() if len(starts) > 1}

    if not duplicates:
        print(f"{min_lines}行以上の重複コードは見つかりませんでした。冗長性は低そうです！")
        return

    print(f"=== コードの冗長性チェック結果 ===")
    print(f"連続する {min_lines} 行以上の同一（または類似）ブロックが複数見つかりました。\n")

    # 完全包含などの重複を取り下げる処理は省いていますが、結果をわかりやすく出力します
    count = 1
    for block_text, starts in duplicates.items():
        print(f"【重複パターン {count}】 出現開始行: {', '.join(f'{s}行目' for s in starts)}")
        print("-" * 40)
        for line in block_text:
            print(f"  {line}")
        print("-" * 40)
        print()
        count += 1

def process_target(target_path, min_lines):
    if os.path.isfile(target_path):
        check_redundancy(target_path, min_lines)
    elif os.path.isdir(target_path):
        for root, dirs, files in os.walk(target_path):
            # 検索対象外のディレクトリを除外
            for exclude in ['.git', '__pycache__', 'node_modules', 'venv', '.pytest_cache']:
                if exclude in dirs:
                    dirs.remove(exclude)
            for file in files:
                # 対象とするファイルの拡張子を絞り込み
                if file.endswith(('.py', '.txt', '.md', '.json', '.html', '.js', '.ts', '.css', '.java', '.c', '.cpp', '.h')):
                    file_path = os.path.join(root, file)
                    print(f"\n[{file_path}] のチェックを開始します...")
                    check_redundancy(file_path, min_lines)
    else:
        print(f"指定されたパスが見つかりません: {target_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使い方: python check.py <対象ファイルまたはディレクトリパス> [最小一致行数(デフォルト:4)]")
        print("例: python check.py sample")
    else:
        target_path = sys.argv[1]
        min_lines = int(sys.argv[2]) if len(sys.argv) > 2 else 4
        process_target(target_path, min_lines)
