from cwl_airflow import CWLJobDispatcher
from biowardrobe_airflow_advanced.utils.analyze import get_heatmap_job


class HeatmapJobDispatcher(CWLJobDispatcher):

    def __init__(self, *args, **kwargs):
        super(HeatmapJobDispatcher, self).__init__(task_id=self.__class__.__name__, *args, **kwargs)

    def execute(self, context):
        """
            conf = {
                "data_uid":      string,  corresponds to tableD
                "intervals_uid": string,  corresponds to tableL
                "name":          string,  corresponds to pltname
                "uid":           string,  corresponds to $UUID from ATDPPrjRun.php   
            }
             
            This is what we get from the client in ATDPPrjRun.php          
            {
              "project_id": string,
              "atype_id": int,
              "name": string,
              "atdp": [{
                "pltname": string,
                "tableD": string,     id from ems.genelist to point to BAM file through labdata record genelist.tableName = labdata.uid 
                "tableL": string      id from ems.genelist to point to genelist file throught params["genelist_file"] field
              }, {
                "pltname": string,
                "tableD": string,
                "tableL": string
              }]
            }                  
            Heatmap should be triggered for every item in atdp list from ATDPPrjRun.php   
        """
        conf = context['dag_run'].conf
        try:
            return self.cwl_dispatch(conf['job'])
        except KeyError:
            return self.cwl_dispatch(get_heatmap_job(conf))

