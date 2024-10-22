# SpringSecurity在分布式环境下的使用
## 参考
来源于黑马程序员： [手把手教你精通新版SpringSecurity](https://www.bilibili.com/video/BV1EE411u7YV?p=43)
## 分布式认证概念说明
分布式认证，即我们常说的单点登录，简称SSO，指的是在多应用系统的项目中，用户只需要登录一次，就可以访
问所有互相信任的应用系统。
## 分布式认证流程图
首先，我们要明确，在分布式项目中，每台服务器都有各自独立的session，而这些session之间是无法直接共享资
源的，所以，session通常不能被作为单点登录的技术方案。最合理的单点登录方案流程如下图所示：
![image-20200920202612159](images/image-20200920202612159.png)
**总结一下，单点登录的实现分两大环节：**
- **用户认证：**这一环节主要是用户向认证服务器发起认证请求，认证服务器给用户返回一个成功的令牌token，
  主要在认证服务器中完成，即图中的A系统，注意A系统只能有一个。
- **身份校验：**这一环节是用户携带token去访问其他服务器时，在其他服务器中要对token的真伪进行检验，主
  要在资源服务器中完成，即图中的B系统，这里B系统可以有很多个。
## JWT介绍
### 概念说明
从分布式认证流程中，我们不难发现，这中间起最关键作用的就是token，token的安全与否，直接关系到系统的
健壮性，这里我们选择使用JWT来实现token的生成和校验。
JWT，全称JSON Web Token，官网地址https://jwt.io，是一款出色的分布式身份校验方案。可以生成token，也可以解析检验token。
### JWT生成的token由三部分组成
- **头部**：主要设置一些规范信息，签名部分的编码格式就在头部中声明。
- **载荷**：token中存放有效信息的部分，比如用户名，用户角色，过期时间等，但是不要放密码，会泄露！
- **签名**：将头部与载荷分别采用base64编码后，用“.”相连，再加入**盐**，最后使用头部声明的编码类型进行编
  码，就得到了签名。【通过随机盐在进行加密】
### JWT生成token的安全性分析
从JWT生成的token组成上来看，要想避免token被伪造，主要就得看签名部分了，而签名部分又有三部分组成，其中头部和载荷的base64编码，几乎是透明的，毫无安全性可言，那么最终守护token安全的重担就落在了加入的盐上面了！
试想：如果生成token所用的盐与解析token时加入的盐是一样的。岂不是类似于中国人民银行把人民币防伪技术
公开了？大家可以用这个盐来解析token，就能用来伪造token。这时，我们就需要对盐采用非对称加密的方式进行加密，以达到生成token与校验token方所用的盐不一致的安全效果！
## 非对称加密RSA介绍
- **基本原理：**同时生成两把密钥：私钥和公钥，私钥隐秘保存，公钥可以下发给信任客户端
- **私钥加密**，持有私钥或公钥才可以解密
- **公钥加密**，持有私钥才可解密
- **优点**：安全，难以破解
- **缺点**：算法比较耗时，为了安全，可以接受
- **历史**：三位数学家Rivest、Shamir 和 Adleman 设计了一种算法，可以实现非对称加密。这种算法用他们三
  个人的名字缩写：RSA。
【总结】：也就是说，我们加密信息的时候，使用的是公钥，而验证token真伪的时候，使用的是公钥
## JWT相关工具类
### jar包 
```xml
    io.jsonwebtoken
    jjwt-api
    0.10.7
    io.jsonwebtoken
    jjwt-impl
    0.10.7
    runtime
    io.jsonwebtoken
    jjwt-jackson
    0.10.7
    runtime
```
### 载荷对象
```java
/**
* 为了方便后期获取token中的用户信息，将token中载荷部分单独封装成一个对象
*/
@Data
public class Payload {
}
```
### JWT工具类
```java
/**
 * 生成token以及校验token相关方法
 */
public class JwtUtils {
    private static final String JWT_PAYLOAD_USER_KEY = "user";
    /**
     * 私钥加密token
     *
     * @param userInfo   载荷中的数据
     * @param privateKey 私钥
     * @param expire     过期时间，单位分钟
     * @return JWT
     */
    public static String generateTokenExpireInMinutes(Object userInfo, PrivateKey privateKey, int expire) {
        return Jwts.builder()
                .claim(JWT_PAYLOAD_USER_KEY, JsonUtils.toString(userInfo))
                .setId(createJTI())
                .setExpiration(DateTime.now().plusMinutes(expire).toDate())
                .signWith(privateKey, SignatureAlgorithm.RS256)
                .compact();
    }
    /**
     * 私钥加密token
     *
     * @param userInfo   载荷中的数据
     * @param privateKey 私钥
     * @param expire     过期时间，单位秒
     * @return JWT
     */
    public static String generateTokenExpireInSeconds(Object userInfo, PrivateKey privateKey, int expire) {
        return Jwts.builder()
                .claim(JWT_PAYLOAD_USER_KEY, JsonUtils.toString(userInfo))
                .setId(createJTI())
                .setExpiration(DateTime.now().plusSeconds(expire).toDate())
                .signWith(privateKey, SignatureAlgorithm.RS256)
                .compact();
    }
    /**
     * 公钥解析token
     *
     * @param token     用户请求中的token
     * @param publicKey 公钥
     * @return Jws
     */
    private static Jws parserToken(String token, PublicKey publicKey) {
        return Jwts.parser().setSigningKey(publicKey).parseClaimsJws(token);
    }
    private static String createJTI() {
        return new String(Base64.getEncoder().encode(UUID.randomUUID().toString().getBytes()));
    }
    /**
     * 获取token中的用户信息
     *
     * @param token     用户请求中的令牌
     * @param publicKey 公钥
     * @return 用户信息
     */
    public static  Payload getInfoFromToken(String token, PublicKey publicKey, Class userType) {
        Jws claimsJws = parserToken(token, publicKey);
        Claims body = claimsJws.getBody();
        Payload claims = new Payload<>();
        claims.setId(body.getId());
        claims.setUserInfo(JsonUtils.toBean(body.get(JWT_PAYLOAD_USER_KEY).toString(), userType));
        claims.setExpiration(body.getExpiration());
        return claims;
    }
    /**
     * 获取token中的载荷信息
     *
     * @param token     用户请求中的令牌
     * @param publicKey 公钥
     * @return 用户信息
     */
    public static  Payload getInfoFromToken(String token, PublicKey publicKey) {
        Jws claimsJws = parserToken(token, publicKey);
        Claims body = claimsJws.getBody();
        Payload claims = new Payload<>();
        claims.setId(body.getId());
        claims.setExpiration(body.getExpiration());
        return claims;
    }
}
```
### RSA工具类
非对称加密工具列
```java
public class RsaUtils {
    private static final int DEFAULT_KEY_SIZE = 2048;
    /**
     * 从文件中读取公钥
     *
     * @param filename 公钥保存路径，相对于classpath
     * @return 公钥对象
     * @throws Exception
     */
    public static PublicKey getPublicKey(String filename) throws Exception {
        byte[] bytes = readFile(filename);
        return getPublicKey(bytes);
    }
    /**
     * 从文件中读取密钥
     *
     * @param filename 私钥保存路径，相对于classpath
     * @return 私钥对象
     * @throws Exception
     */
    public static PrivateKey getPrivateKey(String filename) throws Exception {
        byte[] bytes = readFile(filename);
        return getPrivateKey(bytes);
    }
    /**
     * 获取公钥
     *
     * @param bytes 公钥的字节形式
     * @return
     * @throws Exception
     */
    private static PublicKey getPublicKey(byte[] bytes) throws Exception {
        bytes = Base64.getDecoder().decode(bytes);
        X509EncodedKeySpec spec = new X509EncodedKeySpec(bytes);
        KeyFactory factory = KeyFactory.getInstance("RSA");
        return factory.generatePublic(spec);
    }
    /**
     * 获取密钥
     *
     * @param bytes 私钥的字节形式
     * @return
     * @throws Exception
     */
    private static PrivateKey getPrivateKey(byte[] bytes) throws NoSuchAlgorithmException, InvalidKeySpecException {
        bytes = Base64.getDecoder().decode(bytes);
        PKCS8EncodedKeySpec spec = new PKCS8EncodedKeySpec(bytes);
        KeyFactory factory = KeyFactory.getInstance("RSA");
        return factory.generatePrivate(spec);
    }
    /**
     * 根据密文，生存rsa公钥和私钥,并写入指定文件
     *
     * @param publicKeyFilename  公钥文件路径
     * @param privateKeyFilename 私钥文件路径
     * @param secret             生成密钥的密文
     */
    public static void generateKey(String publicKeyFilename, String privateKeyFilename, String secret, int keySize) throws Exception {
        KeyPairGenerator keyPairGenerator = KeyPairGenerator.getInstance("RSA");
        SecureRandom secureRandom = new SecureRandom(secret.getBytes());
        keyPairGenerator.initialize(Math.max(keySize, DEFAULT_KEY_SIZE), secureRandom);
        KeyPair keyPair = keyPairGenerator.genKeyPair();
        // 获取公钥并写出
        byte[] publicKeyBytes = keyPair.getPublic().getEncoded();
        publicKeyBytes = Base64.getEncoder().encode(publicKeyBytes);
        writeFile(publicKeyFilename, publicKeyBytes);
        // 获取私钥并写出
        byte[] privateKeyBytes = keyPair.getPrivate().getEncoded();
        privateKeyBytes = Base64.getEncoder().encode(privateKeyBytes);
        writeFile(privateKeyFilename, privateKeyBytes);
    }
    private static byte[] readFile(String fileName) throws Exception {
        return Files.readAllBytes(new File(fileName).toPath());
    }
    private static void writeFile(String destPath, byte[] bytes) throws IOException {
        File dest = new File(destPath);
        if (!dest.exists()) {
            dest.createNewFile();
        }
        Files.write(dest.toPath(), bytes);
    }
}
```
## SpringSecurity+JWT+RSA分布式认证思路分析
SpringSecurity主要是通过过滤器来实现功能的！我们要找到SpringSecurity实现认证和校验身份的过滤器！
回顾集中式认证流程
### 用户认证
使用UsernamePasswordAuthenticationFilter过滤器中attemptAuthentication方法实现认证功能，该过滤
器父类中successfulAuthentication方法实现认证成功后的操作。
### 身份校验
使用BasicAuthenticationFilter过滤器中doFilterInternal方法验证是否登录，以决定能否进入后续过滤器。
分析分布式认证流程
### 用户认证
由于，分布式项目，多数是前后端分离的架构设计，我们要满足可以接受异步post的认证请求参数，需要修
改UsernamePasswordAuthenticationFilter过滤器中attemptAuthentication方法，让其能够接收请求体。
另外，默认successfulAuthentication方法在认证通过后，是把用户信息直接放入session就完事了，现在我
们需要修改这个方法，在认证通过后生成token并返回给用户。
### 身份校验
原来BasicAuthenticationFilter过滤器中doFilterInternal方法校验用户是否登录，就是看session中是否有用
户信息，我们要修改为，验证用户携带的token是否合法，并解析出用户信息，交给SpringSecurity，以便于
后续的授权功能可以正常使用。
## SpringSecurity+JWT+RSA分布式认证实现
### 创建父工程并导入jar包
```xml
    4.0.0
    com.itheima
    springboot_security_jwt_rsa_parent
    pom
    1.0-SNAPSHOT
        heima_common
        heima_auth_server
        heima_source_product
        org.springframework.boot
        spring-boot-starter-parent
        2.1.3.RELEASE
```
## 通用模块
创建通用子模块并导入JWT相关jar包
```xml
        springboot_security_jwt_rsa_parent
        com.itheima
        1.0-SNAPSHOT
    4.0.0
    heima_common
            io.jsonwebtoken
            jjwt-api
            0.10.7
            io.jsonwebtoken
            jjwt-impl
            0.10.7
            runtime
            io.jsonwebtoken
            jjwt-jackson
            0.10.7
            runtime
            com.fasterxml.jackson.core