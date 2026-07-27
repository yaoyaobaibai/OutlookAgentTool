import sys
sys.path.insert(0, 'workflows/schema')
from validate_workflow import validate_workflow

schema_path = 'workflows/schema/workflow-schema.json'

# Validate both workflow configs
configs = [
    'workflows/csms_create_proposal/workflow.json',
    'workflows/gracubuy_create_gr/workflow.json'
]

all_valid = True
for wf in configs:
    valid, errors = validate_workflow(wf, schema_path)
    status = 'VALID' if valid else 'INVALID'
    print(f'{wf}: {status}')
    if not valid:
        all_valid = False
        for e in errors:
            print(f'  - {e}')

# Verify GUI syntax
import ast
with open('form_filler.py', 'r', encoding='utf-8-sig') as f:
    source = f.read()
ast.parse(source)
lines = source.count('\n')
print(f'\nform_filler.py: OK ({lines} lines)')

# Verify imports
from workflow_manager import WorkflowManager, WorkflowInfo
from workflow_engine import WorkflowEngine
from handlers import list_handler_types
print(f'WorkflowManager: OK')
print(f'WorkflowEngine: OK')
print(f'Handlers ({len(list_handler_types())}): {list_handler_types()}')

print(f'\nALL VERIFICATIONS: PASSED' if all_valid else '\nSOME VALIDATIONS FAILED')
