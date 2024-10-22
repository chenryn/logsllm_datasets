    {"id":"1006","title":"祥康里 简约风格 *南户型 拎包入住 看房随时","price":"7000"}
![](http://image.moguit.cn/fd94c017b0f54fae8027cb545065dd79)
### REST低级客户端
创建项目，加入依赖
        4.0.0
        org.example
        Study_ElasticSearch_Code
        1.0-SNAPSHOT
                    org.apache.maven.plugins
                    maven-compiler-plugin
                        7
                        7
                org.elasticsearch.client
                elasticsearch-rest-client
                6.8.5
                junit
                junit
                4.12
                test
                com.fasterxml.jackson.core
                jackson-databind
                2.11.1
编写测试类
    import com.fasterxml.jackson.core.JsonProcessingException;
    import com.fasterxml.jackson.databind.ObjectMapper;
    import org.apache.http.HttpHost;
    import org.apache.http.util.EntityUtils;
    import org.elasticsearch.client.Request;
    import org.elasticsearch.client.Response;
    import org.elasticsearch.client.RestClient;
    import org.elasticsearch.client.RestClientBuilder;
    import java.io.IOException;
    import java.util.HashMap;
    import java.util.Map;
    /**
     * 使用低级客户端 访问
     *
     * @author: 陌溪
     * @create: 2020-09-23-16:33
     */
    public class ESApi {
        private RestClient restClient;
        private static final ObjectMapper MAPPER = new ObjectMapper();
        /**
         * 初始化
         */
        public void init() {
            RestClientBuilder restClientBuilder = RestClient.builder(new HttpHost("202.193.56.222", 9200, "http"));
            this.restClient = restClientBuilder.build();
        }
        /**
         * 查询集群状态
         */
        public void testGetInfo() throws IOException {
            Request request = new Request("GET", "/_cluster/state");
            request.addParameter("pretty", "true");
            Response response = this.restClient.performRequest(request);
            System.out.println(response.getStatusLine());
            System.out.println(EntityUtils.toString(response.getEntity()));
        }
        /**
         * 根据ID查询数据
         * @throws IOException
         */
        public void testGetHouseInfo() throws IOException {
            Request request = new Request("GET", "/haoke/house/Z3CduXQBYpWein3CRFug");
            request.addParameter("pretty", "true");
            Response response = this.restClient.performRequest(request);
            System.out.println(response.getStatusLine());
            System.out.println(EntityUtils.toString(response.getEntity()));
        }
        public void testCreateData() throws IOException {
            Request request = new Request("POST", "/haoke/house");
            Map data = new HashMap<>();
            data.put("id", "2001");
            data.put("title", "张江高科");
            data.put("price", "3500");
            // 写成JSON
            request.setJsonEntity(MAPPER.writeValueAsString(data));
            Response response = this.restClient.performRequest(request);
            System.out.println(response.getStatusLine());
            System.out.println(EntityUtils.toString(response.getEntity()));
        }
        // 搜索数据
        public void testSearchData() throws IOException {
            Request request = new Request("POST", "/haoke/house/_search");
            String searchJson = "{\"query\": {\"match\": {\"title\": \"拎包入住\"}}}";
            request.setJsonEntity(searchJson);
            request.addParameter("pretty","true");
            Response response = this.restClient.performRequest(request);
            System.out.println(response.getStatusLine());
            System.out.println(EntityUtils.toString(response.getEntity()));
        }
        public static void main(String[] args) throws IOException {
            ESApi esApi = new ESApi();
            esApi.init();
    //        esApi.testGetInfo();
    //        esApi.testGetHouseInfo();
            esApi.testCreateData();
        }
    }
### REST高级客户端
创建项目，引入依赖
        org.elasticsearch.client
        elasticsearch-rest-high-level-client
        6.8.5
编写测试用例
    import com.fasterxml.jackson.databind.ObjectMapper;
    import org.apache.http.HttpHost;
    import org.apache.http.util.EntityUtils;
    import org.elasticsearch.action.ActionListener;
    import org.elasticsearch.action.delete.DeleteRequest;
    import org.elasticsearch.action.delete.DeleteResponse;
    import org.elasticsearch.action.get.GetRequest;
    import org.elasticsearch.action.get.GetResponse;
    import org.elasticsearch.action.index.IndexRequest;
    import org.elasticsearch.action.index.IndexResponse;
    import org.elasticsearch.action.search.SearchRequest;
    import org.elasticsearch.action.search.SearchResponse;
    import org.elasticsearch.action.update.UpdateRequest;
    import org.elasticsearch.action.update.UpdateResponse;
    import org.elasticsearch.client.*;
    import org.elasticsearch.common.Strings;
    import org.elasticsearch.common.unit.TimeValue;
    import org.elasticsearch.index.query.QueryBuilders;
    import org.elasticsearch.search.SearchHit;
    import org.elasticsearch.search.SearchHits;
    import org.elasticsearch.search.builder.SearchSourceBuilder;
    import org.elasticsearch.search.fetch.subphase.FetchSourceContext;
    import java.io.IOException;
    import java.util.HashMap;
    import java.util.Map;
    import java.util.concurrent.TimeUnit;
    /**
     * ES高级客户端
     *
     * @author: 陌溪
     * @create: 2020-09-23-16:56
     */
    public class ESHightApi {
        private RestHighLevelClient client;
        public void init() {
            RestClientBuilder restClientBuilder = RestClient.builder(
                    new HttpHost("202.193.56.222", 9200, "http"));
            this.client = new RestHighLevelClient(restClientBuilder);
        }
        public void after() throws Exception {
            this.client.close();
        }
        /**
         * 新增文档，同步操作
         *
         * @throws Exception
         */
        public void testCreate() throws Exception {
            Map data = new HashMap<>();
            data.put("id", "2002");
            data.put("title", "南京西路 拎包入住 一室一厅");
            data.put("price", "4500");
            IndexRequest indexRequest = new IndexRequest("haoke", "house")
                    .source(data);
            IndexResponse indexResponse = this.client.index(indexRequest,
                    RequestOptions.DEFAULT);
            System.out.println("id->" + indexResponse.getId());
            System.out.println("index->" + indexResponse.getIndex());
            System.out.println("type->" + indexResponse.getType());
            System.out.println("version->" + indexResponse.getVersion());
            System.out.println("result->" + indexResponse.getResult());
            System.out.println("shardInfo->" + indexResponse.getShardInfo());
        }
        /**
         * 异步创建文档
         * @throws Exception
         */
        public void testCreateAsync() throws Exception {
            Map data = new HashMap<>();
            data.put("id", "2003");
            data.put("title", "南京东路 最新房源 二室一厅");
            data.put("price", "5500");
            IndexRequest indexRequest = new IndexRequest("haoke", "house")
                    .source(data);
            this.client.indexAsync(indexRequest, RequestOptions.DEFAULT, new
                    ActionListener() {
                        @Override
                        public void onResponse(IndexResponse indexResponse) {
                            System.out.println("id->" + indexResponse.getId());
                            System.out.println("index->" + indexResponse.getIndex());
                            System.out.println("type->" + indexResponse.getType());
                            System.out.println("version->" + indexResponse.getVersion());
                            System.out.println("result->" + indexResponse.getResult());
                            System.out.println("shardInfo->" + indexResponse.getShardInfo());
                        }
                        @Override
                        public void onFailure(Exception e) {
                            System.out.println(e);
                        }
                    });
            System.out.println("ok");
            Thread.sleep(20000);
        }
        /**
         * 查询
         * @throws Exception
         */
        public void testQuery() throws Exception {
            GetRequest getRequest = new GetRequest("haoke", "house",
                    "GkpdE2gBCKv8opxuOj12");
            // 指定返回的字段
            String[] includes = new String[]{"title", "id"};
            String[] excludes = Strings.EMPTY_ARRAY;
            FetchSourceContext fetchSourceContext =
                    new FetchSourceContext(true, includes, excludes);
            getRequest.fetchSourceContext(fetchSourceContext);
            GetResponse response = this.client.get(getRequest, RequestOptions.DEFAULT);
            System.out.println("数据 -> " + response.getSource());
        }
        /**
         * 判断是否存在
         *
         * @throws Exception
         */
        public void testExists() throws Exception {
            GetRequest getRequest = new GetRequest("haoke", "house",
                    "GkpdE2gBCKv8opxuOj12");
    // 不返回的字段
            getRequest.fetchSourceContext(new FetchSourceContext(false));
            boolean exists = this.client.exists(getRequest, RequestOptions.DEFAULT);
            System.out.println("exists -> " + exists);
        }
        /**
         * 删除数据
         *
         * @throws Exception
         */
        public void testDelete() throws Exception {
            DeleteRequest deleteRequest = new DeleteRequest("haoke", "house",
                    "GkpdE2gBCKv8opxuOj12");
            DeleteResponse response = this.client.delete(deleteRequest,
                    RequestOptions.DEFAULT);
            System.out.println(response.status());// OK or NOT_FOUND
        }
        /**
         * 更新数据
         *
         * @throws Exception
         */
        public void testUpdate() throws Exception {
            UpdateRequest updateRequest = new UpdateRequest("haoke", "house",
                    "G0pfE2gBCKv8opxuRz1y");
            Map data = new HashMap<>();
            data.put("title", "张江高科2");
            data.put("price", "5000");
            updateRequest.doc(data);
            UpdateResponse response = this.client.update(updateRequest,
                    RequestOptions.DEFAULT);
            System.out.println("version -> " + response.getVersion());
        }
        /**
         * 测试搜索
         *
         * @throws Exception
         */
        public void testSearch() throws Exception {
            SearchRequest searchRequest = new SearchRequest("haoke");
            searchRequest.types("house");
            SearchSourceBuilder sourceBuilder = new SearchSourceBuilder();
            sourceBuilder.query(QueryBuilders.matchQuery("title", "拎包入住"));
            sourceBuilder.from(0);
            sourceBuilder.size(5);
            sourceBuilder.timeout(new TimeValue(60, TimeUnit.SECONDS));
            searchRequest.source(sourceBuilder);
            SearchResponse search = this.client.search(searchRequest,
                    RequestOptions.DEFAULT);
            System.out.println("搜索到 " + search.getHits().totalHits + " 条数据.");
            SearchHits hits = search.getHits();
            for (SearchHit hit : hits) {
                System.out.println(hit.getSourceAsString());
            }
        }
        public static void main(String[] args) throws Exception {
            ESHightApi esHightApi = new ESHightApi();
            esHightApi.init();
            esHightApi.testCreate();
        }
    }
## 往期推荐
- [蘑菇博客从0到2000Star，分享我的Java自学路线图](https://mp.weixin.qq.com/s/3u6OOYkpj4_ecMzfMqKJRw)
- [从三本院校到斩获字节跳动后端研发Offer-讲述我的故事](https://mp.weixin.qq.com/s/c4rR_aWpmNNFGn-mZBLWYg)
- [陌溪在公众号摸滚翻爬半个月，整理的入门指南](https://mp.weixin.qq.com/s/Jj1i-mD9Tw0vUEFXi5y54g)
- [读者问:有没有高效的记视频笔记方法？](https://mp.weixin.qq.com/s/QcQnV1yretxmDQr4ELW7_g)
## 结语
**陌溪**是一个从三本院校一路摸滚翻爬上来的互联网大厂程序员。独立做过几个开源项目，其中**蘑菇博客**在码云上有 **2K Star** 。目前就职于**字节跳动的Data广告部门**，是字节跳动全线产品的商业变现研发团队。本公众号将会持续性的输出很多原创小知识以及学习资源。如果你觉得本文对你有所帮助，麻烦给文章点个“赞”和“在看”。同时欢迎各位小伙伴关注陌溪，让我们一起成长~
![和陌溪一起学编程](http://image.moguit.cn/824fe5738ef54a7383f6d844f2e233a5)