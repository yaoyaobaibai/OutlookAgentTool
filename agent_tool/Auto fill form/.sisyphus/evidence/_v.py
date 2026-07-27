import sys
sys.path.insert(0, 'workflows/schema')
from validate_workflow import validate_workflow
for wf in ['workflows/csms_create_proposal/workflow.json', 'workflows/gracubuy_create_gr/workflow.json']:
    v, e = validate_workflow(wf, 'workflows/schema/workflow-schema.json')
    print(f'{wf}: {"VALID" if v else "INVALID"}')
    if not v:
        for err in e:
            print(f'  - {err}')
print('Done.')
