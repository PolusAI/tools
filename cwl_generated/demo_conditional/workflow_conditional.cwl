class: Workflow
cwlVersion: v1.2
id: file:///Users/antoinegerardin/Documents/projects/polus-tools/cwl_generated/demo_conditional/workflow_conditional.cwl
inputs:
- id: workflow_conditional___0__step__workflow3___msg
  type: string
- id: workflow_conditional___1__step__touch_single___should_execute
  type: int
outputs:
- id: workflow_conditional___0__step__workflow3___uppercase_message
  outputSource: 0__step__workflow3/uppercase_message
  type: string
- id: workflow_conditional___1__step__touch_single___output
  outputSource: 1__step__touch_single/output
  type: File
requirements:
- class: SubworkflowFeatureRequirement
- class: InlineJavascriptRequirement
steps:
- id: 0__step__workflow3
  in:
  - id: msg
    source: workflow_conditional___0__step__workflow3___msg
  out:
  - uppercase_message
  run: file:///Users/antoinegerardin/Documents/projects/polus-tools/tests/workflows/test_data/workflow3.cwl
- id: 1__step__touch_single
  in:
  - id: touchfiles
    source: 0__step__workflow3/uppercase_message
  - id: should_execute
    source: workflow_conditional___1__step__touch_single___should_execute
  out:
  - output
  run: file:///Users/antoinegerardin/Documents/projects/polus-tools/tests/workflows/test_data/touch_single.cwl
  when: $(inputs.should_execute < 1)
