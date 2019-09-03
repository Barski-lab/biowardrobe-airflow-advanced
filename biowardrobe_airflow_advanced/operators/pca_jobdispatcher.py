from cwl_airflow import CWLJobDispatcher
from biowardrobe_airflow_advanced.utils.analyze import get_pca_job


class PcaJobDispatcher(CWLJobDispatcher):

    def __init__(self, *args, **kwargs):
        super(PcaJobDispatcher, self).__init__(task_id=self.__class__.__name__, *args, **kwargs)

    def execute(self, context):
        """
            conf = {
                "uid":         string,
                "expression":  "string string string ..."
            }
        
            "uid" is taken from $UUID and is randomly generated
            "expression" is the space-separated string to include ids from genelist
        """
        conf = context['dag_run'].conf
        try:
            return self.cwl_dispatch(conf['job'])
        except KeyError:
            return self.cwl_dispatch(get_pca_job(conf))

