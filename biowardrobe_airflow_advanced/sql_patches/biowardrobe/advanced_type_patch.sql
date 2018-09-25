# DESeq
INSERT IGNORE INTO `ems`.`advancedtype` SELECT NULL, 'deseq', '', '', '','';
UPDATE `ems`.`plugintype` SET
  workflow='deseq-biowardrobe-only.cwl',
  template='{{
    "untreated_files": {untreated_files},
    "treated_files": {treated_files},
    "output_filename": "{uid}_deseq.tsv",
    "threads": {threads},
    "output_folder": "{anl_data}/{uid}",
    "uid": "{uid}"
  }}',
  upload_rules='{{
      "upload_deseq": "{uid}_deseq.tsv"
  }}',
  job_dispatcher='BioWardrobeDeseqJobDispatcher',
  job_gatherer='BioWardrobeDeseqJobGatherer',
  pool='biowardrobe_advanced',
  etype_id='[3,4,5,6,7,11]'
WHERE atype='deseq';
