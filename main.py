from cluster_utils import connect_to_cluster, install_helm, install_keda
from deploy_utils import deploy_jupyter
from keda_utils import create_scaledobject
from health_check import check_deployment_health

if __name__ == "__main__":
    connect_to_cluster()
    #install_helm()
    #install_keda()
    #deploy_jupyter()
    #create_scaledobject()
    check_deployment_health("jupyter-notebook")
