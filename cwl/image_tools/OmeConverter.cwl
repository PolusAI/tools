class: CommandLineTool
cwlVersion: v1.2
inputs:
  fileExtension:
    inputBinding:
      prefix: --fileExtension
    type: string
  filePattern:
    inputBinding:
      prefix: --filePattern
    type: string
  inpDir:
    inputBinding:
      prefix: --inpDir
    type: Directory
  outDir:
    inputBinding:
      prefix: --outDir
    type: Directory
outputs:
  outDir:
    outputBinding:
      glob: $(inputs.outDir.basename)
    type: Directory
requirements:
  DockerRequirement:
    dockerPull: polusai/ome-converter-plugin:0.3.0
  InitialWorkDirRequirement:
    listing:
    - entry: $(inputs.outDir)
      writable: true
  InlineJavascriptRequirement: {}
  NetworkAccess:
    networkAccess: true
#   EnvVarRequirement:
# # See https://www.commonwl.org/user_guide/topics/environment-variables.html
#     envDef:
#       HOME: /home/polusai
