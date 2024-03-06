class: Workflow
cwlVersion: v1.2
id: file:///Users/antoinegerardin/Documents/projects/polus-tools/tests/workflows/test_data/multi-inputs-workflow.cwl
inputs:
- id: msg1
  type: string
- id: msg2
  type: string
outputs:
- id: new_file
  outputSource: uppercase/uppercase_message
  type: string[]
requirements:
- class: InlineJavascriptRequirement
- class: MultipleInputFeatureRequirement
- class: ScatterFeatureRequirement
- class: SubworkflowFeatureRequirement
steps:
- id: echo1
  in:
  - id: message
    source: msg1
  out:
  - message_string
  run: file:///Users/antoinegerardin/Documents/projects/polus-tools/tests/workflows/test_data/echo_string.cwl
- id: echo2
  in:
  - id: message
    source: msg2
  out:
  - message_string
  run: file:///Users/antoinegerardin/Documents/projects/polus-tools/tests/workflows/test_data/echo_string.cwl
- id: uppercase
  in:
  - id: message
    source:
    - echo1/message_string
    - echo2/message_string
  out:
  - uppercase_message
  run: file:///Users/antoinegerardin/Documents/projects/polus-tools/tests/workflows/test_data/uppercase2_wic_compatible3.cwl
  scatter:
  - message
