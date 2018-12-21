from cwl_airflow_parser import CWLJobGatherer


class PcaJobGatherer(CWLJobGatherer):

    def __init__(self, *args, **kwargs):
        super(PcaJobGatherer, self).__init__(task_id=self.__class__.__name__, *args, **kwargs)

    def execute(self, context):
        conf = context['dag_run'].conf
        job_result, promises = self.cwl_gather(context)
        return job_result
