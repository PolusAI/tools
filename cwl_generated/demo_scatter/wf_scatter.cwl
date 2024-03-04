class: Workflow
cwlVersion: v1.2
id: file:///Users/antoinegerardin/Documents/projects/polus-tools/cwl_generated/demo_scatter/wf_scatter.cwl
inputs:
- id: wf_scatter___0__step__echo_string___message
  type:
    items: string
    type: array
outputs:
- id: wf_scatter___0__step__echo_string___message_string
  outputSource: 0__step__echo_string/message_string
  type:
    items: string
    type: array
- id: wf_scatter___1__step__uppercase2_wic_compatible3___uppercase_message
  outputSource: 1__step__uppercase2_wic_compatible3/uppercase_message
  type:
    items: string
    type: array
requirements:
- class: ScatterFeatureRequirement
steps:
- id: 0__step__echo_string
  in:
  - id: message
    source: wf_scatter___0__step__echo_string___message
  out:
  - message_string
  run: file:///Users/antoinegerardin/Documents/projects/polus-tools/tests/workflows/test_data/echo_string.cwl
  scatter:
  - message
- id: 1__step__uppercase2_wic_compatible3
  in:
  - id: message
    source: 0__step__echo_string/message_string
  out:
  - uppercase_message
  run: file:///Users/antoinegerardin/Documents/projects/polus-tools/tests/workflows/test_data/uppercase2_wic_compatible3.cwl
  scatter:
  - message
