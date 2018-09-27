cwlVersion: v1.0
class: Workflow


inputs:

  untreated_files:
    type:
      - File
      - File[]
    label: "Untreated input CSV files"
    format: "http://edamontology.org/format_3752"
    doc: "Untreated input CSV files"

  treated_files:
    type:
      - File
      - File[]
    label: "Treated input CSV files"
    format: "http://edamontology.org/format_3752"
    doc: "Treated input CSV files"

  output_filename:
    type: string
    label: "Output filename"
    doc: "Output filename"

  threads:
    type: int?
    label: "Number of threads"
    doc: "Number of threads for those steps that support multithreading"


outputs:

  diff_expr_file:
    type: File
    label: "DESeq resutls, TSV"
    format: "http://edamontology.org/format_3475"
    doc: "DESeq generated list of differentially expressed items grouped by isoforms, genes or common TSS"
    outputSource: deseq/diff_expr_file


steps:

  deseq:
    in:
      untreated_files: untreated_files
      treated_files: treated_files
      output_filename: output_filename
      threads: threads
    out: [diff_expr_file]
    run:
      cwlVersion: v1.0
      class: CommandLineTool
      requirements:
      - class: InlineJavascriptRequirement
      - class: DockerRequirement
        dockerPull: biowardrobe2/scidap-deseq:v0.0.1
      inputs:
        untreated_files:
          type:
            - File
            - File[]
          inputBinding:
            position: 5
            prefix: "-u"
          doc: "Untreated input CSV files"
        treated_files:
          type:
            - File
            - File[]
          inputBinding:
            position: 6
            prefix: "-t"
          doc: "Treated input CSV files"
        output_filename:
          type: string
          inputBinding:
            position: 7
            prefix: "-o"
          doc: "Output filename"
        threads:
          type: int?
          inputBinding:
            position: 9
            prefix: '-p'
          doc: "Run script using multiple threads"
      outputs:
        diff_expr_file:
          type: File
          outputBinding:
            glob: $(inputs.output_filename)
      baseCommand: [run_deseq.R]


