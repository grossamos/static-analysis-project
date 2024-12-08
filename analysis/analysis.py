import google.generativeai as genai
from google.generativeai.client import os
import sys
import re
import click



def files_to_string(dir_path: str) -> str:
  res = ""
  for root, _, files in os.walk(dir_path):
    for file in files:
      file_path = os.path.join(root, file)
      try:
        with open(file_path, 'r') as f:
          file_content = f.read()
          res += f"--- {file_path} ---\n{file_content}\n"
      except UnicodeDecodeError:
          continue
      except Exception:
          continue
  return res

def check_gemini(code: str, print_res: bool = False):
    all_files = ""
    all_files += files_to_string(code)

    prompt = "You are a very skilled android developer. Look at the provided code. Does the app (not android or google) allow for deletions of an account if it has one. If it has no account and it allows for deletions answer yes. If it doesn't say no. Preface this answer with 'DECISION:' and the reasoning with 'REASON:;"

    genai.configure(api_key=os.environ["GEMINI_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=prompt)
    count = model.count_tokens(all_files)

    if count.total_tokens >= 1000000:
        print(str(count.total_tokens) + " is too large. Please make it under 1m tokens")
        sys.exit(1)
    response = model.generate_content(all_files)

    if print_res: 
        print(response.text)

    match = re.search(r"(DECISION|Decision|decision|dec):\s*(Yes|No|yes|no)".lower(), response.text, re.IGNORECASE)
    if match:
        return match.group(2).capitalize()  == "yes"
    else:
        print("Invalid Gemini answer")
        print(response.text)
        sys.exit(1)


def check_for_string(filename: str, print_output: bool = False) -> int:
    count = 0
    command = f"strings {filename} | grep -i account | grep -i delet" # matches delete and deletion, etc
    stream = os.popen(command)

    for line in stream:
        count += 1
        if print_output:
            print(line, end="")

    command = f"strings {filename} | grep -i account | grep -i remov"
    stream = os.popen(command)

    for line in stream:
        count += 1
        if print_output:
            print(line, end="")

    if count > 10:
        count = 10

    return count


def check_dependencies(sources: str) -> int:
    dependencies = ["androidx/credential", "com/microsoft/identity", "net/openid/appauth", "com/google/firebase/firebase-auth"]
    for dep in dependencies:
        if os.path.exists(sources + dep) and os.path.isdir(sources + dep):
            return 1

    return 0

@click.command()
@click.argument('apk', type=str)
@click.argument('code', type=str)
@click.argument('source', type=str)
@click.option('--only-gemini', type=bool, help="only executes gemini component")
@click.option('--only-strings', type=bool, help="only executes strings component")
@click.option('--only-deps', type=bool, help="only executes dependencies component")
def main(apk: str, code: str, source: str, only_gemini: bool, only_strings: bool, only_deps: bool) :
    GEMINI_WEIGHT = 1 # expected 5
    STRING_WEIGHT = 0.7 # expected to be max 10
    DEP_WEIGHT = 3 # expected to be 1 or 0
    score = 0
    if only_gemini:
        check_gemini(code, True)
    elif only_strings:
        res = check_for_string(apk)
        print(res)
    elif only_deps:
        res = check_dependencies(source)
    else:
        if check_gemini(code):
            score += 5 * GEMINI_WEIGHT

        score += check_for_string(apk) * STRING_WEIGHT
        score += check_dependencies(source) * DEP_WEIGHT

    if score >= 5:
        print(f"Has account deletion (score: {score})")
    else:
        print(f"Doesn't have account deletion (score: {score})")

if __name__ == '__main__':
    main()

