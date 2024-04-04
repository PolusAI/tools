cwlVersion: v1.2
class: Workflow

inputs:
  msg: string

outputs:
  uppercase_message:
    type: string
    outputSource: uppercase/uppercase_message

steps:
  echo:
    run:
      id: echo_string
      cwlVersion: v1.2
      class: CommandLineTool

      label: generate a cwl string

      doc: Take a user input and generate a cwl string for it.

      baseCommand: echo

      inputs:
        message:
          type: string
          inputBinding:
            position: 1

      stdout: message

      outputs:
        message_string:
          type: string
          outputBinding:
            glob: message
            loadContents: True
            outputEval: $(self[0].contents)
    in:
      message: msg
    out: [message_string]

  uppercase:
    run: uppercase2_wic_compatible3.cwl
    in:
      message: echo/message_string
    out: [uppercase_message]
