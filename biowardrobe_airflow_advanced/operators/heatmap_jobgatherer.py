from cwl_airflow_parser import CWLJobGatherer
from biowardrobe_airflow_advanced.utils.upload import update_heatmap_atdp


class HeatmapJobGatherer(CWLJobGatherer):

    def __init__(self, *args, **kwargs):
        super(HeatmapJobGatherer, self).__init__(task_id=self.__class__.__name__, *args, **kwargs)

    def execute(self, context):
        conf = context['dag_run'].conf
        job_result, promises = self.cwl_gather(context)
        # update_heatmap_atdp(conf, job_result)
        return job_result
