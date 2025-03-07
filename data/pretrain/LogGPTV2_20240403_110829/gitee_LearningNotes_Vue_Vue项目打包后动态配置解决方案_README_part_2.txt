      minify: {
        removeComments: true,
        collapseWhitespace: true,
        removeAttributeQuotes: true
        // more options:
        // https://github.com/kangax/html-minifier#options-quick-reference
      }
      // default sort mode uses toposort which cannot handle cyclic deps
      // in certain cases, and in webpack 4, chunk order in HTML doesn't
      // matter anyway
    }),
    new ScriptExtHtmlWebpackPlugin({
      //`runtime` must same as runtimeChunk name. default is `runtime`
      inline: /runtime\..*\.js$/
    }),
    // keep chunk.id stable when chunk has no name
    new webpack.NamedChunksPlugin(chunk => {
      if (chunk.name) {
        return chunk.name
      }
      const modules = Array.from(chunk.modulesIterable)
      if (modules.length > 1) {
        const hash = require('hash-sum')
        const joinedHash = hash(modules.map(m => m.id).join('_'))
        let len = nameLength
        while (seen.has(joinedHash.substr(0, len))) len++
        seen.add(joinedHash.substr(0, len))
        return `chunk-${joinedHash.substr(0, len)}`
      } else {
        return modules[0].id
      }
    }),
    // keep module.id stable when vender modules does not change
    new webpack.HashedModuleIdsPlugin(),
    // copy custom static assets
    new CopyWebpackPlugin([
      {
        from: path.resolve(__dirname, '../static'),
        to: config.build.assetsSubDirectory,
        ignore: ['.*']
      },
      {
        from: path.resolve(__dirname,'../.env'),
        to: './'
      },
      {
        from: path.resolve(__dirname, '../env.sh'),
        to: './'
      },
      {
        from: path.resolve(__dirname, '../.default.env'),
        to: './'
      },
      {
        from: path.resolve(__dirname, '../env-config.js'),
        to: './'
      },
    ])
  ],
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        libs: {
          name: 'chunk-libs',
          test: /[\\/]node_modules[\\/]/,
          priority: 10,
          chunks: 'initial' // 只打包初始时依赖的第三方
        },
        elementUI: {
          name: 'chunk-elementUI', // 单独将 elementUI 拆包
          priority: 20, // 权重要大于 libs 和 app 不然会被打包进 libs 或者 app
          test: /[\\/]node_modules[\\/]element-ui[\\/]/
        }
      }
    },
    runtimeChunk: 'single',
    minimizer: [
      new UglifyJsPlugin({
        uglifyOptions: {
          mangle: {
            safari10: true
          }
        },
        sourceMap: config.build.productionSourceMap,
        cache: true,
        parallel: true
      }),
      // Compress extracted CSS. We are using this plugin so that possible
      // duplicated CSS from different components can be deduped.
      new OptimizeCSSAssetsPlugin()
    ]
  }
})
if (config.build.productionGzip) {
  const CompressionWebpackPlugin = require('compression-webpack-plugin')
  webpackConfig.plugins.push(
    new CompressionWebpackPlugin({
      asset: '[path].gz[query]',
      algorithm: 'gzip',
      test: new RegExp(
        '\\.(' + config.build.productionGzipExtensions.join('|') + ')$'
      ),
      threshold: 10240,
      minRatio: 0.8
    })
  )
}
if (config.build.generateAnalyzerReport || config.build.bundleAnalyzerReport) {
  const BundleAnalyzerPlugin = require('webpack-bundle-analyzer')
    .BundleAnalyzerPlugin
  if (config.build.bundleAnalyzerReport) {
    webpackConfig.plugins.push(
      new BundleAnalyzerPlugin({
        analyzerPort: 8080,
        generateStatsFile: false
      })
    )
  }
  if (config.build.generateAnalyzerReport) {
    webpackConfig.plugins.push(
      new BundleAnalyzerPlugin({
        analyzerMode: 'static',
        reportFilename: 'bundle-report.html',
        openAnalyzer: false
      })
    )
  }
}
module.exports = webpackConfig
```
## 修改index.html
然后我们修改 vue_mogu_admin\index.html 文件，我们需要在` index.html` 把我们的环境变量放入进去
```bash
```
我是放在 ``中
```bash
  蘑菇云后台管理系统
```
## 添加env.sh
下面我们需要在 `vue_mogu_admin` 目录下添加 `env.sh` 文件，用于容器启动时，替换环境变量
```bash
#!/bin/bash
set -x
set -e
# Recreate config file
absolute_path=$(cd `dirname $0`; pwd)
env_config=${absolute_path}/env-config.js
rm -rf ${env_config}
touch ${env_config}
# Add assignment
echo "window._env_ = {" >> ${env_config}
# Read each line in .env file
# Each line represents key=value pairs
sed -i '/^[[:space:]]*$/d' ${absolute_path}/.env
while read -r line || [[ -n "$line" ]];
do
  # Split env variables by character `=`
  if printf '%s\n' "$line" | grep -q -e '='; then
    varname=$(printf '%s\n' "$line" | sed -e 's/=.*//')
    varvalue=$(printf '%s\n' "$line" | sed -e 's/^[^=]*=//')
  fi
  # Read value of current variable if exists as Environment variable
  value=$(printf '%s\n' "${!varname}")
  # Otherwise use value from .env file
  [[ -z $value ]] && value=${varvalue}
  # Append configuration property to JS file
  echo "  $varname: \"$value\"," >> ${env_config}
done > ${env_config}
done > ${env_config}
sed -e "s/\//\\\/g" ${env_config}
STR=`echo $(cat ${env_config}) | sed 's#\/#\\\/#g'`
mv ${absolute_path}/index.html ${absolute_path}/index.html.bak
#sed -e "s/window\.\_env\_.*\}\;/${STR}/g" ${absolute_path}/index.html.bak > ${absolute_path}/index.html
sed -e "s###g" ${absolute_path}/index.html.bak > ${absolute_path}/index.html
cat ${env_config}
exec "$@"
```
## 编写Dockerfile
下面我们就可以编写Dockerfile文件进行Docker镜像构建相关操作
```bash
FROM registry.cn-shenzhen.aliyuncs.com/mogu-zh/nginx:latest
ADD ./dist/ /usr/share/nginx/html
RUN sed -i 's/\r$//' /usr/share/nginx/html/env.sh
RUN chmod +x /usr/share/nginx/html/env.sh
ENTRYPOINT ["/usr/share/nginx/html/env.sh"]
CMD ["nginx", "-g", "daemon off;"]
```
上述的Dockerfile文件，主要就是以nginx作为基础镜像，然后将我们的 dist文件夹放到 nginx目录下，然后执行脚本进行替换环境变量
## 打包镜像
完成上述的操作后，我们就可以在服务器上进行vue_mogu_admin的镜像构建了，然后提交到DockerHub中
```bash
# 安装依赖
npm install
# 打包
npm run build
# 构建镜像
docker build -t moxi/vue_mogu_admin .
# 提交镜像
docker push moxi/vue_mogu_web
```
最后在DockerHub就能看到我们刚刚构建的镜像
![image-20201127094131535](images/image-20201127094131535.png)
## 测试
### 默认配置
在构建好镜像后，我们就可以在服务器拉取我们的镜像进行测试，首先测试使用默认的配置
```bash
docker run --name vue_mogu_web -d  -it  -p 9527:80 moxi/vue_mogu_web
```
![image-20201127094356561](images/image-20201127094356561.png)
能看到下面的请求的IP如下所示
![image-20201127094603395](images/image-20201127094603395.png)
### 动态配置
下面我们在启动的时候，携带我们的变量
```bash
docker run --name vue_mogu_web -d  -it \
-e VUE_MOGU_WEB=http://101.132.194.128:9527 \
-e PICTURE_API=http://101.132.194.128:8602 \
-e PICTURE_API=http://101.132.194.128:8602 \
-e WEB_API=http://101.132.194.128:8603 \
-e ELASTICSEARCH=http://101.132.194.128:8605 \
-p 9527:80 moxi/vue_mogu_web
```
执行完成后，我们再次打开页面，发现已经变成了蘑菇博客的线上环境了~
![image-20201127101103543](images/image-20201127101103543.png)
打开F12，查看请求端口，发现ip地址已经成功修改了
![image-20201127101152897](images/image-20201127101152897.png)
到此为止，动态配置解决方案已经完成 ~