import re

def filter_python(txt):
    print("Filtering Python code")
    pattern = r"```python(.*?)```"
    matches = re.findall(pattern, txt, re.DOTALL)
    pattern = r"```(.*?)```"
    matches = re.findall(pattern, txt, re.DOTALL)
    if matches:
        python_code = matches[0].strip()
        return python_code
    else:
        return txt

def filter_json(txt):
    print("Filtering JSON code")
    pattern = r"```json(.*?)```"
    matches = re.findall(pattern, txt, re.DOTALL)
    pattern = r"```(.*?)```"
    matches = re.findall(pattern, txt, re.DOTALL)
    if matches:
        json_code = matches[0].strip()
        return json_code
    else:
        return txt
