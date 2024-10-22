前言
--
最开始蘑菇博客收集用户访问日志，是直接在请求接口里面进行编写的，比如像下面这样
![](http://image.moguit.cn/f3b9e96ea8334a9ea534c9b61aa7bee8)
很显然这种方法是非常笨的一种方法，因为它直接侵入了我们的业务代码，引入无关的操作，因此这次主要就是通过spring aop + 自定义接口，来收集用户的访问日志
编写自定义接口
-------
首先我们需要创建一个自定义接口
    package com.moxi.mogublog.web.log;
    import com.moxi.mougblog.base.enums.EBehavior;
    import com.moxi.mougblog.base.enums.PlatformEnum;
    import java.lang.annotation.ElementType;
    import java.lang.annotation.Retention;
    import java.lang.annotation.RetentionPolicy;
    import java.lang.annotation.Target;
    /**
     * 日志记录、自定义注解
     *
     * @author 陌溪
     * @date 2020年2月27日08:55:02
     */
    @Target(ElementType.METHOD)
    @Retention(RetentionPolicy.RUNTIME)
    public @interface BussinessLog {
        /**
         * 业务名称
         *
         * @return
         */
        String value() default "";
        /**
         * 用户行为
         *
         * @return
         */
        EBehavior behavior();
        /**
         * 平台，默认为WEB端
         */
        PlatformEnum platform() default PlatformEnum.WEB;
        /**
         * 是否将当前日志记录到数据库中
         */
        boolean save() default true;
    }
这里的用户行为使用了枚举类，方便扩展，目前共有15中行为
    package com.moxi.mougblog.base.enums;
    import com.moxi.mogublog.utils.JsonUtils;
    import com.moxi.mougblog.base.global.BaseSysConf;
    import java.util.HashMap;
    import java.util.Map;
    public enum EBehavior {
        BLOG_TAG("点击标签", "blog_tag"),
        BLOG_SORT("点击博客分类", "blog_sort"),
        BLOG_CONTNET("点击博客", "blog_content"),
        BLOG_PRAISE("点赞", "blog_praise"),
        FRIENDSHIP_LINK("点击友情链接", "friendship_link"),
        BLOG_SEARCH("点击搜索", "blog_search"),
        STUDY_VIDEO("点击学习视频", "study_video"),
        VISIT_PAGE("访问页面", "visit_page"),
        VISIT_SORT("点击归档", "visit_sort"),
        BLOG_AUTHOR("点击作者", "blog_author"),
        PUBLISH_COMMENT("发表评论", "publish_comment"),
        DELETE_COMMENT("删除评论", "delete_comment"),
        REPORT_COMMENT("举报评论", "report_comment"),
        VISIT_CLASSIFY("点击分类", "visit_classify");
        private String content;
        private String behavior;
        private EBehavior(String content, String behavior) {
            this.content = content;
            this.behavior = behavior;
        }
        /**
         * 根据value返回枚举类型，主要在switch中使用
         * @param value
         * @return
         */
        public static EBehavior getByValue(String value) {
            for(EBehavior behavior: values()) {
                if(behavior.getBehavior() == value) {
                    return behavior;
                }
            }
            return null;
        }
        public static Map getModuleAndOtherData(EBehavior behavior, Map nameAndArgsMap, String bussinessName) {
            String otherData = "";
            String moduleUid = "";
            switch (behavior) {
                case BLOG_AUTHOR: {
                    // 判断是否是点击作者
                    if(nameAndArgsMap.get(BaseSysConf.AUTHOR) != null) {
                        otherData = nameAndArgsMap.get(BaseSysConf.AUTHOR).toString();
                    }
                };break;
                case BLOG_SORT: {
                    // 判断是否点击博客分类
                    if(nameAndArgsMap.get(BaseSysConf.BLOG_SORT_UID) != null) {
                        moduleUid = nameAndArgsMap.get(BaseSysConf.BLOG_SORT_UID).toString();
                    }
                };break;
                case BLOG_TAG: {
                    // 判断是否点击博客标签
                    if(nameAndArgsMap.get(BaseSysConf.TAG_UID) != null) {
                        moduleUid = nameAndArgsMap.get(BaseSysConf.TAG_UID).toString();
                    }
                };break;
                case BLOG_SEARCH: {
                    // 判断是否进行搜索
                    if(nameAndArgsMap.get(BaseSysConf.KEYWORDS) != null) {
                        otherData = nameAndArgsMap.get(BaseSysConf.KEYWORDS).toString();
                    }
                };break;
                case VISIT_CLASSIFY: {
                    // 判断是否点击分类
                    if(nameAndArgsMap.get(BaseSysConf.BLOG_SORT_UID) != null) {
                        moduleUid = nameAndArgsMap.get(BaseSysConf.BLOG_SORT_UID).toString();
                    }
                };break;
                case VISIT_SORT: {
                    // 判断是否点击归档
                    if(nameAndArgsMap.get(BaseSysConf.MONTH_DATE) != null) {
                        otherData = nameAndArgsMap.get(BaseSysConf.MONTH_DATE).toString();
                    }
                };break;
                case BLOG_CONTNET: {
                    // 判断是否博客详情
                    if(nameAndArgsMap.get(BaseSysConf.UID) != null) {
                        moduleUid = nameAndArgsMap.get(BaseSysConf.UID).toString();
                    }
                };break;
                case BLOG_PRAISE: {
                    // 判断是否给博客点赞
                    if(nameAndArgsMap.get(BaseSysConf.UID) != null) {
                        moduleUid = nameAndArgsMap.get(BaseSysConf.UID).toString();
                    }
                };break;
                case VISIT_PAGE: {
                    // 访问页面
                    otherData = bussinessName;
                };break;
                case PUBLISH_COMMENT: {
                    Object object = nameAndArgsMap.get(BaseSysConf.COMMENT_VO);
                    Map map = JsonUtils.objectToMap(object);
                    if(map.get(BaseSysConf.CONTENT) != null) {
                        otherData = map.get(BaseSysConf.CONTENT).toString();
                    }
                };break;
                case REPORT_COMMENT: {
                    // 举报评论
                    Object object = nameAndArgsMap.get(BaseSysConf.COMMENT_VO);
                    Map map = JsonUtils.objectToMap(object);
                    if(map.get(BaseSysConf.CONTENT) != null) {
                        otherData = map.get(BaseSysConf.CONTENT).toString();
                    }
                };break;
                case DELETE_COMMENT: {
                    // 删除评论
                    Object object = nameAndArgsMap.get(BaseSysConf.COMMENT_VO);
                    Map map = JsonUtils.objectToMap(object);
                    if(map.get(BaseSysConf.CONTENT) != null) {
                        otherData = map.get(BaseSysConf.CONTENT).toString();
                    }
                };break;
            }
            Map result = new HashMap<>();
            result.put(BaseSysConf.MODULE_UID, moduleUid);
            result.put(BaseSysConf.OTHER_DATA, otherData);
            return result;
        }
        public String getContent() {
            return content;
        }
        public void setContent(String content) {
            this.content = content;
        }
        public String getBehavior() {
            return behavior;
        }
        public void setBehavior(String behavior) {
            this.behavior = behavior;
        }
    }
编写AOP代码
-------
在AOP中，我们使用环绕通知的方式，来收集用户的访问日志
    package com.moxi.mogublog.web.log;
    import com.moxi.mogublog.utils.AopUtils;
    import com.moxi.mogublog.utils.AspectUtil;
    import com.moxi.mogublog.utils.IpUtils;
    import com.moxi.mogublog.web.global.SysConf;
    import com.moxi.mogublog.xo.entity.ExceptionLog;
    import com.moxi.mogublog.xo.entity.SysLog;
    import com.moxi.mogublog.xo.service.WebVisitService;
    import com.moxi.mougblog.base.enums.EBehavior;
    import com.moxi.mougblog.base.holder.RequestHolder;
    import com.moxi.mougblog.base.util.RequestUtil;
    import lombok.extern.slf4j.Slf4j;
    import org.aspectj.lang.ProceedingJoinPoint;
    import org.aspectj.lang.annotation.Around;
    import org.aspectj.lang.annotation.Aspect;
    import org.aspectj.lang.annotation.Pointcut;
    import org.springframework.beans.factory.annotation.Autowired;
    import org.springframework.stereotype.Component;
    import javax.servlet.http.HttpServletRequest;
    import java.lang.reflect.Method;
    import java.util.Map;
    /**
     * 日志切面
     */
    @Aspect
    @Component
    @Slf4j
    public class LoggerAspect {
        private SysLog sysLog;
        private ExceptionLog exceptionLog;
        @Autowired
        private WebVisitService webVisitService;
        @Pointcut(value = "@annotation(bussinessLog)")
        public void pointcut(BussinessLog bussinessLog) {
        }
        @Around(value = "pointcut(bussinessLog)")
        public Object doAround(ProceedingJoinPoint joinPoint, BussinessLog bussinessLog) throws Throwable {