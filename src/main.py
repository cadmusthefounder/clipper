from clipper_admin import ClipperConnection, KubernetesContainerManager, DockerContainerManager
from clipper_admin.deployers import python as python_deployer
import requests, json, numpy as np

def sum(arr):
    return [str(sum(x)) for x in xs]

def main():
    # Setup container manager.
    # k8 = KubernetesContainerManager(kubernetes_proxy_addr="127.0.0.1:8080",
    #                                 useInternalIP=True)
    # clipper_conn = ClipperConnection(k8)
    swarm = DockerContainerManager()
    clipper_conn = ClipperConnection(swarm)
    clipper_conn.stop_all()
    clipper_conn.start_clipper()

    # Register application.
    clipper_conn.register_application(name="sum-app", 
                                      input_type="doubles", 
                                      default_output="-1.0", 
                                      slo_micros=10000000)

    # Model deployement.
    python_deployer.deploy_python_closure(clipper_conn, 
                                          name="sum-model", 
                                          version=1, 
                                          input_type="doubles", 
                                          func=sum)

    # Link application to model.
    clipper_conn.link_model_to_app(app_name="sum-app", 
                                   model_name="sum-model")

    # Test
    headers = {"Content-type": "application/json"}
    response = requests.post("http://localhost:1337/sum-app/predict", 
                             headers=headers, 
                             data=json.dumps({"input": list(np.random.random(10))})).json()
    print(response)

if __name__=="__main__":
    main()
