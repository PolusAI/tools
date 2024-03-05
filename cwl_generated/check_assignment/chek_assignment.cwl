class: Workflow
cwlVersion: v1.2
id: file:///Users/antoinegerardin/Documents/projects/polus-tools/cwl_generated/check_assignment/chek_assignment.cwl
inputs:
- id: chek_assignment___0__step__echo_string___message
  type: string
outputs:
- id: chek_assignment___0__step__echo_string___message_string
  outputSource: 0__step__echo_string/message_string
  type: string
- id: chek_assignment___1__step__uppercase2_wic_compatible2_optional___uppercase_message
  outputSource: 1__step__uppercase2_wic_compatible2_optional/uppercase_message
  type: string
requirements: []
steps:
- id: 0__step__echo_string
  in:
  - id: message
    source: chek_assignment___0__step__echo_string___message
  out:
  - message_string
  run: file:///Users/antoinegerardin/Documents/projects/polus-tools/tests/workflows/test_data/echo_string.cwl
- id: 1__step__uppercase2_wic_compatible2_optional
  in:
  - id: message
    source: 0__step__echo_string/message_string
  out:
  - uppercase_message
  run: file:///Users/antoinegerardin/Documents/projects/polus-tools/tests/workflows/test_data/uppercase2_wic_compatible2_optional.cwl
