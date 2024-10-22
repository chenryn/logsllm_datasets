```xml
    me.zhyd.oauth
    JustAuth
    1.13.1
```
然后在编写一个用于处理第三方登录的 **Controller** 控制器 ，这里我创建了 **AuthRestApi.java** 文件
```java
/**
 * 第三方登录认证
 */
@RestController
@RequestMapping("/oauth")
@Api(value = "认证RestApi", tags = {"AuthRestApi"})
public class AuthRestApi {
    private static Logger log = LogManager.getLogger(IndexRestApi.class);
    @Autowired
    private UserService userService;
    @Value(value = "${justAuth.clientId.gitee}")
    private String giteeClienId;
    @Value(value = "${justAuth.clientSecret.gitee}")
    private String giteeClientSecret;
    @Value(value = "${justAuth.clientId.github}")
    private String githubClienId;
    @Value(value = "${justAuth.clientSecret.github}")
    private String githubClientSecret;
    @Value(value = "${data.webSite.url}")
    private String webSiteUrl;
    @Value(value = "${data.web.url}")
    private String moguWebUrl;
    @Value(value = "${BLOG.USER_TOKEN_SURVIVAL_TIME}")
    private Long userTokenSurvivalTime;
    @Autowired
    private StringRedisTemplate stringRedisTemplate;
    @ApiOperation(value = "获取认证", notes = "获取认证")
    @RequestMapping("/render")
    public String renderAuth(String source, HttpServletResponse response) throws IOException {
        log.info("进入render:" + source);
        AuthRequest authRequest = getAuthRequest(source);
        String token = AuthStateUtils.createState();
        String authorizeUrl = authRequest.authorize(token);
        Map map = new HashMap<>();
        map.put(SQLConf.URL, authorizeUrl);
        return ResultUtil.result(SysConf.SUCCESS, map);
    }
    /**
     * oauth平台中配置的授权回调地址，以本项目为例，在创建gitee授权应用时的回调地址应为：http://127.0.0.1:8603/oauth/callback/gitee
     */
    @RequestMapping("/callback/{source}")
    public void login(@PathVariable("source") String source, AuthCallback callback, HttpServletRequest request, HttpServletResponse httpServletResponse) throws IOException {
        log.info("进入callback：" + source + " callback params：" + JSONObject.toJSONString(callback));
        AuthRequest authRequest = getAuthRequest(source);
        AuthResponse response = authRequest.login(callback);
        String result = JSONObject.toJSONString(response);
        System.out.println(JSONObject.toJSONString(response));
        Map map = JsonUtils.jsonToMap(result);
        Map data = JsonUtils.jsonToMap(JsonUtils.objectToJson(map.get(SysConf.DATA)));
        Map token = JsonUtils.jsonToMap(JsonUtils.objectToJson(data.get(SysConf.TOKEN)));
        String accessToken = token.get(SysConf.ACCESS_TOKEN).toString();
        User user = userService.insertUserInfo(request, result);
        if (user != null) {
            //将从数据库查询的数据缓存到redis中
            stringRedisTemplate.opsForValue().set(SysConf.USER_TOEKN + SysConf.REDIS_SEGMENTATION + accessToken, JsonUtils.objectToJson(user), userTokenSurvivalTime, TimeUnit.SECONDS);
        }
        httpServletResponse.sendRedirect(webSiteUrl + "?token=" + accessToken);
    }
    @RequestMapping("/revoke/{source}/{token}")
    public Object revokeAuth(@PathVariable("source") String source, @PathVariable("token") String token) throws IOException {
        AuthRequest authRequest = getAuthRequest(source);
        return authRequest.revoke(AuthToken.builder().accessToken(token).build());
    }
    @RequestMapping("/refresh/{source}")
    public Object refreshAuth(@PathVariable("source") String source, String token) {
        AuthRequest authRequest = getAuthRequest(source);
        return authRequest.refresh(AuthToken.builder().refreshToken(token).build());
    }
    @ApiOperation(value = "获取用户信息", notes = "获取用户信息")
    @GetMapping("/verify/{accessToken}")
    public String verifyUser(@PathVariable("accessToken") String accessToken) {
        String userInfo = stringRedisTemplate.opsForValue().get("TOKEN:" + accessToken);
        if (StringUtils.isEmpty(userInfo)) {
            return ResultUtil.result(SysConf.ERROR, MessageConf.INVALID_TOKEN);
        } else {
            Map map = JsonUtils.jsonToMap(userInfo);
            return ResultUtil.result(SysConf.SUCCESS, map);
        }
    }
    @ApiOperation(value = "删除accessToken", notes = "删除accessToken")
    @RequestMapping("/delete/{accessToken}")
    public String deleteUserAccessToken(@PathVariable("accessToken") String accessToken) {
        stringRedisTemplate.delete(SysConf.USER_TOEKN + SysConf.REDIS_SEGMENTATION + accessToken);
        return ResultUtil.result(SysConf.SUCCESS, MessageConf.DELETE_SUCCESS);
    }
    private AuthRequest getAuthRequest(String source) {
        AuthRequest authRequest = null;
        switch (source) {
            case SysConf.GITHUB:
                authRequest = new AuthGithubRequest(AuthConfig.builder()
                        .clientId(githubClienId)
                        .clientSecret(githubClientSecret)
                        .redirectUri(moguWebUrl + "/oauth/callback/github")
                        .build());
                break;
            case SysConf.GITEE:
                authRequest = new AuthGiteeRequest(AuthConfig.builder()
                        .clientId(giteeClienId)
                        .clientSecret(giteeClientSecret)
                        .redirectUri(moguWebUrl + "/oauth/callback/gitee")
                        .build());
                break;
            default:
                break;
        }
        if (null == authRequest) {
            throw new AuthException(MessageConf.OPERATION_FAIL);
        }
        return authRequest;
    }
}
```
**application.yml** 部分配置文件如下所示：
```yml
data:
  # 门户页面
  webSite:
    url: http://localhost:9527/#/
  # mogu_web网址，用于第三方登录回调
  web:
    url: http://127.0.0.1:8603
# 第三方登录
justAuth:
  clientId:
    gitee: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    github: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
  clientSecret:
    gitee: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    github: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX 
```
## Gitee获取授权密钥
在码云中：我们首先进入设置页面，然后选择第三方应用，然后创建应用
![创建应用](images/1577774049160.png)
然后开始填写对应的内容
![填写回调地址](images/1577774070401.png)
重新点击第三方应用，获取到对应的 **ClientID** 和 **Client Secret**
![获取密钥](images/1577774097799.png)
**Github**上的操作同理，我们需要设置 **setting**，然后选择 **Developer settings**，**OAuth Apps**：创建一个新的
![创建应用](images/1577774134599.png)
这里填写的信息和刚刚码云上差不多，最后一个 **Authorization callback URL** 需要改成 **Github** 的回调地址
```bash
http://127.0.0.1:8603/oauth/callback/github
```
页面如下所示
![填写回调地址](images/1577774162993.png)
然后最后在创建成功后复制对应的 **ClientID** 和 **Client Secret** 即可：
![获取Github密钥](images/1577774183497.png)
## 关于AuthRestApi中方法的作用
在 **AuthRestApi** 中，下面几个方法的主要作用是：
- **renderAuth**：获取认证，前端通过 **login** 方法，即访问的是该接口，然后会创建一个认证请求，里面调用了**getAuthRequest** 方法
- **getAuthRequest**：该方法需要传入一个 **source** 参数，该参数主要是失败用户请求的接口，然后封装一个 **URL**，最后通过 **renderAuth** 返回到前台页面中，该方法前端接受后，最终会生成一个 **URL** ，然后跳转到对应的页面进行授权即可
例如下面的 **vue** 代码：
```
    goAuth: function (source) {
        var params = new URLSearchParams();
        params.append("source", source);
        login(params).then(response => {
          if (response.code == "success") {
            console.log(response.data.url);
            var token = response.data.token;
            console.log(response);
            window.location.href = response.data.url
          }
        });
      },
```
**vue** 代码，就是通过 **source** 判断用户点击的按钮，如果是 **github**，那么 **source** 为  **github** ，然后调用后台的登录方法，通过传递的 **source** ，生成一个授权页面 **url**，最后我们通过 **window.location.href** 跳转到授权页面：
![授权登录](images/1577774935816.png)
回调的接口如下所示：
```java
 /**
     * oauth平台中配置的授权回调地址，以本项目为例，在创建gitee授权应用时的回调地址应为：http://127.0.0.1:8603/oauth/callback/gitee
     */
    @RequestMapping("/callback/{source}")
    public void login(@PathVariable("source") String source, AuthCallback callback, HttpServletRequest request, HttpServletResponse httpServletResponse) throws IOException {
        log.info("进入callback：" + source + " callback params：" + JSONObject.toJSONString(callback));
        AuthRequest authRequest = getAuthRequest(source);
        AuthResponse response = authRequest.login(callback);
        String result = JSONObject.toJSONString(response);
        System.out.println(JSONObject.toJSONString(response));
        Map map = JsonUtils.jsonToMap(result);
        Map data = JsonUtils.jsonToMap(JsonUtils.objectToJson(map.get(SysConf.DATA)));
        Map token = JsonUtils.jsonToMap(JsonUtils.objectToJson(data.get(SysConf.TOKEN)));
        String accessToken = token.get(SysConf.ACCESS_TOKEN).toString();
        User user = userService.insertUserInfo(request, result);
        if (user != null) {
            //将从数据库查询的数据缓存到redis中
            stringRedisTemplate.opsForValue().set(SysConf.USER_TOEKN + SysConf.REDIS_SEGMENTATION + accessToken, JsonUtils.objectToJson(user), userTokenSurvivalTime, TimeUnit.SECONDS);
        }
        httpServletResponse.sendRedirect(webSiteUrl + "?token=" + accessToken);
    }
```
我们需要将得到的用户信息，存储到数据库，同时生成一个 **token**，通过 **url** 的方式，传递到前台，然后前台得到**token** 后，通过 **token** 获取用户信息：
```java
    @ApiOperation(value = "获取用户信息", notes = "获取用户信息")
    @GetMapping("/verify/{accessToken}")
    public String verifyUser(@PathVariable("accessToken") String accessToken) {
        String userInfo = stringRedisTemplate.opsForValue().get("TOKEN:" + accessToken);
        if (StringUtils.isEmpty(userInfo)) {
            return ResultUtil.result(SysConf.ERROR, MessageConf.INVALID_TOKEN);
        } else {
            Map map = JsonUtils.jsonToMap(userInfo);
            return ResultUtil.result(SysConf.SUCCESS, map);
        }
    }
```
然后在 **vue** 项目中，我们只需要判断是否有 **token** 通过 **url** 传递过来
```javascript
 let token = this.getUrlVars()["token"];
      // 判断url中是否含有token
      if (token != undefined) {
        setCookie("token", token, 1)
      }
      // 从cookie中获取token
      token = getCookie("token")
      if (token != undefined) {
        authVerify(token).then(response => {
          if (response.code == "success") {
            this.isLogin = true;
            this.userInfo = response.data;
          } else {
            this.isLogin = false;
            delCookie("token");
          }
        });
      } else {
        this.isLogin = false;
 }
```
如果有，那么就通过 **token** 获取用户信息，登录完成后，就能够看到头像回显了：
![显示用户信息](images/1577775104658.png)
本文只介绍了 **Gitee** 的登录流程，如果想要集成 **QQ** 登录或者 **微信** 登录可以参考 **JustAuth** 文档，或者直接查看**蘑菇博客**源码，里面实现了更多的登录方式。
> JustAuth文档：https://docs.justauth.whnb.wang/#/
>
> 蘑菇博客源码: https://gitee.com/moxi159753/mogu_blog_v2
我是**陌溪**，我们下期再见~
## 往期推荐
- [蘑菇博客从0到2000Star，分享我的Java自学路线图](https://mp.weixin.qq.com/s/3u6OOYkpj4_ecMzfMqKJRw)
- [从三本院校到斩获字节跳动后端研发Offer-讲述我的故事](https://mp.weixin.qq.com/s/c4rR_aWpmNNFGn-mZBLWYg)
- [陌溪在公众号摸滚翻爬半个月，整理的入门指南](https://mp.weixin.qq.com/s/Jj1i-mD9Tw0vUEFXi5y54g)
## 结语
**陌溪**是一个从三本院校一路摸滚翻爬上来的互联网大厂程序员。独立做过几个开源项目，其中**蘑菇博客**在码云上有 **2K Star** 。目前就职于**字节跳动的Data广告部门**，是字节跳动全线产品的商业变现研发团队。本公众号将会持续性的输出很多原创小知识以及学习资源。如果你觉得本文对你有所帮助，麻烦给文章点个“赞”和“在看”。同时欢迎各位小伙伴关注陌溪，让我们一起成长~
![和陌溪一起学编程](images/image-20210122092846701.png)