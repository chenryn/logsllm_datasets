```
hostnamectl set-hostname master01
sudo reboot
```
hosts
```
cat > /etc/hosts  /etc/apt/sources.list.d/kubernetes.list  Your Kubernetes control-plane has initialized successfully!
>
> To start using your cluster, you need to run the following as a regular user:
>
> mkdir -p $HOME/.kube
>
>  sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
>
>  sudo chown $(id -u):$(id -g) $HOME/.kube/config
>
> You should now deploy a pod network to the cluster.
>
> Run "kubectl apply -f [podnetwork].yaml" with one of the options listed at:
>
> https://kubernetes.io/docs/concepts/cluster-administration/addons/
>
> Then you can join any number of worker nodes by running the following on each as root:
>
> kubeadm join 10.22.224.113:6443 --token peyc01.8mgmnj6k6zntq84s \
>
>   --discovery-token-ca-cert-hash sha256:ff2b928d246d5fdd8c27c152ab013df5fd665bb13f01184d8fb498f3d50fb554
```
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```
## 3.5.flannel
https://v1-16.docs.kubernetes.io/docs/setup/production-environment/tools/kubeadm/create-cluster-kubeadm/
https://raw.githubusercontent.com/coreos/flannel/2140ac876ef134e0ed5af15c65e414cf26827915/Documentation/kube-flannel.yml
```
kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
```
flannel镜像下载慢可以在一个节点下载然后分发，见4.2
## 3.6.join cluster
```
 kubeadm join 10.22.224.113:6443 --token peyc01.8mgmnj6k6zntq84s \
   --discovery-token-ca-cert-hash sha256:ff2b928d246d5fdd8c27c152ab013df5fd665bb13f01184d8fb498f3d50fb554
```
## 3.7.dashboard
无证书dashboard火狐可以访问
```
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.0.0-beta5/aio/deploy/recommended.yaml
kubectl patch svc -n kubernetes-dashboard kubernetes-dashboard -p '{"spec":{"type":"NodePort"}}'
kubectl -n kube-system describe secret $(kubectl -n kube-system get secret | grep admin-user | awk '{print $1}')
kubectl get svc -n kubernetes-dashboard
```
有证书dashboard
https://github.com/kubernetes/dashboard/releases
https://raw.githubusercontent.com/kubernetes/dashboard/v2.0.0-rc1/aio/deploy/recommended.yaml
```
mkdir keys
cd keys
# 创建空白证书
openssl genrsa -out ca.key 2048
openssl req -new -x509 -key ca.key -out ca.crt -days 3650 -subj "/C=CN/ST=HB/L=WH/O=DM/OU=YPT/CN=CA"
# 创建 dashboard 证书
(umask 077; openssl genrsa -out dashboard.key 2048)
openssl req -new -key dashboard.key  -out dashboard.csr -subj "/O=zhixin/CN=dashboard"
openssl  x509 -req -in dashboard.csr -CA ca.crt -CAkey ca.key  -CAcreateserial -out dashboard.crt -days 3650
kubectl create namespace kubernetes-dashboard
kubectl create secret generic kubernetes-dashboard-certs -n kubernetes-dashboard --from-file=dashboard.crt=./dashboard.crt  --from-file=dashboard.key=./dashboard.key
kubectl get secret -n kubernetes-dashboard |grep dashboard
kubectl create serviceaccount kubernetes-dashboard -n kubernetes-dashboard
kubectl get sa -n kubernetes-dashboard |grep kubernetes-dashboard
kubectl create clusterrolebinding kubernetes-dashboard --clusterrole=cluster-admin --serviceaccount=kubernetes-dashboard:kubernetes-dashboard
kubectl get secret -n kubernetes-dashboard |grep dashboard
kubectl describe secret kubernetes-dashboard-token-tptw4 -n kubernetes-dashboard
kubectl apply -f recommended.yaml
kubectl get svc -n kubernetes-dashboard
```
删除dashboard
```
kubectl delete ns kubernetes-dashboard
```
## 3.8.helm
https://helm.sh/docs/intro/install/
```
sudo snap install helm --classic
helm repo add stable https://kubernetes-charts.storage.googleapis.com/
# helm pull stable/stolon
```
## 3.9.stolon - helm
https://hub.helm.sh/charts/stable/stolon
在rancher中提前配置好“storageClassName”和“PV”
```
helm pull stable/stolon
vim value.yaml
#########################
image:
  repository: sorintlab/stolon
  tag: v0.16.0-pg10
​````````````````````````
persistence:
  enabled: true
  storageClassName: "local-storage-class"
  accessModes:
  - ReadWriteOnce
  size: 50Gi 
​````````````````````````  
superuserUsername: "stolon"
superuserPassword: "admin163"
replicationUsername: "repluser"
replicationPassword: "admin163"  
#############################
helm install -n stolon my-stolon ./stolon
```
备注：
stolon的“--dry-run”可以“simulate an install”生成yml文件
helm install xxx-release-name ./stolon --dry-run
appendix
手动生成“StorageClass”和“PersistentVolume”
```
---
kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: local-storage
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: stolonpv1
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: sc
  local:
    path: /stolon
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - node01
```
*通过helm安装不需要手动同步？？？？？？？？？？？？？？？
待定，需要测试一下
*如果按照stolon的示例，仅使用yml文件部署，需要初始化stolon，否则数据库不会同步
https://github.com/sorintlab/stolon/tree/master/examples/kubernetes
```
kubectl exec -it release-name-stolon-keeper-0 -- /bin/bash
stolonctl  --cluster-name=release-name-stolon --store-backend=kubernetes --kube-resource-kind=configmap init
```
“--cluster-name”要去configmap里看一下，要对应上
stolon init 之后，pg的默认user，dbname和密码都重置了，重置为helm install时的配置，
数据的数据？
手动改掉pg的密码之后，stolon不能识别了！怎么办？
## 3.10 manage k8s
- windows
- ubuntu
```
sudo curl -s https://mirrors.aliyun.com/kubernetes/apt/doc/apt-key.gpg | sudo apt-key add -
cat > /etc/apt/sources.list.d/kubernetes.list available
# stolon