import os
from cwl_airflow import CWLJobGatherer
from biowardrobe_airflow_advanced.utils.upload import update_atdp_table_for_heatmap, upload_atdp_results, update_genelist_table_for_atdp


class HeatmapJobGatherer(CWLJobGatherer):

    def __init__(self, *args, **kwargs):
        super(HeatmapJobGatherer, self).__init__(task_id=self.__class__.__name__, *args, **kwargs)

    def execute(self, context):
        conf = context['dag_run'].conf
        job_result, promises = self.cwl_gather(context)
        upload_atdp_results(conf, job_result)
        update_atdp_table_for_heatmap(conf, job_result)
        update_genelist_table_for_atdp(conf)
        return job_result
