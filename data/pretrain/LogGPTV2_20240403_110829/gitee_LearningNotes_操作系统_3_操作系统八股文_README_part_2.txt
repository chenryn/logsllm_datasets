- 在一个进程退出时必须做调度决策
- 当一个进程阻塞在IO和信号量时，或者由于其他原因，必须选择另一个进程运行
- 在一个IO中断发生时，必须做出决策调度
批处理中的调度
- 先来先服务
- 最短作业优先
- 最短剩余作业优先（每当新的进程时间比当前的剩余时间段，则挂起当前的）；饥饿问题
交互系统中的调度
- 轮转调度：时间片划分；时间短效率低，时间长交互效果不好
- 优先级调度：在每个时钟都会降低当前进程的优先级；优先级可以**动态（随时间递减）或者静态**赋予，
  - 静态非抢占式
  - 抢占式：每次调度时选择当前已到达且优先级最高的进程。当前进程主动放弃处理机时发生调度。就是在运行进程的过程中，放弃当前进行，去进行优先级高的进程。
- 多级队列
  - ![image-20210628202032099](C:\Users\huami\AppData\Roaming\Typora\typora-user-images\image-20210628202032099.png)
- 保证调度：系统跟踪各个进程自创以来使用过多少CPU的时间
- 公平分享调度算法：对于上述的保证调度算法，是对诸进程而言体现的一定程度的公平性。但是对于**用户**来讲就不一定公平了。
- 彩票调度：权重高的进程拥有更多的票，然后随机
##### 内存管理
无内存抽象：编程时直接写死地址；这样不能同时在系统上运行两份一样程序
**地址空间**：保护和重定位；是一个进程可用于寻址内存的一套地址集合。每个进程都有自己的地址空间，并且这个地址空间是独立于其他程度的地址空间；动态重定位：用基址寄存器和界限寄存器；
**交换技术**：处理**内存超载**问题
- 直接交换：把程序完整调入内存中，使用该进程一段时间后，把它存到磁盘中
- 虚拟内存：是程序只有一部分被调入内存的情况下运行
- 会导致空洞；用内存紧缩技术会耗时
- 所需空间动态增长问题
**空闲内存管理**
- 使用位图来管理；单元越小图越大，检索连续的指定长度的空闲空间是耗时的
- 使用链表的储存管理：进程结束或者换出链表时块；
  - 下次适配算法
  - 最佳适配算法
**虚拟内存**
**虚拟存储器就是作为主存储器空间扩充的一种方式**，存储器管理把进程的全部信息放到辅存中，执行时先将其中的一部分装入主存，以后根据执行行为**随用随调入**，并且当主存中没有足够的内存空间时，存储器管理依据某些算法（页面置换算法或者是分区淘汰算法）淘汰内存中的页或者是分区。
页面:虚拟地址分为多个单元。
页帧:物理内存中相应的单元。
**内存管理单元**负责虚拟地址到物理地址的转换
逻辑地址：页号+偏移量；前面几位是页号后面几位是偏移量；用页号去页表（map）去查询得到物理地址+上偏移量就得到物理地址；
页表会保存在内存中，寄存器存页表指针
TLB寄存器：相当于给页表加个缓存，为了解决虚拟地址到物理地址的转换速度
页式管理：页号+偏移量
段式管理：段号+段长度+偏移量
段页式管理：段号+页表长度+页的偏移量（段表【页的长度+页表存放的位置】 需要三次访存：第一次是段表、第二次页表、第三次访目标单元）
​	可以引用块表，将【段号和页号】作为关键字，这样只要一次访存，依旧是直接访问目标数据
**分页的原理**
将内存划分成多个小的分区，让一个进程的代码分布在**非连续的内存地址中**，一个进程按页的大小划分后，不同片段可以分开存储，但是这样就不能使用了之前连续分配的动态重定位的方式，需要额外实现定位的方法；按页的大小划分的一个较大的好处就是减少了进程的内部碎片的问题
**局部性原理**
1. **时间局部性** ：如果程序中的某条指令一旦执行，不久以后该指令可能再次执行；如果某数据被访问过，不久以后该数据可能再次被访问。产生时间局部性的典型原因，是由于在程序中存在着大量的循环操作。
2. **空间局部性** ：一旦程序访问了某个存储单元，在不久之后，其附近的存储单元也将被访问，即程序在一段时间内所访问的地址，可能集中在一定的范围之内，这是因为指令通常是顺序存放、顺序执行的，数据也一般是以向量、数组、表等形式簇聚存储的。
针对大内存的页表
- 多级页表
  - 避免全部页表保存一直保存在内存中
- 倒排页表
  - 将虚拟地址作hash，然后根据hash值去对应槽找节点，如果有对应的（虚拟页面，页框）则找到
页面置换算法
- 最近未使用页面置换算法NRU
  - 定时将页面设置为没有被访问
    - 没有被访问，没有被修改
    - 没有被访问，已经被修改
    - 已经被访问，没有修改
    - 已经被访问，已经修改
- 先进先出
- 第二次机会页面置换算法
  - 修改FIFO，如果已经被访问，则设置为没被访问，重新进队
- 时钟置换算法
  - 循环队列，如果R（访问）为0，直接淘汰，如果为1设为0，继续向前走
- 最近最少使用LRU
  - 可以用老化算法来模拟；
  - 可以理解为每次都访问的放到队头
- 最近最不常用LFU
  - 计算访问次数
页面小
- 优点：更少的页框，更少没被使用的
- 缺点：页表大
**分段**
采用分页内存管理有一个不可避免的问题：用户视角的内存和实际物理内存的分离。用户通常更愿意将内存看做是一组**不同长度的段的集合，这些段之间并没有一定的顺序**，因此**用户通过两个量来指定地址：段号+偏移**
**分段和分页的差别**
1. 页式和段式管理策略都不会产生外部碎片，但都有可能产生内部碎片
2. 页的大小是统一的，而段的大小是可变的
3. 采用分页会导致用户视角的内存和实际内存的分离，即使用户视角的内存和实际物理内存不一样，而分段正好可以支持用户视角，使用户视角的内存和实际物理内存分布保持一致
4. 分页对程序员来说是透明的，用户指定一个地址，该地址通过硬件分为页码和偏移，这些程序员是看不见的；而分段对程序员来说通常是可见的，用户通过两个量：段号和偏移来指定地址，这两个量作为组织程序和数据的一种方便手段提供给程序员，程序员可以通过这两个量把程序和数据指定到不同的段（程序员必须清楚段的最大长度）
**文件管理**
提供文件和目录的抽象，隐藏硬件设施的复杂信息；提供文件保护
同样也有文件控制块的概念
文件名-255字符
目录：包含所有文件信息的节点集合，是根据文件名检索文件的桥梁
通过FCB再次索引，索引中只有文件名，只有真正需要采取读取FCB,再根据FCB来找出文件的存放位置
**文件跟踪**：实现文件存储就是跟踪哪些磁盘块与哪些文件一起使用。
- 连续分配
  - 容易实现；读取效率高；文件删除后会留下空洞；文件最大空间在创建时就要确定
- 链表分配
  - 没有外部碎片；文件检索简单；可以做到增长；随机访问速率低，空间不一定会填满一个空
- 索引分配
  - 只有在打开相应文件时，才需要将i-node加载到内存中。
  - 支持直接访问；没有外部碎片；索引也会占用空间开销
**文件名字的管理**
- 固定长度：浪费空间
- 线性：删除文件时会留下空洞
- 堆：需要额外的开销
**文件共享**
- 硬链接：都保存的i-node节点
  - 删除源文件时，文件并没有被删除，会导致文件一直存在（按理删了源全部都要删掉）
- 软链接：只有一个节点是保存了i-node，其他是保存”路径“
  - 需要额外的开销
#### IO
管理和控制IO操作和IO设备；主要管理IO设备和对应的控制器
**设备无关性**：应用程序独立于具体使用的物理设备；在系统中引入**逻辑设备**和**物理设备**；在应用程序中使用逻辑设备名来请求使用某类设备，而系统在实际执行中使用物理设备名；
设备驱动程序层：为内核IO子系统隐藏设别控制器的不同细节
- 将串行位流转换为字节块
- 执行必要的错误纠正
- 方便主存使用
**内存映射**：CPU如何与设备的控制器和数据缓冲区进行通信
- 每个控制寄存器都被分配一个IO端口，所有的IO端口形成IO端口空间
  - 直接访问
- 将所有控制器映射到内存空间中，每个寄存器都被分配唯一的内存空间
  - 不需要特殊的保护机制来保护控制寄存器不被用户直接访问
  - 每一条引用内存的指令也可以引用控制寄存器
  - 但是需要缓存
  - 因为只有一个地址空间，所有主内存模块和所有I/O设备控制器必须检查所有内存引用才能看到该回应哪一个呢
![image-20210729213204890](C:\Users\huami\AppData\Roaming\Typora\typora-user-images\image-20210729213204890.png)