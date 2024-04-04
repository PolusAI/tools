class: Workflow
cwlVersion: v1.2
id: file:///Users/antoinegerardin/Documents/projects/polus-tools/tests/workflows/test_data/subworkflow1.cwl
inputs:
- id: msg
  type: string
outputs:
- id: new_file
  outputSource: touch/output
  type: File
requirements:
- class: SubworkflowFeatureRequirement
steps:
- id: echo-uppercase-wf
  in:
  - id: msg
    source: msg
  out:
  - uppercase_message
  run: file:///Users/antoinegerardin/Documents/projects/polus-tools/tests/workflows/test_data/workflow3.cwl
- id: touch
  in:
  - id: touchfiles
    source: echo-uppercase-wf/uppercase_message
  out:
  - output
  run: file:///Users/antoinegerardin/Documents/projects/polus-tools/tests/workflows/test_data/touch_single.cwl
