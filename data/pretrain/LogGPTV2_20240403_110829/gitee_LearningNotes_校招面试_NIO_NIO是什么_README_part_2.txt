            } finally {
            }
        }
    }
}
```
- 利用直接缓冲区，完成文件复制
```
/**
 * 利用通道完成文件的复制（直接缓冲区，内存映射）
 * @author: 陌溪
 * @create: 2020-03-27-16:36
 */
public class FileCopyByDirectDemo {
    public static void main(String[] args) throws IOException {
        // 获取通道
        FileChannel inChannel = FileChannel.open(Paths.get("1.jpg"), StandardOpenOption.READ);
        FileChannel outChannel = FileChannel.open(Paths.get("2.jpg"), StandardOpenOption.WRITE, StandardOpenOption.READ, StandardOpenOption.CREATE_NEW);
        // 得到的一个内存映射文件
        // 这个的好处是，直接将文件存储在内存中了
        MappedByteBuffer inMappedBuf = inChannel.map(FileChannel.MapMode.READ_ONLY, 0, inChannel.size());
        MappedByteBuffer outMappedBuf = outChannel.map(FileChannel.MapMode.READ_WRITE, 0, inChannel.size());
        // 直接对缓冲区进行数据的读写操作
        byte [] dst = new byte[inMappedBuf.limit()];
        inMappedBuf.get(dst);
        outMappedBuf.put(dst);
        inChannel.close();
        outChannel.close();
    }
}
```
- 通道之间数据传输
  ```
  /**
   * 利用通道直接进行数据传输
   * @author: 陌溪
   * @create: 2020-03-27-16:36
   */
  public class FileCopyByChannelDemo {
      public static void main(String[] args) throws IOException {
          // 获取通道
          // 获取通道
          FileChannel inChannel = FileChannel.open(Paths.get("1.jpg"), StandardOpenOption.READ);
          FileChannel outChannel = FileChannel.open(Paths.get("2.jpg"), StandardOpenOption.WRITE, StandardOpenOption.READ, StandardOpenOption.CREATE_NEW);
          // 从 inChannel通道 到 outChannel通道
          inChannel.transferTo(0, inChannel.size(), outChannel);
          inChannel.close();
          outChannel.close();
      }
  }
  ```
### 分散读取与聚集写入
- 分散读取（Scatter）：将通道中的数据分散到多个缓冲区中
![image-20200327174630941](images/image-20200327174630941.png)
注意：按照缓冲区的顺序，写入position和limit之间的数据到Channel
下面我们定义了两个缓冲区，然后通过通道将我们的内容分别读取到两个缓冲区中，这就实现了分散读取
```
    /**
     * 分散读取
     * @throws IOException
     */
    private static void Scatteer() throws IOException {
        RandomAccessFile raf1 = new RandomAccessFile("1.txt", "rw");
        // 获取通道
        FileChannel channel = raf1.getChannel();
        // 分配指定大小的缓冲区
        ByteBuffer buf1 = ByteBuffer.allocate(10);
        ByteBuffer buf2 = ByteBuffer.allocate(1024);
        // 分散读取
        ByteBuffer[] bufs = {buf1, buf2};
        channel.read(bufs);
        for (ByteBuffer byteBuffer: bufs) {
            // 切换成读模式
            byteBuffer.flip();
        }
        System.out.println(new String(bufs[0].array(), 0, bufs[0].limit()));
        System.out.println(new String(bufs[1].array(), 0, bufs[1].limit()));
    }
```
- 聚集写入（Gather）：将多个缓冲区中的数据都聚集到通道中
```
    /**
     * 聚集写入
     * @throws IOException
     */
    private static void Gather() throws IOException {
        RandomAccessFile raf2 = new RandomAccessFile("2.txt", "rw");
        FileChannel channel2 = raf2.getChannel();
        // 分配指定大小的缓冲区
        ByteBuffer buf1 = ByteBuffer.allocate(10);
        ByteBuffer buf2 = ByteBuffer.allocate(1024);
        ByteBuffer[] bufs = {buf1, buf2};
        // 聚集写入
        channel2.write(bufs);
    }
```
### 字符集
- 编码：字符串转换成字节数组
- 解码：字节数组转换成字符串
```
/**
 * 通道字符集编码
 *
 * @author: 陌溪
 * @create: 2020-03-27-18:20
 */
public class ChannelCharsetDemo {
    public static void main(String[] args) throws CharacterCodingException {
        Charset cs1 = Charset.forName("GBK");
        // 获取编码器
        CharsetEncoder ce = cs1.newEncoder();
        // 获取解码器
        CharsetDecoder cd = cs1.newDecoder();
        CharBuffer cBuf = CharBuffer.allocate(1024);
        cBuf.put("今天天气不错");
        cBuf.flip();
        //编码
        ByteBuffer bBuf = ce.encode(cBuf);
        for(int i=0; i< 12; i++) {
            System.out.println(bBuf.get());
        }
        // 解码
        bBuf.flip();
        CharBuffer cBuf2 = cd.decode(bBuf);
        System.out.println(cBuf2.toString());
    }
}
```
## NIO的非阻塞式网络通信
传统的阻塞式IO必须等待内容获取完毕后，才能够继续往下执行
![image-20200327190553998](images/image-20200327190553998.png)
在NIO中，引入了选择器的概念，它会把每个通道都注册到选择器中，选择器的作用就是监控通道上的IO状态，但某个通道上，某个IO请求已经准备就绪时，那么选择器才会将该客户端的通道分配到服务端的一个或多个线程上
## 使用NIO完成网络通信的三个核心
- 通道（Channel）：负责连接
  - `java.nio.channels.Channel`
    - SelectableChannel
      - SocketChannel
      - ServerSocketChannel：TCP
      - DatagramChannel：UDP
    - Pipe.SinkChannel
    - Pipe.SourceChannel
- 缓冲区（Buffer）：负责数据的存取
- 选择器（Selector）：SelectableChannel的多路复用器，用于监控SelectorableChannel的IO状况
## 使用阻塞式IO完成网络通信
我们首先需要创建一个服务端，用于接收客户端请求
```
    /**
     * 服务端
     */
    public static void server() throws IOException {
        // 获取通道
        ServerSocketChannel ssChannel = ServerSocketChannel.open();
        FileChannel fileChannel = FileChannel.open(Paths.get("D:\\2.jpg"), StandardOpenOption.WRITE, StandardOpenOption.CREATE);
        // 绑定端口号
        ssChannel.bind(new InetSocketAddress(9898));
        // 获取客户端连接的通道
        SocketChannel socketChannel = ssChannel.accept();
        // 分配指定大小的缓冲区
        ByteBuffer buf = ByteBuffer.allocate(1024);
        // 读取客户端的数据，并保存到本地
        while(socketChannel.read(buf) != -1) {
            // 切换成读模式
            buf.flip();
            // 写入
            fileChannel.write(buf);
            // 清空缓冲区
            buf.clear();
        }
        // 关闭通道
        ssChannel.close();
        socketChannel.close();
        fileChannel.close();
    }
```
然后在创建客户端，发送文件
```
    public static void client() throws IOException {
        // 获取通道
        SocketChannel sChannel = SocketChannel.open(new InetSocketAddress("127.0.0.1", 9898));
        FileChannel inChannel = FileChannel.open(Paths.get("D:\\1.jpg"), StandardOpenOption.READ);
        // 分配指定大小的缓冲区
        ByteBuffer buf = ByteBuffer.allocate(1024);
        // 读取本地文件，并发送到服务端
        while (inChannel.read(buf) != -1) {
            // 切换到读数据模式
            buf.flip();
            // 将缓冲区的数据写入管道
            sChannel.write(buf);
            // 清空缓冲区
            buf.clear();
        }
        //关闭通道
        inChannel.close();
        sChannel.close();
    }
```
完整代码：
```
/**
 * 阻塞式NIO
 *
 * @author: 陌溪
 * @create: 2020-03-27-19:16
 */
public class TestBlockingDemo {
    public static void client() throws IOException {
        // 获取通道
        SocketChannel sChannel = SocketChannel.open(new InetSocketAddress("127.0.0.1", 9898));
        FileChannel inChannel = FileChannel.open(Paths.get("D:\\1.jpg"), StandardOpenOption.READ);
        // 分配指定大小的缓冲区
        ByteBuffer buf = ByteBuffer.allocate(1024);
        // 读取本地文件，并发送到服务端
        while (inChannel.read(buf) != -1) {
            // 切换到读数据模式
            buf.flip();
            // 将缓冲区的数据写入管道
            sChannel.write(buf);
            // 清空缓冲区
            buf.clear();
        }
        // 告诉客户端我发送完成了，或者切换成非阻塞模式
        sChannel.shutdownOutput();
        // 接收服务端的反馈
        int len = 0;
        while((len = sChannel.read(buf)) != -1) {
            buf.flip();
            System.out.println(new String(buf.array(), 0, len));
            buf.clear();
        }
        //关闭通道
        inChannel.close();
        sChannel.close();
    }
    /**
     * 服务端
     */
    public static void server() throws IOException {
        // 获取通道
        ServerSocketChannel ssChannel = ServerSocketChannel.open();
        FileChannel fileChannel = FileChannel.open(Paths.get("D:\\2.jpg"), StandardOpenOption.WRITE, StandardOpenOption.CREATE);
        // 绑定端口号
        ssChannel.bind(new InetSocketAddress(9898));
        // 获取客户端连接的通道
        SocketChannel socketChannel = ssChannel.accept();
        // 分配指定大小的缓冲区
        ByteBuffer buf = ByteBuffer.allocate(1024);
        // 读取客户端的数据，并保存到本地
        while(socketChannel.read(buf) != -1) {
            // 切换成读模式
            buf.flip();
            // 写入
            fileChannel.write(buf);
            // 清空缓冲区
            buf.clear();
        }
        //向客户端反馈
        buf.put("服务端数据接收成功".getBytes());
        buf.flip();
        socketChannel.write(buf);
        // 关闭通道
        ssChannel.close();
        socketChannel.close();
        fileChannel.close();
    }