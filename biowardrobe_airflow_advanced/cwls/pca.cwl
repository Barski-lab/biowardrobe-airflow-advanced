cwlVersion: v1.0
class: Workflow


inputs:

  expression_file:
    type: File[]
    label: "Array of CSV/TSV expression files"
    format:
     - "http://edamontology.org/format_3752"
     - "http://edamontology.org/format_3475"
    doc: "Array of CSV/TSV expression files"

  legend_name:
    type: string[]
    label: "Legend names"
    doc: |
      Array of names to make a legend.
      Order corresponds to the expression files

  output_prefix:
    type: string
    label: "Output file prefix"
    doc: "Prefix to generate names for output files"


outputs:

  png_file:
    type: File[]
    label: "Generated plots"
    format: "http://edamontology.org/format_3603"
    doc: "Exported to png generated plots"
    outputSource: pca/png_file

  pca_file:
    type: File
    label: "Generated pca data"
    format: "http://edamontology.org/format_3475"
    doc: "PCA data exported to TSV"
    outputSource: pca/pca_file

steps:

  pca:
    in:
      expression_file: expression_file
      legend_name: legend_name
      output_prefix: output_prefix
    out:
    - png_file
    - pca_file
    run:
      cwlVersion: v1.0
      class: CommandLineTool
      requirements:
      - class: DockerRequirement
        dockerPull: biowardrobe2/pca:v0.0.1
      inputs:
        expression_file:
          type: File[]
          inputBinding:
            position: 5
            prefix: "-i"
        legend_name:
          type: string[]
          inputBinding:
            position: 6
            prefix: "-n"
        output_prefix:
          type: string?
          inputBinding:
            position: 9
            prefix: "-o"
      outputs:
        png_file:
          type: File[]
          outputBinding:
            glob: "*.png"
        pca_file:
          type: File
          outputBinding:
            glob: "*pca.tsv"
      baseCommand: ["run_pca.R"]