# BioWardrobe Airflow Advanced Analysis

### Requirements
1 To generate outputs for `DeSeq` the following programs should be installed
  - `R`
    - `data.table` library

### How to init advanced analysis
Run on behalf of the user who has permissions to read BioWardrobe configuration file
   ```bash
   biowardrobe-advanced-init
   ```
   Use `-c` to use custom configuration file.
   
   It will do the following steps:
   - read BioWardrobe configuration from `/etc/wardrobe/wardrobe` file
     to get access to BioWardobe's DB
   - generate missing output files and update `params` field in DB
   - apply patches from `sql_patches` folder
     * add `params` column to `ems.atdp`
     * add `params` column to `ems.genelist`
   
   It's safe to run `biowardrobe-advanced-init` more then one time if necessarry.

### How make it run from php scripts
1. To be able to run DeSeq
   
   - copy `biowardrobe_airflow_advanced/scripts/run_deseq.sh` to the folder with `DESeqPrjRun.php` as `DESeqPrjRun.sh` 
   - update `DESeqPrjRun.php` with the following lines
     ```php
     $CMD_CWL = "./DESeqPrjRun.sh " . $tablepairs[$i]['t1'] . " " . $tablepairs[$i]['t2'] . " $rtypeid '$projectid' '$RNAME' $UUID";
     exec($CMD_CWL);
     ```
   For more details refer to the `/wardrobe/src.new/EMS/ems/data/DESeqPrjRun.php`

2. To be able to build Heatmap
  
   - copy `biowardrobe_airflow_advanced/scripts/run_heatmap.sh` to the folder with `ATDPPrjRun.php` as `ATDPPrjRun.sh`
   - update `ATDPPrjRun.php` with the following lines
     ```php
     $CMD_CWL = "./ATDPPrjRun.sh" . " " . $atdp[$i]->tableD . " " . $atdp[$i]->tableL . " '" . $atdp[$i]->pltname . "' " . $UUID;
     exec($CMD_CWL);
     ```
   For more details refer to the `/wardrobe/src.new/EMS/ems/data/ATDPPrjRun.php`

3. To be able to display Heatmap

   - copy `biowardrobe_airflow_advanced/scripts/load_heatmap.py` to the folder with `ATDPHeatA.php` as `ATDPHeatA.py`
   - update `ATDPHeatA.php` with the following lines
     ```php
     $resutls_folder = $settings->settings['wardrobe']['value'] . '/' . $settings->settings['advanced']['value'] . '/' . $uid;
     if (file_exists($resutls_folder))
       $command = "python3.6 ./ATDPHeatA.py -f " . $resutls_folder;
     else
       $command = "{$BIN}/atdp --avd_guid=\"{$uid}\" -log=\"{$TMP}/atdpheat.log\" --avd_heat_window=\"400\" -sam_twicechr=\"chrX chrY\" -sam_ignorechr=\"chrM\" -avd_window=4000 -avd_bsmooth=40 -avd_smooth=200 ";
     ```
   For more details refer to the `/wardrobe/src.new/EMS/ems/data/ATDPHeatA.php`

4. To run PCA
   - copy `biowardrobe_airflow_advanced/scripts/run_pca.sh` to the folder with `RPrjRun.php` as `RPrjRun.sh`
   - update `RPrjRun.php` with the following lines
     ```bash
     //$exec_result = shell_exec($command);   <----- THIS IS THE OLD STRING

     // Update to run PCA with CWL
     if ($rscriptid=="PCA00000-0000-0000-0000-000000000001") {
         $CMD_CWL = "/bin/bash /wardrobe/src.new/EMS/ems/data/RPrjRun.sh" . " " . $d->id . " " . $rargs;
         exec($CMD_CWL);
     } else {
         $exec_result = shell_exec($command);
     }
     ```
   - make sure that you set the absolute path to the `RPrjRun.sh`, because current directory is changed within `RPrjRun.php`
   - make sure that `PCA00000-0000-0000-0000-000000000001` corresponds to the correct `id` in `ems.advanced_r` 