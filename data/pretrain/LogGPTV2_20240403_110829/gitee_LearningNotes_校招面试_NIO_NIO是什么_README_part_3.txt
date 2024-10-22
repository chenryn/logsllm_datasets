    public static void main(String[] args) {
        new Thread(() -> {
            try {
                server();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }, "t1").start();
        try {
            TimeUnit.SECONDS.sleep(5);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        new Thread(() -> {
            try {
                client();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }, "t2").start();
    }
}
```
## 使用非阻塞式IO完成网络通信
```
/**
 * @author: 陌溪
 * @create: 2020-03-28-8:57
 */
public class TestNonBlockingNIODemo {
    /**
     * 客户端
     */
    public static void client() throws IOException {
        // 获取通道
        SocketChannel sChannel = SocketChannel.open(new InetSocketAddress("127.0.0.1", 9898));
        // 切换成非阻塞模式
        sChannel.configureBlocking(false);
        // 分配指定大小的缓冲区
        ByteBuffer buf = ByteBuffer.allocate(1024);
        // 发送数据给服务器
        buf.put(new Date().toString().getBytes());
        // 切换成写模式
        buf.flip();
        // 将缓冲区中的内容写入通道
        sChannel.write(buf);
        // 关闭通道
        sChannel.close();
    }
    /**
     * 服务端
     */
    public static void server() throws IOException {
        // 获取通道
        ServerSocketChannel ssChannel = ServerSocketChannel.open();
        // 切换成非阻塞模式
        ssChannel.configureBlocking(false);
        // 绑定连接
        ssChannel.bind(new InetSocketAddress(9898));
        // 获取选择器
        Selector selector = Selector.open();
        // 将通道注册到选择器上，第二个参数代表选择器监控通道的什么状态
        // 用选择器监听 接收状态，也就是说客户端什么时候发送了，我才会开始获取连接
        ssChannel.register(selector, SelectionKey.OP_ACCEPT);
        // 轮询式的获取选择器上已经准备就绪的事件
        while(selector.select() > 0) {
            // 获取当前选择器中 所有注册的选择键（已就绪的监听事件）
            Iterator it = selector.selectedKeys().iterator();
            while(it.hasNext()) {
                // 获取准备就绪的事件
                SelectionKey sk = it.next();
                // 判断是具体什么事件准备就绪
                // 接收事件就绪
                if(sk.isAcceptable()) {
                    // 若 接收就绪，获取客户端连接
                    SocketChannel sChannel = ssChannel.accept();
                    // 切换非阻塞模式
                    sChannel.configureBlocking(false);
                    // 将该通道注册到选择器上，并监听读就绪状态
                    sChannel.register(selector, SelectionKey.OP_READ);
                } else if(sk.isReadable()) {
                    // 读就绪状态就绪
                    // 获取当前选择器上 读就绪 状态的通道
                    SocketChannel sChannel = (SocketChannel) sk.channel();
                    // 读取数据
                    ByteBuffer buf = ByteBuffer.allocate(1024);
                    int len = 0;
                    while((len = sChannel.read(buf)) > 0) {
                        // 切换成读取模式
                        buf.flip();
                        // 打印客户端的发送
                        System.out.println(Thread.currentThread().getName() + "\t  " + new String(buf.array(), 0, len));
                        // 清空缓存
                        buf.clear();
                    }
                }
            }
            // 操作执行完成后，需要将 选择键给取消 SelectionKey
            it.remove();
        }
    }
    public static void main(String[] args) {
        new Thread(() -> {
            try {
                server();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }, "t1").start();
        // 十个客户端发送数据过去
        for (int i = 0; i  {
                try {
                    client();
                    try {
                        TimeUnit.SECONDS.sleep(1);
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }, String.valueOf(i)).start();
        }
    }
}
```
## 使用非阻塞式IO制作聊天室
我们只需要把上面的代码稍微改一下，就能够实现聊天室的功能了
首先创建一个服务端，然后启动
```
/**
 * 使用非阻塞IO制作聊天室  服务端
 * @author: 陌溪
 * @create: 2020-03-28-8:57
 */
public class ChatServerDemo {
    /**
     * 服务端
     */
    public static void server() throws IOException {
        // 获取通道
        ServerSocketChannel ssChannel = ServerSocketChannel.open();
        // 切换成非阻塞模式
        ssChannel.configureBlocking(false);
        // 绑定连接
        ssChannel.bind(new InetSocketAddress(9898));
        // 获取选择器
        Selector selector = Selector.open();
        // 将通道注册到选择器上，第二个参数代表选择器监控通道的什么状态
        // 用选择器监听 接收状态，也就是说客户端什么时候发送了，我才会开始获取连接
        ssChannel.register(selector, SelectionKey.OP_ACCEPT);
        // 轮询式的获取选择器上已经准备就绪的事件
        while(selector.select() > 0) {
            // 获取当前选择器中 所有注册的选择键（已就绪的监听事件）
            Iterator it = selector.selectedKeys().iterator();
            while(it.hasNext()) {
                // 获取准备就绪的事件
                SelectionKey sk = it.next();
                // 判断是具体什么事件准备就绪
                // 接收事件就绪
                if(sk.isAcceptable()) {
                    // 若 接收就绪，获取客户端连接
                    SocketChannel sChannel = ssChannel.accept();
                    // 切换非阻塞模式
                    sChannel.configureBlocking(false);
                    // 将该通道注册到选择器上，并监听读就绪状态
                    sChannel.register(selector, SelectionKey.OP_READ);
                } else if(sk.isReadable()) {
                    // 读就绪状态就绪
                    // 获取当前选择器上 读就绪 状态的通道
                    SocketChannel sChannel = (SocketChannel) sk.channel();
                    // 读取数据
                    ByteBuffer buf = ByteBuffer.allocate(1024);
                    int len = 0;
                    while((len = sChannel.read(buf)) > 0) {
                        // 切换成读取模式
                        buf.flip();
                        // 打印客户端的发送
                        System.out.println(Thread.currentThread().getName() + "\t  " + new String(buf.array(), 0, len));
                        // 清空缓存
                        buf.clear();
                    }
                }
            }
            // 操作执行完成后，需要将 选择键给取消 SelectionKey
            it.remove();
        }
    }
    public static void main(String[] args) throws IOException {
        server();
    }
}
```
然后在创建一个客户端
```
/**
 * 使用非阻塞IO制作聊天室  客户端
 * @author: 陌溪
 * @create: 2020-03-28-8:57
 */
public class ChatClientDemo {
    /**
     * 客户端
     */
    public static void client() throws IOException {
        // 获取通道
        SocketChannel sChannel = SocketChannel.open(new InetSocketAddress("127.0.0.1", 9898));
        // 切换成非阻塞模式
        sChannel.configureBlocking(false);
        // 分配指定大小的缓冲区
        ByteBuffer buf = ByteBuffer.allocate(1024);
        // 使用输入流
        Scanner sc = new Scanner(System.in);
        while(sc.hasNext()) {
            String str = sc.next();
            // 获取输入内容
            buf.put((new Date().toString() + "\n" +str).getBytes());
            // 切换成写模式
            buf.flip();
            // 将缓冲区中的内容写入通道
            sChannel.write(buf);
            // 清空缓冲区
            buf.clear();
        }
        // 关闭通道
        sChannel.close();
    }
    public static void main(String[] args) throws IOException {
        client();
    }
}
```
然后我们需要运行两个客户端，但是IDEA默认只能运行一个，因此需要设置并行运行
打开run–>edit configuration
![image-20200328102743970](images/image-20200328102743970.png)
最后看效果
![image-20200328102743970](images/111.gif)
## 管道（Pipe）
Java NIO管道是两个线程之间的单向数据连接。Pipe有一个source通道和一个sink通道，数据会被写入到sink通道，从source通道读取。
![image-20200328104843505](images/image-20200328104843505.png)
代码：
```
/**
 * 管道
 * @author: 陌溪
 * @create: 2020-03-28-10:49
 */
public class PipeDemo {
    public static void main(String[] args) throws IOException {
        // 获取管道
        Pipe pipe = Pipe.open();
        // 将缓冲区的数据写入管道
        ByteBuffer buf = ByteBuffer.allocate(1024);
        // 发送数据（使用sink发送）
        Pipe.SinkChannel sinkChannel = pipe.sink();
        buf.put("通过单向管道发送数据".getBytes());
        buf.flip();
        sinkChannel.write(buf);
        // 读取缓冲区中的数据（使用source接收）
        Pipe.SourceChannel sourceChannel = pipe.source();
        buf.flip();
        int len = sourceChannel.read(buf);
        System.out.println(new String(buf.array(), 0, len));
        sourceChannel.close();
        sinkChannel.close();
    }
}
```