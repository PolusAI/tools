class: Workflow
cwlVersion: v1.2
id: file:///Users/antoinegerardin/Documents/projects/polus-tools/tests/workflows/test_data/scatter-workflow2.cwl
inputs:
- id: msg
  type: string[]
outputs:
- id: new_file
  outputSource: touch/output
  type: File[]
requirements:
- class: ScatterFeatureRequirement
steps:
- id: echo
  in:
  - id: message
    source: msg
  out:
  - message_string
  run: file:///Users/antoinegerardin/Documents/projects/polus-tools/tests/workflows/test_data/echo_string.cwl
  scatter:
  - message
- id: touch
  in:
  - id: touchfiles
    source: echo/message_string
  out:
  - output
  run: file:///Users/antoinegerardin/Documents/projects/polus-tools/tests/workflows/test_data/touch_single.cwl
  scatter:
  - touchfiles
