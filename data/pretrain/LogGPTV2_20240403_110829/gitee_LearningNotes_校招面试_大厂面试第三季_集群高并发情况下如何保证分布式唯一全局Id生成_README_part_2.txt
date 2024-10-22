    private final static long START_STMP = 1480166465631L;
    /**
     * 每一部分占用的位数
     */
    private final static long SEQUENCE_BIT = 12; //序列号占用的位数
    private final static long MACHINE_BIT = 5;   //机器标识占用的位数
    private final static long DATACENTER_BIT = 5;//数据中心占用的位数
    /**
     * 每一部分的最大值
     */
    private final static long MAX_DATACENTER_NUM = -1L ^ (-1L  MAX_DATACENTER_NUM || datacenterId  MAX_MACHINE_NUM || machineId 
    cn.hutool
    hutool-all
    5.3.1
```
整合
```
/**
 * 雪花算法
 *
 * @author: 陌溪
 * @create: 2020-04-18-11:08
 */
public class SnowFlakeDemo {
    private long workerId = 0;
    private long datacenterId = 1;
    private Snowflake snowFlake = IdUtil.createSnowflake(workerId, datacenterId);
    @PostConstruct
    public void init() {
        try {
            // 将网络ip转换成long
            workerId = NetUtil.ipv4ToLong(NetUtil.getLocalhostStr());
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    /**
     * 获取雪花ID
     * @return
     */
    public synchronized long snowflakeId() {
        return this.snowFlake.nextId();
    }
    public synchronized long snowflakeId(long workerId, long datacenterId) {
        Snowflake snowflake = IdUtil.createSnowflake(workerId, datacenterId);
        return snowflake.nextId();
    }
    public static void main(String[] args) {
        SnowFlakeDemo snowFlakeDemo = new SnowFlakeDemo();
        for (int i = 0; i  {
                System.out.println(snowFlakeDemo.snowflakeId());
            }, String.valueOf(i)).start();
        }
    }
}
```
得到结果
```
1251350711346790400
1251350711346790402
1251350711346790401
1251350711346790403
1251350711346790405
1251350711346790404
1251350711346790406
1251350711346790407
1251350711350984704
1251350711350984706
1251350711350984705
1251350711350984707
1251350711350984708
1251350711350984709
1251350711350984710
1251350711350984711
1251350711350984712
1251350711355179008
1251350711355179009
1251350711355179010
```
### 优缺点
#### 优点
- 毫秒数在高维，自增序列在低位，整个ID都是趋势递增的
- 不依赖数据库等第三方系统，以服务的方式部署，稳定性更高，生成ID的性能也是非常高的
- 可以根据自身业务特性分配bit位，非常灵活
#### 缺点
- 依赖机器时钟，如果机器时钟回拨，会导致重复ID生成
- 在单机上是递增的，但由于涉及到分布式环境，每台机器上的时钟不可能完全同步，有时候会出现不是全局递增的情况，此缺点可以认为无所谓，一般分布式ID只要求趋势递增，并不会严格要求递增，90%的需求只要求趋势递增。
#### 其它补充
为了解决时钟回拨问题，导致ID重复，后面有人专门提出了解决的方案
- 百度开源的分布式唯一ID生成器 UidGenerator
- Leaf - 美团点评分布式ID生成系统