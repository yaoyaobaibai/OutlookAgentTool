import marshal, os

build_dir = r"C:\Open AI Proj\agent_tool\outlook_agent\build\OutlookAgent"
for root, dirs, files in os.walk(build_dir):
    for f in files:
        if "attachment_handler" in f and f.endswith(".pyc"):
            path = os.path.join(root, f)
            with open(path, "rb") as fc:
                fc.read(16)
                code = marshal.load(fc)
            def find_string(co, target):
                for const in co.co_consts:
                    if isinstance(const, str) and target in const:
                        return True
                    if hasattr(const, "co_consts"):
                        if find_string(const, target):
                            return True
                return False
            print(f"DEBUG found: {find_string(code, 'DEBUG')}")
            print(f"Extracted found: {find_string(code, 'Extracted embedded')}")
            break
else:
    print("No pyc found")
