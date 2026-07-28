import sys, os
sys.path.insert(0, '.')
sys.path.insert(0, 'workflows/schema')

from validate_workflow import validate_workflow

print('=== FINAL VERIFICATION ===')
print()

# 1. Check all key files exist
files = [
    'form_filler.py', 'workflow_manager.py', 'workflow_engine.py',
    'handlers/__init__.py', 'handlers/base_handler.py',
    'handlers/input_handler.py', 'handlers/select_handler.py',
    'handlers/checkbox_handler.py', 'handlers/autocomplete_handler.py',
    'handlers/datepicker_handler.py', 'handlers/popup_search_handler.py',
    'handlers/file_upload_handler.py',
    'workflows/schema/workflow-schema.json',
    'workflows/csms_create_proposal/workflow.json',
    'workflows/gracubuy_create_gr/workflow.json',
    'tests/csms_regression.py', 'tests/test_integration.py',
    'workflows/settings.json',
    'README.md', 'workflows/README.md',
    chr(25191)+chr(34892)+chr(25171)+chr(21253)+'.bat',
    chr(37325)+chr(26032)+chr(25171)+chr(21253)+'.bat'
]
all_exist = True
for f in files:
    exists = os.path.exists(f)
    if not exists:
        all_exist = False
print('1. Key files: ' + ('ALL PRESENT' if all_exist else 'SOME MISSING'))

# 2. Validate workflow configs
schema = 'workflows/schema/workflow-schema.json'
for name, path in [('CSMS', 'workflows/csms_create_proposal/workflow.json'),
                   ('Acubuy', 'workflows/gracubuy_create_gr/workflow.json')]:
    v, e = validate_workflow(path, schema)
    status = 'VALID' if v else 'INVALID'
    print('2. ' + name + ': ' + status)

# 3. Verify imports
from workflow_manager import WorkflowManager
from workflow_engine import WorkflowEngine
from handlers import list_handler_types, get_handler
types = list_handler_types()
print('3. Imports: OK (' + str(len(types)) + ' handlers)')

# 4. Verify handlers are real
import inspect
all_real = True
for t in types:
    cls = get_handler(t)
    source = inspect.getsource(cls.execute)
    if 'TODO' in source:
        print('  STUB: ' + t)
        all_real = False
print('4. Handlers: ' + ('ALL REAL' if all_real else 'SOME STUBS'))

# 5. Verify WorkflowManager
wm = WorkflowManager()
workflows = wm.list_workflows()
names = [w['name'] for w in workflows]
print('5. Workflow discovery: ' + str(len(workflows)) + ' workflow(s): ' + str(names))

print()
print('=== VERIFICATION COMPLETE ===')
