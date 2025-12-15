import subprocess
import tempfile
import sys
import re

MAX_RETRIES = 3
MODEL = "wizardlm2"


def extract_python_code(text):
    match = re.search(r"```python\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()

    match = re.search(r"```\s*(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()

    return text.strip()


def ollama_chat(prompt):
    result = subprocess.run(
        ["ollama", "run", MODEL],
        input=prompt.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.decode("utf-8", errors="ignore")


def runs_without_error(code):
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
            f.write(code)
            temp_file = f.name

        result = subprocess.run(
            [sys.executable, temp_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
        )

        if result.returncode == 0:
            return True
        else:
            print("Runtime error:")
            print(result.stderr.decode())
            return False
    except Exception as e:
        print("Execution failed:", e)
        return False


def fix_code_agent(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        original_code = f.read()

    for attempt in range(1, MAX_RETRIES + 1):
        print("Attempt", attempt)

        prompt = (
            "You are a Python code fixer.\n"
            "Rules:\n"
            "- Output ONLY corrected Python code\n"
            "- No explanations\n"
            "- No comments\n\n"
            "Code:\n"
            "```python\n"
            + original_code +
            "\n```"
        )

        raw_output = ollama_chat(prompt)
        clean_code = extract_python_code(raw_output)

        if runs_without_error(clean_code):
            output_file = file_path.replace(".py", "_fixed.py")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(clean_code)
            print("Fixed file saved as:", output_file)
            return
        else:
            print("Retrying...\n")

    print("Failed after multiple attempts.")


if __name__ == "__main__":
    fix_code_agent("example4.py") # Here, add the sample file you want to test

