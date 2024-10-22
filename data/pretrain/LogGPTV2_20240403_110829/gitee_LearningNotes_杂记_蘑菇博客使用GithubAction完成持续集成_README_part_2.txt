补充
*密钥验证*
- 机器1生成密钥对并将公钥发给机器2，机器2将公钥保存。
- 机器1要登录机器2时，机器2生成随机字符串并用机器1的公钥加密后，发给机器1。
- 机器1用私钥将其解密后发回给机器2，验证成功后登录
## 获取蘑菇博客配置文件
下面我们就需要使用git clone命令下载我们的配置文件了，在下载之前，我们首先需要配置好ssh免密登录
![image-20200106144749341](images/image-20200106144749341.png)
```
git clone PI:EMAIL:moxi624/mogu_prod_configuration.git
```
完整的action如下：run表示运行的是脚本文件，我们要做的是把刚刚下载的配置文件，使用mv命令，替换我们项目中的各个目录下的配置文件...
```
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
然后执行 mvn clean install进行打包
```
- name: Build Java jar
      run: | 
        mvn clean install
```
下面的操作是对vue_mogu_admin 和 vue_mogu_web进行打包，首先是安装node，然后执行
```
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
## 将构建好的文件打包
在我们将maven项目和vue项目进行打包后，我们要做的是将他们进行压缩，传递到我们的服务器
首先是创建一个文件夹，将刚刚生成的jar包和静态页面dist，全部放到文件夹下，然后使用tar命令进行压缩
```
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
## 使用Scp脚本拷贝到服务器
在这一步，我们就需要将我们刚刚压缩好的 transfer_files.tar.gz 超拷贝我们的阿里云服务器上，在这里我们无法直接使用scp命令，而需要借助别人写的的一个脚本：appleboy/scp-action@master
这里面需要用到刚刚我们定义的Secrets，如果没有的话，是无法完成的，source是我们需要拷贝的文件，target是我们需要拷贝的目标服务器的地址，完整代码如下所示：
```
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
在这步的action中，我们要做的事情是，使用ssh远程登录我们的云服务器，然后将我们的刚刚拷贝过来的压缩包解压，然后分发到各自的目录下，同时还需要将原来的文件进行备份和删除
这里远程连接ssh，也是引用的别人的action：appleboy/ssh-action@master
```
    - name: Distribution and backup
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.DOCKER_IP_DEV }}
        username: ${{ secrets.DOCKER_ID }}
        password: ${{ secrets.DOCKER_PASSWORD }}
        port: ${{ secrets.DOCKER_PORT }}
```
登录进去后，我们需要做的是，首先进入到home目录下，然后解压
```
script: |
          cd /home
          tar -zxvf /home/transfer_files.tar.gz
```
然后判断原来的备份文件是否存在，如果存在那么需要删除
```
if [ -f "/home/mogu_blog/mogu_admin/mogu_admin-0.0.1-SNAPSHOT.jar.bak" ];then
	echo "mogu_admin.jar.bak exists and is being deleted"
	rm -f /home/mogu_blog/mogu_admin/mogu_admin-0.0.1-SNAPSHOT.jar.bak
fi
```
然后把现在的jar文件进行备份
```
if [ -f "/home/mogu_blog/mogu_admin/mogu_admin-0.0.1-SNAPSHOT.jar" ];then
	echo "mogu_admin.jar exists and is being backup"
	mv /home/mogu_blog/mogu_admin/mogu_admin-0.0.1-SNAPSHOT.jar 		/home/mogu_blog/mogu_admin/mogu_admin-0.0.1-SNAPSHOT.jar.bak
fi
```
然后在从解压的文件夹中把对应的jar移动过来
```
mv /home/transfer_files/mogu_admin-0.0.1-SNAPSHOT.jar /home/mogu_blog/mogu_admin/mogu_admin-0.0.1-SNAPSHOT.jar
```
完整的动作如下所示，我们需要将 mogu_eureka、mogu_picture、mogu_sms、mogu_admin、mogu_web、以及vue_mogu_web 和 vue_mogu_admin 都替换一遍。
```
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
          echo "################# mogu_sms moving #################"
          if [ -f "/home/mogu_blog/mogu_sms/mogu_sms-0.0.1-SNAPSHOT.jar.bak" ];then
            echo "mogu_sms.jar.bak exists and is being deleted"
            rm -f /home/mogu_blog/mogu_sms/mogu_sms-0.0.1-SNAPSHOT.jar.bak
          fi
          if [ -f "/home/mogu_blog/mogu_admin/mogu_admin-0.0.1-SNAPSHOT.jar" ];then
            echo "mogu_sms.jar exists and is being backup"
            mv /home/mogu_blog/mogu_sms/mogu_sms-0.0.1-SNAPSHOT.jar /home/mogu_blog/mogu_sms/mogu_sms-0.0.1-SNAPSHOT.jar.bak
          fi
          mv /home/transfer_files/mogu_sms-0.0.1-SNAPSHOT.jar /home/mogu_blog/mogu_sms/mogu_sms-0.0.1-SNAPSHOT.jar
          echo "################# mogu_eureka moving #################"
          if [ -f "/home/mogu_blog/mogu_eureka/mogu_eureka-0.0.1-SNAPSHOT.jar.bak" ];then
            echo "mogu_eureka.jar.bak exists and is being deleted"
            rm -f /home/mogu_blog/mogu_eureka/mogu_eureka-0.0.1-SNAPSHOT.jar.bak
          fi
          if [ -f "/home/mogu_blog/mogu_eureka/mogu_eureka-0.0.1-SNAPSHOT.jar" ];then
            echo "mogu_eureka.jar exists and is being backup"
            mv /home/mogu_blog/mogu_eureka/mogu_eureka-0.0.1-SNAPSHOT.jar /home/mogu_blog/mogu_eureka/mogu_eureka-0.0.1-SNAPSHOT.jar.bak
          fi
          mv /home/transfer_files/mogu_eureka-0.0.1-SNAPSHOT.jar /home/mogu_blog/mogu_eureka/mogu_eureka-0.0.1-SNAPSHOT.jar
          echo "################# mogu_picture moving #################"
          if [ -f "/home/mogu_blog/mogu_picture/mogu_picture-0.0.1-SNAPSHOT.jar.bak" ];then
            echo "mogu_picture.jar.bak exists and is being deleted"
            rm -f /home/mogu_blog/mogu_picture/mogu_picture-0.0.1-SNAPSHOT.jar.bak
          fi
          if [ -f "/home/mogu_blog/mogu_picture/mogu_picture-0.0.1-SNAPSHOT.jar" ];then
            echo "mogu_picture.jar exists and is being backup"
            mv /home/mogu_blog/mogu_picture/mogu_picture-0.0.1-SNAPSHOT.jar /home/mogu_blog/mogu_picture/mogu_picture-0.0.1-SNAPSHOT.jar.bak
          fi
          mv /home/transfer_files/mogu_picture-0.0.1-SNAPSHOT.jar /home/mogu_blog/mogu_picture/mogu_picture-0.0.1-SNAPSHOT.jar
          echo "################# mogu_web moving #################"
          if [ -f "/home/mogu_blog/mogu_web/mogu_web-0.0.1-SNAPSHOT.jar.bak" ];then
            echo "mogu_web.jar.bak exists and is being deleted"
            rm -f /home/mogu_blog/mogu_web/mogu_web-0.0.1-SNAPSHOT.jar.bak
          fi
          if [ -f "/home/mogu_blog/mogu_web/mogu_web-0.0.1-SNAPSHOT.jar" ];then
            echo "mogu_web.jar exists and is being backup"
            mv /home/mogu_blog/mogu_web/mogu_web-0.0.1-SNAPSHOT.jar /home/mogu_blog/mogu_web/mogu_web-0.0.1-SNAPSHOT.jar.bak
          fi
          mv /home/transfer_files/mogu_web-0.0.1-SNAPSHOT.jar /home/mogu_blog/mogu_web/mogu_web-0.0.1-SNAPSHOT.jar
          echo "################# vue_mogu_web moving #################"
          if [ -d "/home/mogu_blog/vue_mogu_web/dist.bak/" ];then
            echo "vue_mogu_web dist.bak exists and is being deleted"
            cd /home/mogu_blog/vue_mogu_web
            rm -rf dist.bak/
          fi
          if [ -d "/home/mogu_blog/vue_mogu_web/dist/" ];then
            echo "vue_mogu_web dist exists and is being backup"
            mv /home/mogu_blog/vue_mogu_web/dist /home/mogu_blog/vue_mogu_web/dist.bak
          fi
          mv /home/transfer_files/web_dist /home/mogu_blog/vue_mogu_web/dist
          echo "################# vue_mogu_admin moving #################"
          if [ -d "/home/mogu_blog/vue_mogu_admin/dist.bak/" ];then
            echo "vue_mogu_admin dist.bak exists and is being deleted"
            cd /home/mogu_blog/vue_mogu_admin
            rm -rf dist.bak/
          fi
          if [ -d "/home/mogu_blog/vue_mogu_admin/dist/" ];then
            echo "vue_mogu_admin dist exists and is being backup"
            mv /home/mogu_blog/vue_mogu_admin/dist /home/mogu_blog/vue_mogu_admin/dist.bak
          fi
          mv /home/transfer_files/admin_dist /home/mogu_blog/vue_mogu_admin/dist
          echo "################# rm transfer_files.tar.gz #################"
          rm -rf /home/transfer_files.tar.gz
          echo "################# rm transfer_files #################"
          rm -rf /home/transfer_files
```
## 启动项目