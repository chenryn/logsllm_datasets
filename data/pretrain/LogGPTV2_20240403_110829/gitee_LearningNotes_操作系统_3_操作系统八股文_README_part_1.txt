# 	操作系统
**并发和并行**
并发是指**一个处理器**同时处理多个任务。
并行是指**多个处理器**或者是多核的处理器同时处理多个不同的任务。
并发是逻辑上的同时发生（simultaneous），而并行是物理上的同时发生。
**并行(parallel)**：指在同一时刻，有多条指令在多个处理器上同时执行。就好像两个人各拿一把铁锨在挖坑，一小时后，每人一个大坑。所以无论从微观还是从宏观来看，二者都是一起执行的。
**并发(concurrency)**：指在同一时刻只能有一条指令执行，但多个进程指令被快速的轮换执行，使得在宏观上具有多个进程同时执行的效果，但在微观上并不是同时执行的，只是把时间分成若干段，使多个进程快速交替的执行。这就好像两个人用同一把铁锨，轮流挖坑，一小时后，两个人各挖一个小一点的坑，要想挖两个大一点得坑，一定会用两个小时。
并行在多处理器系统中存在，而并发可以在单处理器和多处理器系统中都存在，并发能够在单处理器系统中存在是因为并发是并行的假象，并行要求程序能够同时执行多个操作，而并发只是要求程序假装同时执行多个操作（每个小时间片执行一个操作，多个操作快速切换执行）。
操作系统的功能
- 进程管理
- 内存管理：提高内存利用率和访问速度，从而提高计算机的运行效率
- 文件管理
- IO设备管理：设备无关性，将设备抽象成逻辑设备
分成外核与内核模式的原因：
- 保证操作系统受其他系统异常故障的影响；内核模式只能运行操作系统的程序，用户程序运行在外核中；
- 确保可能引起系统崩溃的指令（特权指令）只能在内核模式下运行；
- 为了防止非法IO，将所有IO指令定义为特权指令
- 设置中断，一定时间后将控制权返回给操作系统
###### **进程和线程的区别**
进程，是计算机中的程序关于某数据集合上的一次运行活动，是系统进行资源分配和调度的基本单位
在执行一些细小任务时，本身无需分配单独资源时(多个任务共享同一组资源即可，比如所有子进程共享父进程的资源)，进程的实现机制依然会繁琐的将资源分割，这样造成浪费，而且还消耗时间。后来就有了专门的多任务技术被创造出来——线程。
**共同点**：在多任务程序中，子进程(子线程)的调度一般与父进程(父线程)平等竞争。在早期的Linux内核中，线程的实现和管理方式就是**完全按照进程方式实现的**。在2.6版内核以后才有了单独的线程实现。
**实现方法的差异**：进程的个体间是完全独立的，而线程间是彼此依存的。多进程环境中，任何一个进程的终止，不会影响到其他进程。而多线程环境中，父线程终止，全部子线程被迫终止(没有了资源)。而任何一个子线程终止一般不会影响其他线程，除非**子线程执行了exit()系统调用**。任何一个子线程执行exit()，全部线程同时灭亡。
- 从系统实现角度讲，进程的实现是调用fork系统调用：pid_t fork(void)；线程的实现是调用clone系统调用
- fork()是将父进程的**全部资源复制给了子进程**。而线程的**clone只是复制了一小部分必要的资源**。后来操作系统还进一步优化fork实现——**写时复制技术**。在子进程需要复制资源(比如子进程执行写入动作更改父进程内存空间)时才复制，否则创建子进程时先不复制。
- 个体间辈分关系的迥异；进程的备份关系森严，在父进程没有结束前，所有的子进程都尊从父子关系；多线程间的关系没有那么严格，不管是父线程还是子线程创建了新的线程，都是共享父线程的资源，所以，都可以说是父线程的子线程，也就是只存在一个父线程，其余线程都是父线程的子线程。
**内核态线程、轻量级进程、用户态线程**
它的创建和撤消是由内核的内部需求来决定的，一个内核线程不需要
**内核态线程**：和一个用户进程联系起来。它共享内核的正文段和全局数据，具有自己的内核堆栈。内核线程的调度由于不需要经过态的转换并进行地址空间的重新映射，因此在内核线程间做上下文切换比在进程间做上下文切换快得多。
**轻量级进程**：轻量级进程是核心支持的用户线程，它在一个单独的进程中提供多线程控制。这些轻量级进程被单独的调度，可以在多个处理器上运行，**每一个轻量级进程都被绑定在一个内核线程上**，而且在它的**生命周期**这种绑定都是有效的。轻量级进程被独立调度并且共享地址空间和进程中的其它资源，但是每个LWP都应该有自己的程序计数器、寄存器集合、核心栈和用户栈。
**用户线程**：用户线程是通过线程库实现的。它们可以在没有内核参与下创建、释放和管理。内核对它们一无所知，而只是调度用户线程下的进程或者轻量级进程，这些进程再通过线程库函数来调度它们的线程。当一个进程被抢占时，它的所有用户线程都被抢占，当一个用户线程被阻塞时，它会阻塞下面的轻量级进程，如果进程只有一个轻量级进程，则它的所有用户线程都会被阻塞。
 **注意**：Linux中，每个线程都有一个task_struct，所以线程和进程可以使用同一调度器调度。如果一个task独占所有的资源，则是一个HWP，如果一个task和其它task共享部分资源，则是LWP。**clone**系统调用就是一个**创建轻量级进程**的系统调用，clone的用法和pthread_create有些相似，两者的最根本的差别在于clone是创建一个LWP，对核心是可见的，由核心调度，**而pthread_create通常只是创建一个用户线程**，对核心是不可见的，由线程库调度。
**PCB进程控制模块**
- 记录进程信息：进程标识信息、处理机状态、进程调度信息、资源分配信息
- 操作系统是根据进程控制块PCB来对并发执行的进程进行控制和管理的。
- PCB是进程存在的唯一标志
- 寄存器、堆栈指针、程序计数器、进程状态、优先级、调度的参数、父进程、cpu占用时间
**进程和程序的区别**
Program 指令的集合、是静态的概念；是持久的
Process 描述的是执行，动态的概念、包含程序、数据以及PCB；是暂时的
###### **进程之间的通信**
- 共享内存
  - 最快的速度进行方便的通信；
- 信息传递
  - 交换较少的数据；小号时间多
- 间接通信
  - 每当一个信箱有一个唯一的id
  - 仅当共享一个信箱时，才能通信
- 共享存储
  - 两个进程对共享空间的存储是互斥的
    - 基于数据结构的：共享速度慢、限制多、是一种低级通信方法
    - 基于存储区的共享，数据的形式、存放位置都是由进程控制的，是一种高级通信方式
- 管道通信
  - 某个时间只能单行通信，在内存中开辟一个固定大小的缓冲区，但是也是互斥的
  - 需要将缓冲区写满，缓冲区读满的时候才可以
  - 数据不可以重复读，所以读进程只能有一个
- 消息传递
  - 直接通信：将消息挂到对应线程的缓冲队列上，每个进程都会有自己信息缓冲队列，需要设置一些头
  - 间接通信方式：将信息挂载到中间实体，也被称为“信箱”
**线程**
引入的原因
- ​	进程操作系统开销大；将进程的两个任务分开：**分配资源**以及**调度**；对于作为调度和分派的基本单位，不同时作为拥有资源的单位，以做到“轻装上阵”； 对于拥有资源的基本单位，又不对之进行频繁的切换。
- 因此线程为CPU调度的最小单位，进程为资源分配的最小单位
线程**不拥有系统资源**，只有其运行所必需的一些数据结构：TCB, a program counter, a register set, and a stack. 它与该进程内其它线程**共享**该进程所拥有的**全部资源**。
**线程和进程的区别**
1.  进程是**资源分配**的基本单位，所有与该进程有关的资源分配情况，进程也是分配主存的基本单位，它拥有一个完整的虚拟地址空间。而线程与资源分配无关，它属于某一个进程，并与该进程内的其它线程一起共享进程的资源。 
2.  不同的进程拥有不同的虚拟地址空间，而同一进程中的多个线程共享同一地址空间。
3.  进程调度的切换将涉及到有关资源指针的保存及进程地址空间的转换等问题。而线程的切换将**不涉及资源指针**的保存和地址空间的变化。所以，线程切换的开销要比进程切换的开销小得多。
4.  进程的调度与切换都是由操作系统内核完成，而线程则既可由操作系统内核完成，也可由用户程序进行。
5.  进程可以动态创建进程。被进程创建的线程也可以创建其它线程。
6.  进程有创建、执行、消亡的生命周期。线程也有类似的生命周期
**线程模型**
- 用户线程，一对多
  - 线程在用户态中运行，运行与调度在用户空间中运行，内核无法感知，出问题无法切换，多个线程不能并发执行在多个处理器上（内核中只看到一个进程）
- 一对一模型
  - 可以并行在多个处理器上
  - 内核开销大
- 多个多模型
**进程同步**：对多个相关进程在执行次序上的协调，用于保证这种关系的相应机制称为进程同步。
进程间通信问题
- 竞争：竞争共享资源，导致运行的结果和进程执行的顺序相关； 解决方法：互斥，某种方法来确保如果一个进程正在使用一个共享的变量或文件，将被其他进程占用不能做同样的事情
四种必要情况去保证互斥
1. 不能有两个进程同时在临界区中
2. 不能假设CPU的速度以及数量
3. 任何运行在关键区域之外的进程都不能阻止另一个进程
4. 没有进程必须永远等待才能进入关键区域
**忙等待的互斥**
1. 屏蔽中断
   1. 每个进程刚进去临界区便屏蔽所有终端
   2. 如果屏蔽中断后忘记打开中断会导致系统的崩溃
   3. 如果系统是多处理器，屏蔽中断只会对单个cpu有效
2. 锁变量
   1. 可能会有多个进程同时进入到临界区中
3. 严格轮换法
   1. 不断测试变量直到某一个值的出现为止，称为忙等待；
   2. 在认为等待时间**非常短**的情况下，用于忙等待的锁，称为**自旋锁**
**睡眠与唤醒**:生产者和消费者问题
**信号量**：检测信号量的数值、修改变量数值都是不可分割的**原子操作**。在操作完成或者阻塞前，其他进程都是无法访问该信号量的。
**管程的引入**
信号量的缺点：用信号量可实现进程间的同步，但由于信号量的控制分布在整个序中，其正确性分析很困难
引入管程：把信号量及其操作原语封装在一个对象内部；管程是管理进程间同步的机制，它保证进程互斥地访问共享变量，并方便地阻塞和唤醒进程。
经典的进程通信问题
- 生产者消费者；等待唤醒机制
- 哲学家就餐问题；通过增加信号量，保证有一位哲学家可以吃到
- 读写问题；对资源加锁；对读者之间用锁保证互斥
CPU调度问题
首先是处理机调度算法的共同目标（就与OS的共同目标一样）：
- 资源利用率高：系统中处理机和其他资源都应尽可能的保持忙碌状态，其中最重要的资源是**处理机**；
- 公平性：诸进程都获得合理的CPU时间，不会发生进程**饥饿现象**；
- 平衡性：调度算法应当尽可能的保证系统资源使用的平衡性；
- 策略强制执行：对于所制定的策略，只要需要，就必须执行，即使会造成某些工作的延迟也要执行。
 **作业(Job)**：作业是一个比程序更为广泛的概念，它不仅包含了通常的**程序和数据**，而且还应配有一份**作业说明书**，系统根据该说明书来对程序的运行进行控制。
作业从进入系统到运行，通常需要经历**收容**、**运行**、**完成**三个阶段，其对应的作业状态分别为：**后备状态**（后备队列中）、**运行状态**（创建进程，进程的生命周期）、**完成状态**（作业运行结束或提前中断）。
**进程调度方式**：分为非抢占式和抢占式两种，主要的划分方式就是进程在正常执行的过程中（发生阻塞情况例外），处理机是否可以被抢占。
**非抢占式**：分派程序一旦把处理机分配给某进程后便让它一直运行下去，直到进程完成或发生某事件而阻塞时，才把处理机分配给另一个进程；
**抢占式**：当一个进程正在运行时，系统可以基于某种原则（优先权原则、短进程优先原则、时间片原则），剥夺已分配给它的处理机，将之分配给其它进程。
调度发生的情况
- 在创建一个进程后，需要决定是运行父进程还是子进程