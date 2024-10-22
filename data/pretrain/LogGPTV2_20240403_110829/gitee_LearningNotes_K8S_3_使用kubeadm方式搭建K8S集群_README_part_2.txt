# 添加
kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
##①首先下载v0.13.1-rc2-amd64 镜像
##参考博客：https://www.cnblogs.com/pyxuexi/p/14288591.html
##② 导入镜像，命令，，特别提示，3个机器都需要导入，3个机器都需要导入，3个机器都需要导入，3个机器都需要导入，重要的事情说3遍。不然抱错。如果没有操作，报错后，需要删除节点，重置，在导入镜像，重新加入才行。本地就是这样操作成功的！
docker load  /proc/sys/net/ipv4/ip_forward
```
修改完成后，重新执行命令即可