}
```
### 缓存机制
针对 Map 缓存的问题，我们使用了Redis进行改造，增加超时机制，同时可以避免node崩溃缓存击穿问题
**redis/index.js**
```javascript
import redis from 'redis';
import bluebird from 'bluebird';
bluebird.promisifyAll(redis);
const host = 'www.abc.com';
const port = 6379;
const password = '123456';
const client = redis.createClient({
    host,
    port,
    password,
    retry_strategy: function(options) {
        if (options.error && options.error.code === "ECONNREFUSED") {
            return new Error("The server refused the connection");
        }
        if (options.total_retry_time > 1000 * 60 * 60) {
            return new Error("Retry time exhausted");
        }
        if (options.attempt > 10) {
            return undefined;
        }
        return Math.min(options.attempt * 100, 3000);
    },
});
client.on("error", function(e) {
    console.error('dynamic-render redis error: ', e);
});
export default client;
```
### 样式错乱
出现这个问题的原因是：
```html
```
如果爬虫没有 js 执行能力，并不会去请求这类样式文件，所以我们需要将link标签转换为 style 标签。
这部分工作在以前可以不搞，反正主要内容已经给到爬虫了，但是现在爬虫越来越聪明，能够通过样式文件识别网站是否有作弊行为，而且如果不做这块，在百度、谷歌的快照页面看到的是错乱的页面，会降低排名，所以我们要帮爬虫安排好样式文件。
下面代码利用 puppeteer 请求样式文件，用 style 替代 link 标签。 **ssr.js**
```javascript
import puppeteer from 'puppeteer';
import redisClient from './redis/index.js';
async function ssr(url) {
    const REDIS_KEY = `ssr:${url}`;
    const CACHE_TIME = 600; // 10 分钟缓存
    const CACHE_HTML = await redisClient.getAsync(REDIS_KEY);
    if (CACHE_HTML) {
        return { html: CACHE_HTML, ttRenderMs: 0 };
    }
    const start = Date.now();
    const browser = await puppeteer.launch({
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    try {
        const page = await browser.newPage();
        const stylesheetContents = {};
        // 1. Stash the responses of local stylesheets.
        page.on('response', async resp => {
            const responseUrl = resp.url();
            const sameOrigin = new URL(responseUrl).origin === new URL(url).origin;
            const isStylesheet = resp.request().resourceType() === 'stylesheet';
            if (sameOrigin && isStylesheet) {
                stylesheetContents[responseUrl] = await resp.text();
            }
        });
        // 2. Load page as normal, waiting for network requests to be idle.
        // networkidle0 waits for the network to be idle (no requests for 500ms).
        await page.goto(url, {waitUntil: 'networkidle0'});
        await page.waitForSelector('#root'); // ensure #posts exists in the DOM.
        // 3. Inline the CSS.
        // Replace stylesheets in the page with their equivalent .
        await page.$$eval('link[rel="stylesheet"]', (links, content) => {
            links.forEach(link => {
                const cssText = content[link.href];
                if (cssText) {
                    const style = document.createElement('style');
                    style.textContent = cssText;
                    link.replaceWith(style);
                }
            });
        }, stylesheetContents);
        // 4. Get updated serialized HTML of page.
        const html = await page.content(); // serialized HTML of page DOM.
        await browser.close();
        const ttRenderMs = Date.now() - start;
        redisClient.set(REDIS_KEY, html, 'EX', CACHE_TIME); // cache rendered page.
        return {html, ttRenderMs};
    } catch (err) {
        console.error(err);
        throw new Error('render fail');
    }
}
export {ssr as default};
```
这部分代码可以参考 [google 文档](https://developers.google.com/web/tools/puppeteer/articles/ssr#inline)
### 错误渲染
渲染后的页面回到浏览器后，有时执行操作会重新加载样式文件，请求路径类似：/static/1231234sdf.css，这些路径会被当做一个页面路径，而不是静态资源进行渲染，导致渲染错误。解决方式：增加 path 匹配拦截，资源文件直接向原域名请求
```javascript
import express from 'express';
import request from 'request';
import ssr from './ssr.js';
const app = express();
const host = 'https://www.abc.com';
app.get('/static/*', async (req, res) => {
    request(`${host}${req.url}`).pipe(res);
});
app.get('/manifest.json', async (req, res) => {
    request(`${host}${req.url}`).pipe(res);
});
app.get('/favicon.ico', async (req, res) => {
    request(`${host}${req.url}`).pipe(res);
});
app.get('/logo*', async (req, res) => {
    request(`${host}${req.url}`).pipe(res);
});
app.get('*', async (req, res) => {
    const {html, ttRenderMs} = await ssr(`${host}${req.originalUrl}`);
    res.set('Server-Timing', `Prerender;dur=${ttRenderMs};desc="Headless render time (ms)"`);
    return res.status(200).send(html); // Serve prerendered page as response.
});
app.listen(8080, () => console.log('Server started. Press Ctrl + C to quit'));
```
动态渲染相比SSR有几点明显好处：
- 和 SSR 一致的 SEO 效果，通过 puppeteer 还可进一步定制 SEO 方案
- node 应用负载压力小，只需应对爬虫请求，相当于只有爬虫来了页面才做SSR
- 从整体架构上来说相当于一个插件，可随时插拔，无副作用
- 不需要大量修改SPA代码（只在重复请求问题上用一个标志位去识别，当然也可以不管这个问题）
*（重复请求只在爬虫有js执行能力时才出现，一般再次请求数据也没问题）*
## Nginx 配置
这部分配置可以参考：[这里](https://gist.github.com/thoop/8165802)
## 附录
#### 常见爬虫 user-agent
| 主体      | user-agent                          | 用途                                |
| :-------- | :---------------------------------- | :---------------------------------- |
| Google    | googlebot                           | 搜索引擎                            |
| Google    | google-structured-data-testing-tool | 测试工具                            |
| Google    | Mediapartners-Google                | Adsense广告网页被访问后，爬虫就来访 |
| Microsoft | bingbot                             | 搜索引擎                            |
| Linked    | linkedinbot                         | 应用内搜索                          |
| 百度      | baiduspider                         | 搜索引擎                            |
| 奇虎 360  | 360Spider                           | 搜索引擎                            |
| 搜狗      | Sogou Spider                        | 搜索引擎                            |
| Yahoo     | Yahoo! Slurp China                  | 搜索引擎                            |
| Yahoo     | Yahoo! Slurp                        | 搜索引擎                            |
| Twitter   | twitterbot                          | 应用内搜索                          |
| Facebook  | facebookexternalhit                 | 应用内搜索                          |
| -         | rogerbot                            | -                                   |
| -         | embedly                             | -                                   |
| Quora     | quora link preview                  | -                                   |
| -         | showyoubot                          | -                                   |
| -         | outbrain                            | -                                   |
| -         | pinterest                           | -                                   |
| -         | slackbot                            | -                                   |
| -         | vkShare                             | -                                   |
| -         | W3C_Validator                       | -                                   |
#### 模拟爬虫测试
```shell
# 不带 user-agent 返回SPA页面，html 上无数据
curl 你的网站全路径
# 模拟爬虫、返回页面应该带有 title，body 等数据，方便 SEO
curl -H 'User-agent:Googlebot' 你的网站全路径
```
#### 参考资料
【1】[构建时预渲染：网页首帧优化实践](https://tech.meituan.com/2018/11/15/first-contentful-paint-practice.html)
【2】[Implement dynamic rendering](https://developers.google.com/search/docs/guides/dynamic-rendering)
【3】[Google 抓取工具（用户代理）概览](https://support.google.com/webmasters/answer/1061943?hl=zh-Hans)