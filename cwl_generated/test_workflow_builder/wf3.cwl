class: Workflow
cwlVersion: v1.2
id: file:///Users/antoinegerardin/Documents/projects/polus-tools/cwl_generated/test_workflow_builder/wf3.cwl
inputs:
- id: wf3___0__step__echo_string___message
  type: string
outputs:
- id: wf3___0__step__echo_string___message_string
  outputSource: 0__step__echo_string/message_string
  type: string
- id: wf3___1__step__uppercase2_wic_compatible2___uppercase_message
  outputSource: 1__step__uppercase2_wic_compatible2/uppercase_message
  type: string
requirements: []
steps:
- id: 0__step__echo_string
  in:
  - id: message
    source: wf3___0__step__echo_string___message
  out:
  - message_string
  run: file:///Users/antoinegerardin/Documents/projects/polus-tools/tests/workflows/test_data/echo_string.cwl
- id: 1__step__uppercase2_wic_compatible2
  in:
  - id: message
    source: 0__step__echo_string/message_string
  - id: uppercase_message
    source: 0__step__echo_string/message_string
  out:
  - uppercase_message
  run: file:///Users/antoinegerardin/Documents/projects/polus-tools/tests/workflows/test_data/uppercase2_wic_compatible2.cwl
