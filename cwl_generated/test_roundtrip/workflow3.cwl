class: Workflow
cwlVersion: v1.2
id: file:///Users/antoinegerardin/Documents/projects/polus-tools/tests/workflows/test_data/workflow3.cwl
inputs:
- id: msg
  type: string
outputs:
- id: uppercase_message
  outputSource: uppercase/uppercase_message
  type: string
steps:
- id: echo
  in:
  - id: message
    source: msg
  out:
  - message_string
  run: file:///Users/antoinegerardin/Documents/projects/polus-tools/tests/workflows/test_data/echo_string.cwl
- id: uppercase
  in:
  - id: message
    source: echo/message_string
  out:
  - uppercase_message
  run: file:///Users/antoinegerardin/Documents/projects/polus-tools/tests/workflows/test_data/uppercase2_wic_compatible3.cwl
