cwlVersion: v1.2
class: Workflow

requirements:
  SubworkflowFeatureRequirement: {}
  ScatterFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  MultipleInputFeatureRequirement: {}

inputs:
  msg1: string
  msg2: string

outputs:
  new_file:
    type: string
    outputSource: uppercase/uppercase_message

steps:
  echo1:
    run: echo_string.cwl
    in:
      message: msg1
    out: [message_string]
  echo2:
    run: echo_string.cwl
    in:
      message: msg2
    out: [message_string]
  uppercase:
    run: uppercase2_wic_compatible3.cwl
    in:
      - id: message
        source: [echo1/message_string, echo2/message_string]
        pickValue: first_non_null
    out: [uppercase_message]
