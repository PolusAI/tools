class: Workflow
cwlVersion: v1.2
id: file:///Users/antoinegerardin/Documents/projects/polus-tools/multi-input.cwl
inputs:
- id: multi-input___0__echo1___message
  type: string
- id: multi-input___1__echo2___message
  type: string
outputs:
- id: multi-input___0__echo1___message_string
  outputSource: 0__echo1/message_string
  type: string
- id: multi-input___1__echo2___message_string
  outputSource: 1__echo2/message_string
  type: string
- id: multi-input___2__step__uppercase2_wic_compatible3___uppercase_message
  outputSource: 2__step__uppercase2_wic_compatible3/uppercase_message
  type: string[]
requirements:
- class: ScatterFeatureRequirement
steps:
- id: 0__echo1
  in:
  - id: message
    source: multi-input___0__echo1___message
  out:
  - message_string
  run: file:///Users/antoinegerardin/Documents/projects/polus-tools/tests/workflows/test_data/echo_string.cwl
- id: 1__echo2
  in:
  - id: message
    source: multi-input___1__echo2___message
  out:
  - message_string
  run: file:///Users/antoinegerardin/Documents/projects/polus-tools/tests/workflows/test_data/echo_string.cwl
- id: 2__step__uppercase2_wic_compatible3
  in:
  - id: message
    source:
    - 0__echo1/message_string
    - 1__echo2/message_string
  out:
  - uppercase_message
  run: file:///Users/antoinegerardin/Documents/projects/polus-tools/tests/workflows/test_data/uppercase2_wic_compatible3.cwl
  scatter:
  - message
