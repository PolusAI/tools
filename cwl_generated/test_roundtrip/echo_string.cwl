baseCommand: echo
class: CommandLineTool
cwlVersion: v1.2
doc: Take a user input and generate a cwl string for it.
id: file:///Users/antoinegerardin/Documents/projects/polus-tools/tests/workflows/test_data/echo_string.cwl
inputs:
- id: message
  inputBinding:
    position: 1
  type: string
label: generate a cwl string
outputs:
- id: message_string
  outputBinding:
    glob: message
    loadContents: true
    outputEval: $(self[0].contents)
  type: string
stdout: message
