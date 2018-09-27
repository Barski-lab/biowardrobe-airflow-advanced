#!/usr/bin/env python3
from cwl_airflow_parser.cwldag import CWLDAG
from biowardrobe_airflow_advanced.utils.analyze import get_workflow


def create_advanced(workflow_name, job_dispatcher, job_gatherer, pool):
    dag = CWLDAG(default_args={'pool': pool}, cwl_workflow=get_workflow(workflow_name))
    dag.create()
    dag.add(job_dispatcher(dag=dag), to='top')
    dag.add(job_gatherer(dag=dag), to='bottom')
    return dag











