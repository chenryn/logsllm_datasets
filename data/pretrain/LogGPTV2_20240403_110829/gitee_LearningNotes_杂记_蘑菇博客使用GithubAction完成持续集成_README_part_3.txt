在我们替换完成后，我们要做的就是启动我们的项目了，同样也是使用ssh连接我们的云服务器，然后进入各自的目录下，执行启动脚本
```
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
## 完整的workflow文件
如果小伙伴有多个服务器的话，可以配置两个workflow文件，一个用来监听测试分支的改动，一个用来测试master主分支的改动，这样首先将代码提交到测试服务器后，然后测试没问题，在提交到正式服务器~，下面是完整的workflow文件：
```
name: mogu CI/CD/DEV
on: 
  push:
    branches: 
      - dev
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@master
      with:
        ref: dev 
    - uses: actions/setup-java@v1
      with:
        java-version: 1.8
    - name: Set SSH Environment
      run: |
        mkdir -p ~/.ssh/
        echo "${{ secrets.ID_RSA }}" > ~/.ssh/id_rsa
        echo "${{ secrets.ID_RSA_PUB }}" > ~/.ssh/id_rsa.pub
        cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
        chmod 600 ~/.ssh/id_rsa
        chmod 700 ~/.ssh && chmod 700 ~/.ssh/*
        ls -l ~/.ssh/
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
    - name: Build Java jar
      run: | 
        mvn clean install
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
    - name: Scp file to aliyun
      uses: appleboy/scp-action@master
      with:
        host: ${{ secrets.DOCKER_IP_DEV }}
        username: ${{ secrets.DOCKER_ID }}
        password: ${{ secrets.DOCKER_PASSWORD }}
        port: ${{ secrets.DOCKER_PORT }}
        source: "transfer_files.tar.gz"
        target: "/home"
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
    - name: Start mogu_picture
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.DOCKER_IP_DEV }}
        username: ${{ secrets.DOCKER_ID }}
        password: ${{ secrets.DOCKER_PASSWORD }}
        port: ${{ secrets.DOCKER_PORT }}
        script: |
          cd /home/mogu_blog/mogu_picture/
          ./shutdown.sh
          ./startup.sh
    - name: Start mogu_admin
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.DOCKER_IP_DEV }}
        username: ${{ secrets.DOCKER_ID }}
        password: ${{ secrets.DOCKER_PASSWORD }}
        port: ${{ secrets.DOCKER_PORT }}
        script: |
          cd /home/mogu_blog/mogu_admin/
          ./shutdown.sh
          ./startup.sh
    - name: Start mogu_sms
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.DOCKER_IP_DEV }}
        username: ${{ secrets.DOCKER_ID }}
        password: ${{ secrets.DOCKER_PASSWORD }}
        port: ${{ secrets.DOCKER_PORT }}
        script: |
          cd /home/mogu_blog/mogu_sms/
          ./shutdown.sh
          ./startup.sh
    - name: Start mogu_web
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.DOCKER_IP_DEV }}
        username: ${{ secrets.DOCKER_ID }}
        password: ${{ secrets.DOCKER_PASSWORD }}
        port: ${{ secrets.DOCKER_PORT }}
        script: |
          cd /home/mogu_blog/mogu_web/
          ./shutdown.sh
          ./startup.sh
```
## 参考
- [GitHub Actions 入门教程](http://www.ruanyifeng.com/blog/2019/09/getting-started-with-github-actions.html)
- [GitHub Actions 初体验](https://zhuanlan.zhihu.com/p/52750017)