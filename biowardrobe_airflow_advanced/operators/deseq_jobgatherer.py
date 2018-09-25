import os
from cwl_airflow_parser import CWLJobGatherer


class DeseqJobGatherer(CWLJobGatherer):

    def __init__(self, *args, **kwargs):
        super(DeseqJobGatherer, self).__init__(task_id=self.__class__.__name__, *args, **kwargs)

    def execute(self, context):
        pass
