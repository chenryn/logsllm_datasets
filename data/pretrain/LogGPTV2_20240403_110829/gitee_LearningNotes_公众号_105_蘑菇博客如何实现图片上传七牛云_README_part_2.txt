    } catch (QiniuException ex) {
        //如果遇到异常，说明删除失败
        ex.printStackTrace();
        return "删除失败";
    }
}
```
完整的 **QiNiuUtil.java** 如下：
```java
@Component
public class QiNiuUtil {
    @Value("${qiniu.accessKey}")
    private  String accessKey;      //公钥
    @Value("${qiniu.secretKey}")
    private  String accessSecretKey;   //私钥
    @Value("${qiniu.bucketName}")
    private  String bucketName;   // 存储空间
    @Value("${qiniu.path}")
    private  String path;       // 域名
    @Value("${qiniu.area}")
    private  String area;       // 区域
    /**
     * @param file 前端传来的图片
     * @return 图片的访问路径
     */
    public String upload(MultipartFile file){
        // 生成文件名
        String fileName = getRandomImgName(file.getOriginalFilename());
        //构造一个带指定 Region 对象的配置类
        Configuration cfg = setQiNiuArea(area);
        //...其他参数参考类注释
        UploadManager uploadManager = new UploadManager(cfg);
        //默认不指定key的情况下，以文件内容的hash值作为文件名
        try {
            byte[] uploadBytes = file.getBytes();
            Auth auth = Auth.create(accessKey, accessSecretKey);
            String upToken = auth.uploadToken(bucketName);
            Response response = uploadManager.put(uploadBytes, fileName , upToken);
            //解析上传成功的结果
            DefaultPutRet putRet = new Gson().fromJson(response.bodyString(), DefaultPutRet.class);
            return path + fileName;
        } catch (Exception ex) {
            ex.printStackTrace();
        }
        return null;
    }
    /**
     * 删除七牛云文件
     *
     * @return
     */
    public String deleteFile(String fileName) {
        //构造一个带指定Zone对象的配置类
        Configuration cfg = setQiNiuArea(area);
        //获取上传凭证
        Auth auth = Auth.create(accessKey, accessSecretKey);
        BucketManager bucketManager = new BucketManager(auth, cfg);
        try {
            bucketManager.delete(bucketName, fileName);
            return "删除成功";
        } catch (QiniuException ex) {
            //如果遇到异常，说明删除失败
            ex.printStackTrace();
            return "删除失败";
        }
    }
    /**
     * @Description: 生成唯一图片名称
     * @Param: fileName
     * @return: 云服务器fileName
     */
    public static String getRandomImgName(String fileName) {
        int index = fileName.lastIndexOf(".");
        if (fileName.isEmpty() || index == -1){
            throw new IllegalArgumentException();
        }
        // 获取文件后缀
        String suffix = fileName.substring(index).toLowerCase();
        // 生成UUID
        String uuid = UUID.randomUUID().toString().replaceAll("-", "");
        // 拼接新的名称
        return uuid + suffix;
    }
    /**
     * 设置七牛云上传区域（内部方法）
     *
     * @param area
     * @return
     */
    private Configuration setQiNiuArea(String area) {
        //构造一个带指定Zone对象的配置类
        Configuration cfg = null;
        //zong2() 代表华南地区
        switch (area) {
            case "z0": {
                cfg = new Configuration(Zone.zone0());
            }
            break;
            case "z1": {
                cfg = new Configuration(Zone.zone1());
            }
            break;
            case "z2": {
                cfg = new Configuration(Zone.zone2());
            }
            break;
            case "na0": {
                cfg = new Configuration(Zone.zoneNa0());
            }
            break;
            case "as0": {
                cfg = new Configuration(Zone.zoneAs0());
            }
            break;
            default: {
                return null;
            }
        }
        return cfg;
    }
}
```
最后，在编写 **Controller** ，提供 **http** 接口供外界调用
```java
@RestController
public class UploadController {
    @Autowired
    private QiNiuUtil qiNiuUtil;
    @PostMapping("/upload")
    public String upload(@RequestBody MultipartFile file) {
        return qiNiuUtil.upload(file);
    }
    @PostMapping("/delete")
    public String upload(@RequestParam String fileName) {
        return qiNiuUtil.deleteFile(fileName);
    }
}
```
完整的代码压缩包，陌溪也已经上传到网盘，在公众号回复【**qiniu**】即可下载
## 测试七牛云
完成代表编写后，启动项目开始进行图片上传测试
首先，测试一下上传功能，选择对应的文件点击上传，上传成功后即可返回图片url地址
![image-20220918222048956](images/image-20220918222048956.png)
打开七牛云的文件管理目录，即可查看到刚刚上传的文件：
![image-20220918235911995](images/image-20220918235911995.png)
调用 **delete** 方法，输入刚刚的文件名，即可删除刚刚上传的文件
![image-20220918222534685](images/image-20220918222534685.png)
再次到七牛云后台管理中，可以看到刚刚删除的配置
最后，陌溪也把完整的代码操作，上传到网盘了，
## 蘑菇集成七牛云配置
在蘑菇社区中，集成了 七牛云、阿里云、Minio、本地存储四种方式，通过配置表保存各个云存储的配置信息
![image-20220918223629052](images/image-20220918223629052.png)
可以通过切换 **TAB** ，来配置不同的存储模式，来满足大家对于不同存储方式的需求。
![image-20220918233011612](images/image-20220918233011612.png)
下面，是蘑菇图片服务的完整流程图
![image-20220919000611326](images/image-20220919000611326.png)
如果想了解关于蘑菇图片存储的更多细节，可以下载蘑菇源码体验吧~
```bash
Gitee： https://gitee.com/moxi159753/mogu_blog_v2
```
好了，本期的蘑菇第三方存储学习就到这里了
我是陌溪，我们下期再见。