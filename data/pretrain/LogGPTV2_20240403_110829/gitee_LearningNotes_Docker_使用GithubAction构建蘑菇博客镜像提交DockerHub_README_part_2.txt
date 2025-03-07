on:
  push:
    branches:
      - Nacos
jobs:
  push:
    # 如果需要在构建前进行测试的话需要取消下面的注释和上面对应的 test 动作的注释。
    # needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-java@v1
        with:
          java-version: 1.8
      - uses: docker/setup-buildx-action@v1
        # 构建镜像，指定镜像名
      - name: Build Docker Images
        run: |
          echo '=====开始mvn clean====='
          mvn clean
          echo '=====开始mvn install&&package====='
          mvn install -DskipTests=true && mvn package -DskipTests=true
          echo '=====开始构建镜像====='
          echo '=====开始构建mogu_admin====='
          cd mogu_admin
          mvn docker:build
          cd ..
          echo '=====开始构建mogu_gateway====='
          cd mogu_gateway
          mvn docker:build
          cd ..
          echo '=====开始构建mogu_monitor====='
          cd mogu_monitor
          mvn docker:build
          cd ..
          echo '=====开始构建mogu_picture====='
          cd mogu_picture
          mvn docker:build
          cd ..
          echo '=====开始构建mogu_search====='
          cd mogu_search
          mvn docker:build
          cd ..
          echo '=====开始构建mogu_sms====='
          cd mogu_sms
          mvn docker:build
          cd ..
          echo '=====开始构建mogu_spider====='
          cd mogu_spider
          mvn docker:build
          cd ..
          echo '=====开始构建mogu_web====='
          cd mogu_web
          mvn docker:build
          cd ..
          echo '=====镜像构建结束====='
      # 登录到 dockerhub，使用 GitHub secrets 传入账号密码，密码被加密存储在 GitHub 服务器
      - name: Login to DockerHub
        uses: docker/login-action@v1
        with:
          username: ${{ secrets.DOCKER_HUB_USER_NAME }}
          password: ${{ secrets.DOCKER_HUB_PASSWORD }}
      - name: Push Docker Image
        run: |
          echo '=====开始上传镜像====='
          echo '=====开始上传mogu_admin====='
          docker push moxi/mogu_admin
          echo '=====开始上传mogu_gateway====='
          docker push moxi/mogu_gateway
          echo '=====开始上传mogu_monitor====='
          docker push moxi/mogu_monitor
          echo '=====开始上传mogu_picture====='
          docker push moxi/mogu_picture
          echo '=====开始上传mogu_search====='
          docker push moxi/mogu_search
          echo '=====开始上传mogu_sms====='
          docker push moxi/mogu_sms
          echo '=====开始上传mogu_spider====='
          docker push moxi/mogu_spider
          echo '=====开始上传mogu_web====='
          docker push moxi/mogu_web
          echo '=====镜像上传结束====='
```
执行完脚本后，进入到 [DockerHub](https://registry.hub.docker.com/) 中，发现已经成功提交到仓库了
![image-20201202091107737](images/image-20201202091107737.png)
### 阿里云容器镜像服务
上传至阿里云容器镜像服务的完整的脚本，如下所示
```yaml
name: Master-Build-Docker-Images
#on:
#  push:
#    # 每次 push tag 时进行构建，不需要每次 push 都构建。使用通配符匹配每次 tag 的提交，记得 tag 名一定要以 v 开头
#    tags:
#      - v*
on:
  push:
    branches:
      - Nacos
jobs:
  push:
    # 如果需要在构建前进行测试的话需要取消下面的注释和上面对应的 test 动作的注释。
    # needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-java@v1
        with:
          java-version: 1.8
      - uses: docker/setup-buildx-action@v1
      - uses: actions/setup-node@v1
        with:
          node-version: 12.x
      # 安装maven依赖
      - name: Maven Clean Install
        run: |
          echo '=====开始mvn clean====='
          mvn clean
          echo '=====开始mvn install&&package====='
          mvn install -DskipTests=true && mvn package -DskipTests=true
      - name: Build vue_mogu_admin and vue_mogu_web
        run: |
          echo '=====开始安装Vue_mogu_admin依赖====='
          cd ./vue_mogu_admin
          npm install
          npm run build
          cd ..
          echo '=====开始安装Vue_mogu_web依赖====='
          cd ./vue_mogu_web
          npm install
          npm run build
          cd ..
        # 构建镜像，指定镜像名
      - name: Build Java Docker Images
        run: |
          echo '=====开始构建镜像====='
          echo '=====开始构建mogu_admin====='
          cd mogu_admin
          mvn docker:build
          cd ..
          echo '=====开始构建mogu_gateway====='
          cd mogu_gateway
          mvn docker:build
          cd ..
          echo '=====开始构建mogu_monitor====='
          cd mogu_monitor
          mvn docker:build
          cd ..
          echo '=====开始构建mogu_picture====='
          cd mogu_picture
          mvn docker:build
          cd ..
          echo '=====开始构建mogu_search====='
          cd mogu_search
          mvn docker:build
          cd ..
          echo '=====开始构建mogu_sms====='
          cd mogu_sms
          mvn docker:build
          cd ..
          echo '=====开始构建mogu_spider====='
          cd mogu_spider
          mvn docker:build
          cd ..
          echo '=====开始构建mogu_web====='
          cd mogu_web
          mvn docker:build
          cd ..
          echo '=====镜像构建结束====='
      # 构建镜像，指定镜像名
      - name: Build Vue Docker Images
        run: |
          echo '=====开始构建镜像====='
          echo '=====开始构建vue_mogu_admin====='
          cd vue_mogu_admin
          docker build -t registry.cn-shenzhen.aliyuncs.com/mogublog/vue_mogu_admin .
          cd ..
          cd vue_mogu_web
          docker build -t registry.cn-shenzhen.aliyuncs.com/mogublog/vue_mogu_web .
          cd ..
          echo '=====镜像构建结束====='
      # 登录到 阿里云镜像服务，使用 GitHub secrets 传入账号密码，密码被加密存储在 GitHub 服务器
      - name: Login to Aliyun
        uses: docker/login-action@v1
        with:
          registry: registry.cn-shenzhen.aliyuncs.com
          username: ${{ secrets.ALIYUN_USER_NAME }}
          password: ${{ secrets.ALIYUN_PASSWORD }}
      - name: Push Docker Image
        run: |
          echo '=====开始上传镜像====='
          echo '=====开始上传mogu_admin====='
          docker push registry.cn-shenzhen.aliyuncs.com/mogublog/mogu_admin
          echo '=====开始上传mogu_gateway====='
          docker push registry.cn-shenzhen.aliyuncs.com/mogublog/mogu_gateway
          echo '=====开始上传mogu_monitor====='
          docker push registry.cn-shenzhen.aliyuncs.com/mogublog/mogu_monitor
          echo '=====开始上传mogu_picture====='
          docker push registry.cn-shenzhen.aliyuncs.com/mogublog/mogu_picture
          echo '=====开始上传mogu_search====='
          docker push registry.cn-shenzhen.aliyuncs.com/mogublog/mogu_search
          echo '=====开始上传mogu_sms====='
          docker push registry.cn-shenzhen.aliyuncs.com/mogublog/mogu_sms
          echo '=====开始上传mogu_spider====='
          docker push registry.cn-shenzhen.aliyuncs.com/mogublog/mogu_spider
          echo '=====开始上传mogu_web====='
          docker push registry.cn-shenzhen.aliyuncs.com/mogublog/mogu_web
          echo '=====开始上传vue_mogu_admin====='
          docker push registry.cn-shenzhen.aliyuncs.com/mogublog/vue_mogu_admin
          echo '=====开始上传vue_mogu_web====='
          docker push registry.cn-shenzhen.aliyuncs.com/mogublog/vue_mogu_web
          echo '=====镜像上传结束====='
```
执行完上述脚本后，我们发现已经成功提交到  [阿里云容器镜像服务](https://cr.console.aliyun.com/)
![image-20201202091542735](images/image-20201202091542735.png)
到目前为止，自动化镜像制作已经完成了~