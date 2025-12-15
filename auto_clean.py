import re

def extract_python_code(llm_output: str) -> str:
    python_block = re.search(
        r"```python\s*(.*?)```",
        llm_output,
        re.DOTALL | re.IGNORECASE
    )
    if python_block:
        return python_block.group(1).strip()

    generic_block = re.search(
        r"```\s*(.*?)```",
        llm_output,
        re.DOTALL
    )
    if generic_block:
        return generic_block.group(1).strip()

    return llm_output.strip()
