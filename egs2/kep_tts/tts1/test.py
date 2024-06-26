# # import os

# # def rename_to_lowercase(root_dir):
# #     for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
# #         for name in dirnames:
# #             lower_name = name.lower()
# #             if name != lower_name:
# #                 os.rename(
# #                     os.path.join(dirpath, name),
# #                     os.path.join(dirpath, lower_name)
# #                 )
# #         for name in filenames:
# #             lower_name = name.lower()
# #             if name != lower_name:
# #                 os.rename(
# #                     os.path.join(dirpath, name),
# #                     os.path.join(dirpath, lower_name)
# #                 )

# # if __name__ == "__main__":
# #     base_dir = '/home/ubuntu/Workspace/mul50'
# #     if not os.path.isdir(base_dir):
# #         print(f"The directory {base_dir} does not exist.")
# #     else:
# #         rename_to_lowercase(base_dir)
# #         print("All folder and file names have been converted to lowercase.")
# import os

# def convert_file_contents_to_lowercase(file_path):
#     try:
#         with open(file_path, 'r') as file:
#             content = file.read()
#         lower_content = content.lower()
#         with open(file_path, 'w') as file:
#             file.write(lower_content)
#     except Exception as e:
#         print(f"Error processing file {file_path}: {e}")

# def convert_directory_files_to_lowercase(root_dir):
#     for dirpath, _, filenames in os.walk(root_dir):
#         for filename in filenames:
#             if filename.endswith('.txt'):
#                 file_path = os.path.join(dirpath, filename)
#                 convert_file_contents_to_lowercase(file_path)

# if __name__ == "__main__":
#     base_dir = '/home/ubuntu/Workspace/mul50'
#     if not os.path.isdir(base_dir):
#         print(f"The directory {base_dir} does not exist.")
#     else:
#         convert_directory_files_to_lowercase(base_dir)
#         print("All file contents have been converted to lowercase.")
import os
import re

def remove_disallowed_whitespaces(file_path):
    # 유니코드 공백 문자 목록
    unicode_whitespace_chars = ''.join([
        '\u00A0',  # NO-BREAK SPACE
        '\u1680',  # OGHAM SPACE MARK
        '\u180E',  # MONGOLIAN VOWEL SEPARATOR
        '\u2000', '\u2001', '\u2002', '\u2003', '\u2004', '\u2005', '\u2006', '\u2007', '\u2008', '\u2009', '\u200A',  # EN QUAD, EM QUAD, EN SPACE, EM SPACE, THREE-PER-EM SPACE, FOUR-PER-EM SPACE, SIX-PER-EM SPACE, FIGURE SPACE, PUNCTUATION SPACE, THIN SPACE, HAIR SPACE
        '\u202F',  # NARROW NO-BREAK SPACE
        '\u205F',  # MEDIUM MATHEMATICAL SPACE
        '\u3000',  # IDEOGRAPHIC SPACE
        '\uFEFF'   # ZERO WIDTH NO-BREAK SPACE
    ])

    # 유니코드 공백 문자 패턴
    unicode_whitespace_pattern = f"[{re.escape(unicode_whitespace_chars)}]"

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # 허용되지 않는 유니코드 공백 문자를 일반 공백으로 대체
        cleaned_content = re.sub(unicode_whitespace_pattern, ' ', content)

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(cleaned_content)
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")

def process_directory(root_dir):
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename == 'text':  # 'text' 파일만 처리
                file_path = os.path.join(dirpath, filename)
                remove_disallowed_whitespaces(file_path)

if __name__ == "__main__":
    base_dir = '/home/ubuntu/Workspace/TTS/KEP_TTS/egs2/kep_tts/tts1/data'
    if not os.path.isdir(base_dir):
        print(f"The directory {base_dir} does not exist.")
    else:
        process_directory(base_dir)
        print("All disallowed whitespace characters have been replaced.")
