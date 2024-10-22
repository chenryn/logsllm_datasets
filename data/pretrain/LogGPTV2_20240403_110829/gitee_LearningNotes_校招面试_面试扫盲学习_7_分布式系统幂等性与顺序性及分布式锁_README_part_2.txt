 ![02_RedLock算法](images/02_RedLock算法.png)
### ZK实现分布式锁
zk分布式锁，其实可以做的比较简单，就是某个节点尝试创建临时znode，此时创建成功了就获取了这个锁；这个时候别的客户端来创建锁会失败，只能注册个监听器监听这个锁。释放锁就是删除这个znode，一旦释放掉就会通知客户端，然后有一个等待着的客户端就可以再次重新加锁。
![03_zookeeper的分布式锁原理](images/03_zookeeper的分布式锁原理.png)
ZK实现分布式锁，就是不需要执行轮询算法，而是注册监听器，但有人释放锁的时候，会通知需要获取锁的进程。
同时ZK获取锁的时候，其实就是创建了一个临时节点，如果这个临时节点之前不存在，那么就创建成功，也就是说这个锁就是属于该线程的。
同时其它的线程会尝试创建相同名称的一个临时节点，如果已经存在，说明别人已经占有了这把锁，那么就创建失败。
一旦临时节点被删除，zk就通知别人这个锁已经被释放掉了，相当于锁被释放掉了。
假设这个时候，持有锁的服务器宕机了，那么Zookeeper会自动将该锁给释放掉。
### ZK实现分布式锁代码
```
/**
 * ZooKeeperSession
 * @author Administrator
 *
 */
public class ZooKeeperSession {
	private static CountDownLatch connectedSemaphore = new CountDownLatch(1);
	private ZooKeeper zookeeper;
private CountDownLatch latch;
	public ZooKeeperSession() {
		try {
			this.zookeeper = new ZooKeeper(
					"192.168.31.187:2181,192.168.31.19:2181,192.168.31.227:2181", 
					50000, 
					new ZooKeeperWatcher());			
			try {
				connectedSemaphore.await();
			} catch(InterruptedException e) {
				e.printStackTrace();
			}
			System.out.println("ZooKeeper session established......");
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	/**
	 * 获取分布式锁
	 * @param productId
	 */
	public Boolean acquireDistributedLock(Long productId) {
		String path = "/product-lock-" + productId;
		try {
			zookeeper.create(path, "".getBytes(), 
					Ids.OPEN_ACL_UNSAFE, CreateMode.EPHEMERAL);
return true;
		} catch (Exception e) {
while(true) {
				try {
Stat stat = zk.exists(path, true); // 相当于是给node注册一个监听器，去看看这个监听器是否存在
if(stat != null) {
this.latch = new CountDownLatch(1);
this.latch.await(waitTime, TimeUnit.MILLISECONDS);
this.latch = null;
}
zookeeper.create(path, "".getBytes(), 
						Ids.OPEN_ACL_UNSAFE, CreateMode.EPHEMERAL);
return true;
} catch(Exception e) {
continue;
}
}
// 很不优雅，我呢就是给大家来演示这么一个思路
// 比较通用的，我们公司里我们自己封装的基于zookeeper的分布式锁，我们基于zookeeper的临时顺序节点去实现的，比较优雅的
		}
return true;
	}
	/**
	 * 释放掉一个分布式锁
	 * @param productId
	 */
	public void releaseDistributedLock(Long productId) {
		String path = "/product-lock-" + productId;
		try {
			zookeeper.delete(path, -1); 
			System.out.println("release the lock for product[id=" + productId + "]......");  
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	/**
	 * 建立zk session的watcher
	 * @author Administrator
	 *
	 */
	private class ZooKeeperWatcher implements Watcher {
		public void process(WatchedEvent event) {
			System.out.println("Receive watched event: " + event.getState());
			if(KeeperState.SyncConnected == event.getState()) {
				connectedSemaphore.countDown();
			} 
if(this.latch != null) {  
this.latch.countDown();  
}
		}
	}
	/**
	 * 封装单例的静态内部类
	 * @author Administrator
	 *
	 */
	private static class Singleton {
		private static ZooKeeperSession instance;
		static {
			instance = new ZooKeeperSession();
		}
		public static ZooKeeperSession getInstance() {
			return instance;
		}
	}
	/**
	 * 获取单例
	 * @return
	 */
	public static ZooKeeperSession getInstance() {
		return Singleton.getInstance();
	}
	/**
	 * 初始化单例的便捷方法
	 */
	public static void init() {
		getInstance();
	}
}
```
### Redis分布式锁和ZK分布式锁
redis分布式锁，其实需要自己不断去尝试获取锁，比较消耗性能
 zk分布式锁，获取不到锁，注册个监听器即可，不需要不断主动尝试获取锁，性能开销较小
 另外一点就是，如果是redis获取锁的那个客户端bug了或者挂了，那么只能等待超时时间之后才能释放锁；而zk的话，因为创建的是临时znode，只要客户端挂了，znode就没了，此时就自动释放锁
 redis分布式锁大家每发现好麻烦吗？遍历上锁，计算时间等等。。。zk的分布式锁语义清晰实现简单
 所以先不分析太多的东西，就说这两点，我个人实践认为zk的分布式锁比redis的分布式锁牢靠、而且模型简单易用