```
然后在编写定义一个Controller，这里我创建了一个AuthRestApi.java文件
```java
package com.moxi.mogublog.web.restapi;
import com.alibaba.fastjson.JSONObject;
import com.moxi.mogublog.utils.JsonUtils;
import com.moxi.mogublog.utils.ResultUtil;
import com.moxi.mogublog.utils.StringUtils;
import com.moxi.mogublog.web.global.MessageConf;
import com.moxi.mogublog.web.global.SQLConf;
import com.moxi.mogublog.web.global.SysConf;
import com.moxi.mogublog.xo.entity.User;
import com.moxi.mogublog.xo.service.UserService;
import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import me.zhyd.oauth.config.AuthConfig;
import me.zhyd.oauth.exception.AuthException;
import me.zhyd.oauth.model.AuthCallback;
import me.zhyd.oauth.model.AuthResponse;
import me.zhyd.oauth.model.AuthToken;
import me.zhyd.oauth.request.AuthGiteeRequest;
import me.zhyd.oauth.request.AuthGithubRequest;
import me.zhyd.oauth.request.AuthRequest;
import me.zhyd.oauth.utils.AuthStateUtils;
import org.apache.log4j.LogManager;
import org.apache.log4j.Logger;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.TimeUnit;
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
application.yml部分配置文件如下所示：
```yaml
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
关于clientId和clientSecret需要到各自的码云和github设置上进行获取：
在码云中：我们首先进入设置页面，然后选择第三方应用，然后创建应用
![image-20191231125943234](images/image-20191231125943234.png)
然后开始填写对应的内容
![image-20191231130159318](images/image-20191231130159318.png)
重新点击第三方应用，获取到对应的ClientID和Client Secret替换即可
![image-20191231133512612](images/image-20191231133512612.png)
Github上的操作同理，我们需要设置setting，然后选择Developer settings，OAuth Apps：创建一个新的
![image-20191231133218598](images/image-20191231133218598.png)
这里填写的信息和刚刚码云上差不多
![image-20191231133315906](images/image-20191231133315906.png)
然后最后在创建成功后复制对应的ClientID和Client Secret即可：
![image-20191231133422982](images/image-20191231133422982.png)
在AuthRestApi中，下面几个方法的主要作用是：
- renderAuth：获取认证，前端通过login方法，即访问的是该接口，然后会创建一个认证请求，里面调用了getAuthRequest方法
- getAuthRequest：该方法需要传入一个source参数，该参数主要是失败用户请求的接口，然后封装一个URL，最后通过renderAuth返回到前台页面中，该方法前端接受后，最终会生成一个URL，然后跳转到对应的页面进行授权即可
例如下面的vue代码：
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
vue代码，就是通过source判断我点击的按钮，如果是github，那么source为 ”github“，然后调用后台的登录方法，通过传递的source，生成一个授权页面url，最后我们通过window.location.href 跳转到授权页面：
![image-20191231124501601](images/image-20191231124501601.png)
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
我们需要将得到的用户信息，存储到数据库，同时生成一个token，通过url的方式，传递到前台，然后前台得到token后，通过token获取用户信息：
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
然后在vue项目中，我们只需要判断是否有token通过url传递过来
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
如果有，那么就通过token获取用户信息，登录完成后，就能够看到头像回显了：
![image-20191231125825022](images/image-20191231125825022.png)