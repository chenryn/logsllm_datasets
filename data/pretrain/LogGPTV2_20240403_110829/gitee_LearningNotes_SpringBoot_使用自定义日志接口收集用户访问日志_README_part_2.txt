            //先执行业务
            Object result = joinPoint.proceed();
            try {
                // 日志收集
                handle(joinPoint);
            } catch (Exception e) {
                log.error("日志记录出错!", e);
            }
            return result;
        }
        private void handle(ProceedingJoinPoint point) throws Exception {
            HttpServletRequest request = RequestHolder.getRequest();
            Method currentMethod = AspectUtil.INSTANCE.getMethod(point);
            //获取操作名称
            BussinessLog annotation = currentMethod.getAnnotation(BussinessLog.class);
            boolean save = annotation.save();
            EBehavior behavior = annotation.behavior();
            String bussinessName = AspectUtil.INSTANCE.parseParams(point.getArgs(), annotation.value());
            String ua = RequestUtil.getUa();
            log.info("{} | {} - {} {} - {}", bussinessName, IpUtils.getIpAddr(request), RequestUtil.getMethod(), RequestUtil.getRequestUrl(), ua);
            if (!save) {
                return;
            }
            // 获取参数名称和值
            Map nameAndArgsMap = AopUtils.getFieldsName(point);
            Map result = EBehavior.getModuleAndOtherData(behavior, nameAndArgsMap, bussinessName);
            AopUtils.getFieldsName(point);
            if (result != null) {
                String userUid = "";
                if (request.getAttribute(SysConf.USER_UID) != null) {
                    userUid = request.getAttribute(SysConf.USER_UID).toString();
                }
                webVisitService.addWebVisit(userUid, request, behavior.getBehavior(), result.get(SysConf.MODULE_UID), result.get(SysConf.OTHER_DATA));
            }
        }
    }
这里使用了一个AspectUtils工具类
    package com.moxi.mogublog.utils;
    import com.alibaba.fastjson.JSON;
    import org.aspectj.lang.JoinPoint;
    import org.aspectj.lang.Signature;
    import org.aspectj.lang.reflect.MethodSignature;
    import org.springframework.util.StringUtils;
    import java.lang.reflect.Method;
    import java.util.List;
    /**
     * AOP相关的工具
     * @author 陌溪
     * @date 2020年2月27日08:44:28
     */
    public enum AspectUtil {
        INSTANCE;
        /**
         * 获取以类路径为前缀的键
         *
         * @param point 当前切面执行的方法
         */
        public String getKey(JoinPoint point, String prefix) {
            String keyPrefix = "";
            if (!StringUtils.isEmpty(prefix)) {
                keyPrefix += prefix;
            }
            keyPrefix += getClassName(point);
            return keyPrefix;
        }
        /**
         * 获取当前切面执行的方法所在的class
         *
         * @param point 当前切面执行的方法
         */
        public String getClassName(JoinPoint point) {
            return point.getTarget().getClass().getName().replaceAll("\\.", "_");
        }
        /**
         * 获取当前切面执行的方法的方法名
         *
         * @param point 当前切面执行的方法
         */
        public Method getMethod(JoinPoint point) throws NoSuchMethodException {
            Signature sig = point.getSignature();
            MethodSignature msig = (MethodSignature) sig;
            Object target = point.getTarget();
            return target.getClass().getMethod(msig.getName(), msig.getParameterTypes());
        }
        public String parseParams(Object[] params, String bussinessName) {
            if (bussinessName.contains("{") && bussinessName.contains("}")) {
                List result = RegexUtils.match(bussinessName, "(? paramMap = new HashMap();
            for (int i = 0; i   在Spring中，基于@Async标注的方法，称之为异步方法；这些方法将在执行的时候，将会在独立的线程中被执行，调用者无需等待它的完成，即可继续其他的操作。
        @Async
        @Override
        public void addWebVisit(String userUid, HttpServletRequest request, String behavior, String moduleUid, String otherData) {
            //增加记录（可以考虑使用AOP）
            Map map = IpUtils.getOsAndBrowserInfo(request);
            String os = map.get("OS");
            String browser = map.get("BROWSER");
            WebVisit webVisit = new WebVisit();
            String ip = IpUtils.getIpAddr(request);
            webVisit.setIp(ip);
            //从Redis中获取IP来源
            String jsonResult = stringRedisTemplate.opsForValue().get("IP_SOURCE:" + ip);
            if (StringUtils.isEmpty(jsonResult)) {
                String addresses = IpUtils.getAddresses("ip=" + ip, "utf-8");
                if (StringUtils.isNotEmpty(addresses)) {
                    webVisit.setIpSource(addresses);
                    stringRedisTemplate.opsForValue().set("IP_SOURCE" + BaseSysConf.REDIS_SEGMENTATION + ip, addresses, 24, TimeUnit.HOURS);
                }
            } else {
                webVisit.setIpSource(jsonResult);
            }
            webVisit.setOs(os);
            webVisit.setBrowser(browser);
            webVisit.setUserUid(userUid);
            webVisit.setBehavior(behavior);
            webVisit.setModuleUid(moduleUid);
            webVisit.setOtherData(otherData);
            webVisit.insert();
        }
tip：在使用@Async注解时候，需要在启动类中加入  @EnableAsync  才能够开启异步功能
指定接口进行收集
--------
最后我们使用  @BussinessLog 在我们需要收集的日志出进行标记，标记后AOP的环绕通知 就会获取该接口的相关参数，将其实例化到数据库中
  示例代码如下：
        @BussinessLog(value = "发表评论", behavior = EBehavior.PUBLISH_COMMENT)
        @ApiOperation(value = "增加评论", notes = "增加评论")
        @PostMapping("/add")
        public String add(@Validated({Insert.class}) @RequestBody CommentVO commentVO, BindingResult result) {
            QueryWrapper queryWrapper = new QueryWrapper<>();
            queryWrapper.eq(SysConf.STATUS, EStatus.ENABLE);
            WebConfig webConfig = webConfigService.getOne(queryWrapper);
            if (SysConf.CAN_NOT_COMMENT.equals(webConfig.getStartComment())) {
                return ResultUtil.result(SysConf.ERROR, MessageConf.NO_COMMENTS_OPEN);
            }
            ThrowableUtils.checkParamArgument(result);
            if (commentVO.getContent().length() > SysConf.TWO_TWO_FIVE) {
                return ResultUtil.result(SysConf.ERROR, MessageConf.COMMENT_CAN_NOT_MORE_THAN_225);
            }
            Comment comment = new Comment();
            comment.setSource(commentVO.getSource());
            comment.setBlogUid(commentVO.getBlogUid());
            comment.setContent(commentVO.getContent());
            comment.setUserUid(commentVO.getUserUid());
            comment.setToUid(commentVO.getToUid());
            comment.setToUserUid(commentVO.getToUserUid());
            comment.setStatus(EStatus.ENABLE);
            comment.insert();
            User user = userService.getById(commentVO.getUserUid());
            //获取图片
            if (StringUtils.isNotEmpty(user.getAvatar())) {
                String pictureList = this.pictureFeignClient.getPicture(user.getAvatar(), SysConf.FILE_SEGMENTATION);
                if (webUtils.getPicture(pictureList).size() > 0) {
                    user.setPhotoUrl(webUtils.getPicture(pictureList).get(0));
                }
            }
            comment.setUser(user);
            return ResultUtil.result(SysConf.SUCCESS, comment);
        }
最后用户的日志记录也能够成功记录下来了
![](http://image.moguit.cn/6211208ae36e4523ae620cd9cf0e180d)