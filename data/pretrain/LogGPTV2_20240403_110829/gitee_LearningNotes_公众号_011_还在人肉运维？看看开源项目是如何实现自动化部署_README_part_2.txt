![](images/1578308804722.png)
然后进行密钥添加
![](images/1578308818590.png)
注意每次添加完后，要是想修改的话，只能够重新删除后再添加。这里主要添加的几个 **Secrets** 有：
```bash
DOCKER_ID：云服务器登录名，如root等
DOCKER_IP：云服务器IP地址
DOCKER_PASSWORD：云服务器IP地址
DOCKER_PORT：云服务器ssh端口
ID_RSA：私钥
ID_RSA_PUB：公钥
```
在 **Actions** 脚本中通过 **${{ secrets.xxxxx }}** 引用，示例如下：
```yaml
  - name: Set SSH Environment
    run: |
      mkdir -p ~/.ssh/
      echo "${{ secrets.ID_RSA }}" > ~/.ssh/id_rsa
      echo "${{ secrets.ID_RSA_PUB }}" > ~/.ssh/id_rsa.pub
      cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
      chmod 600 ~/.ssh/id_rsa
      chmod 700 ~/.ssh && chmod 700 ~/.ssh/*
      ls -l ~/.ssh/
```
关于密钥验证过程如下：
- 机器1生成密钥对并将公钥发给机器2，机器2将公钥保存。
- 机器1要登录机器2时，机器2生成随机字符串并用机器1的公钥加密后，发给机器1。
- 机器1用私钥将其解密后发回给机器2，验证成功后登录
## 获取蘑菇博客配置文件
下面我们就需要使用 **git clone** 命令下载我们的配置文件了，在下载之前，我们首先需要配置好 **ssh** 免密登录
![使用SSH拉取项目](images/1578308868450.png)
拉取脚本如下
```bash
git clone PI:EMAIL:moxi624/mogu_prod_configuration.git
```
完整的 **action** 如下：其中 **run** 表示运行的是脚本文件，我们要做的是把刚刚下载的配置文件，使用 **mv** 命令，替换我们项目中的各个目录下的配置文件...
```yaml
 - name: Download config file and replace
      run: |
        git clone PI:EMAIL:moxi624/mogu_prod_configuration.git
        mv -f ./mogu_prod_configuration/dev_config/mogu_admin/application.yml ./mogu_admin/src/main/resources/application.yml
        mv -f ./mogu_prod_configuration/dev_config/mogu_eureka/application.yml ./mogu_eureka/src/main/resources/application.yml
        mv -f ./mogu_prod_configuration/dev_config/mogu_picture/application.yml ./mogu_picture/src/main/resources/application.yml
        mv -f ./mogu_prod_configuration/dev_config/mogu_sms/application.yml ./mogu_sms/src/main/resources/application.yml
        mv -f ./mogu_prod_configuration/dev_config/mogu_web/application.yml ./mogu_web/src/main/resources/application.yml
        mv -f ./mogu_prod_configuration/dev_config/vue_mogu_admin/config.js ./vue_mogu_admin/static/ckeditor/config.js
        mv -f ./mogu_prod_configuration/dev_config/vue_mogu_admin/prod.env.js ./vue_mogu_admin/config/prod.env.js
        mv -f ./mogu_prod_configuration/dev_config/vue_mogu_web/prod.env.js ./vue_mogu_web/config/prod.env.js
```
然后执行 **mvn clean install** 进行打包
```yaml
- name: Build Java jar
      run: | 
        mvn clean install
```
下面的操作是对 **vue_mogu_admin** 和 **vue_mogu_web** 进行打包。因为是 **Vue** 项目，所需安装 **node** 环境，然后执行
```yaml
# 安装依赖
npm install
# 打包
npm run build
```
完整代码如下：
```
    - name: Use Node.js 12.x
      uses: actions/setup-node@v1
      with:
        node-version: 12.x    
    - name: Build vue_mogu_admin and vue_mogu_web
      run: |
        cd ./vue_mogu_admin
        npm install
        npm run build
        cd ..
        cd ./vue_mogu_web
        npm install
        npm run build
        cd ..
```
## 构建的文件打包
将 **maven** 项目和 **vue** 项目进行打包后，后续要做的是将其压缩，传递到我们的服务器
首先是创建一个文件夹，将刚刚生成的 **jar** 包和静态页面 **dist**，全部放到文件夹下，然后使用 **tar** 命令进行压缩
```yaml
 - name: Move files and compress
      run: |
        mkdir -p transfer_files
        mv ./mogu_admin/target/mogu_admin-0.0.1-SNAPSHOT.jar ./transfer_files/mogu_admin-0.0.1-SNAPSHOT.jar
        mv ./mogu_sms/target/mogu_sms-0.0.1-SNAPSHOT.jar ./transfer_files/mogu_sms-0.0.1-SNAPSHOT.jar
        mv ./mogu_eureka/target/mogu_eureka-0.0.1-SNAPSHOT.jar ./transfer_files/mogu_eureka-0.0.1-SNAPSHOT.jar
        mv ./mogu_picture/target/mogu_picture-0.0.1-SNAPSHOT.jar ./transfer_files/mogu_picture-0.0.1-SNAPSHOT.jar
        mv ./mogu_web/target/mogu_web-0.0.1-SNAPSHOT.jar ./transfer_files/mogu_web-0.0.1-SNAPSHOT.jar
        mv ./vue_mogu_web/dist ./transfer_files/web_dist
        mv ./vue_mogu_admin/dist ./transfer_files/admin_dist
        tar -zcvf  transfer_files.tar.gz transfer_files/
```
## Scp脚本拷贝到服务器
在这一步，我们就需要将我们刚刚压缩好的 **transfer_files.tar.gz** 使用**远程超拷贝**命令，复制到我们的阿里云服务器上，在这里我们无法直接使用 **scp** 命令，而需要借助别人写的的一个脚本：**appleboy/scp-action@master**
这里面需要用到刚刚我们定义的 **Secrets**，如果没有的话，是无法完成的，**source** 是我们需要拷贝的文件，**target** 是我们需要拷贝的目标服务器的地址，完整代码如下所示：
```bash
    - name: Scp file to aliyun
      uses: appleboy/scp-action@master
      with:
        host: ${{ secrets.DOCKER_IP_DEV }}
        username: ${{ secrets.DOCKER_ID }}
        password: ${{ secrets.DOCKER_PASSWORD }}
        port: ${{ secrets.DOCKER_PORT }}
        source: "transfer_files.tar.gz"
        target: "/home"
```
## 文件分发和备份
在这步的 **action** 中，我们要做的事情是，使用ssh远程登录我们的云服务器，然后将我们的刚刚拷贝过来的压缩包解压，然后分发到各自的目录下，同时还需要将原来的文件进行备份和删除
这里远程连接 **ssh**，也是引用的别人的 **action**：**appleboy/ssh-action@master**
```yaml
    - name: Distribution and backup
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.DOCKER_IP_DEV }}
        username: ${{ secrets.DOCKER_ID }}
        password: ${{ secrets.DOCKER_PASSWORD }}
        port: ${{ secrets.DOCKER_PORT }}
```
登录进去后，我们需要做的是，首先进入到home目录下，然后解压
```yaml
script: |
          cd /home
          tar -zxvf /home/transfer_files.tar.gz
```
然后判断原来的备份文件是否存在，如果存在那么需要删除
```yaml
if [ -f "/home/mogu_blog/mogu_admin/mogu_admin-0.0.1-SNAPSHOT.jar.bak" ];then
	echo "mogu_admin.jar.bak exists and is being deleted"
	rm -f /home/mogu_blog/mogu_admin/mogu_admin-0.0.1-SNAPSHOT.jar.bak
fi
```
然后把现在的jar文件进行备份
```yaml
if [ -f "/home/mogu_blog/mogu_admin/mogu_admin-0.0.1-SNAPSHOT.jar" ];then
	echo "mogu_admin.jar exists and is being backup"
	mv /home/mogu_blog/mogu_admin/mogu_admin-0.0.1-SNAPSHOT.jar 		/home/mogu_blog/mogu_admin/mogu_admin-0.0.1-SNAPSHOT.jar.bak
fi
```
然后在从解压的文件夹中把对应的jar移动过来
```yaml
mv /home/transfer_files/mogu_admin-0.0.1-SNAPSHOT.jar /home/mogu_blog/mogu_admin/mogu_admin-0.0.1-SNAPSHOT.jar
```
我们需要将 mogu_eureka、mogu_picture、mogu_sms、mogu_admin、mogu_web、以及vue_mogu_web 和 vue_mogu_admin 都替换一遍。
```yaml
  - name: Distribution and backup
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.DOCKER_IP_DEV }}
        username: ${{ secrets.DOCKER_ID }}
        password: ${{ secrets.DOCKER_PASSWORD }}
        port: ${{ secrets.DOCKER_PORT }}
        script: |
          cd /home
          tar -zxvf /home/transfer_files.tar.gz
          echo "################# mogu_admin moving #################"
          if [ -f "/home/mogu_blog/mogu_admin/mogu_admin-0.0.1-SNAPSHOT.jar.bak" ];then
            echo "mogu_admin.jar.bak exists and is being deleted"
            rm -f /home/mogu_blog/mogu_admin/mogu_admin-0.0.1-SNAPSHOT.jar.bak
          fi
          if [ -f "/home/mogu_blog/mogu_admin/mogu_admin-0.0.1-SNAPSHOT.jar" ];then
            echo "mogu_admin.jar exists and is being backup"
            mv /home/mogu_blog/mogu_admin/mogu_admin-0.0.1-SNAPSHOT.jar /home/mogu_blog/mogu_admin/mogu_admin-0.0.1-SNAPSHOT.jar.bak
          fi
          mv /home/transfer_files/mogu_admin-0.0.1-SNAPSHOT.jar /home/mogu_blog/mogu_admin/mogu_admin-0.0.1-SNAPSHOT.jar
```
## 启动项目
在我们替换完成后，我们要做的就是启动我们的项目了，同样也是使用 **ssh** 连接我们的云服务器，然后进入各自的目录下，执行启动脚本
```yaml
 - name: Start mogu_eureka
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.DOCKER_IP_DEV }}
        username: ${{ secrets.DOCKER_ID }}
        password: ${{ secrets.DOCKER_PASSWORD }}
        port: ${{ secrets.DOCKER_PORT }}
        script: |
          cd /home/mogu_blog/mogu_eureka/
          ./shutdown.sh
          ./startup.sh
```
到这里为止，自动化脚本已经构建完毕~。如果小伙伴有多台服务器的话，可以配置两个 **workflow** 文件，一个用来监听 **dev** 分支的改动，另一个用来监听 **master** 主分支的改动。这样将代码提交到测试服务器进行测试，测试通过后，在提交到正式服务器~。
陌溪已经将完整的 **workflow** 脚本文件打包好了，在公众号回复 **自动化部署脚本** ，即可获取。
## 结语
**陌溪**是一个从三本院校一路摸滚翻爬上来的互联网大厂程序员。独立做过几个开源项目，其中**蘑菇博客**在码云上有 **2K Star** 。目前就职于**字节跳动的Data广告部门**，是字节跳动全线产品的商业变现研发团队。本公众号将会持续性的输出很多原创小知识以及学习资源。如果你觉得本文对你有所帮助，麻烦给文章点个“赞”和“在看”。同时欢迎各位小伙伴关注陌溪，让我们一起成长~
![和陌溪一起学编程](images/image-20210122092846701.png)
## 参考
 阮一峰 GitHub Actions 入门教程：
http://www.ruanyifeng.com/blog/2019/09/getting-started-with-github-actions.html
GitHub Actions 初体验:
https://zhuanlan.zhihu.com/p/52750017