## **蓝牙OTA升级学习记录**

**直接介绍怎么用蓝牙ota，具体原理请查看STM32CubeMx_OTA文件夹**



#### **一 .用到的**

***1.硬件***

蓝牙模块**hc-05**，**stm32f102zet6**开发板（正点原子）

**2.软件**

**python文件**，**hc-05固件**（出厂自带），stm32程序



## **二.操作**

**1.配置蓝牙透传**

`AT+ORGL            // 恢复出厂设置（可选）`

`AT+NAME=YModemBT     // 设置模块名称` 

`AT+UART=115200,0,0 // 设置波特率115200`

`AT+CMODE=1         // 允许连接任意地址` 

`AT+ROLE=0          // 设为从机模式` 

`AT+PSWD=1234       // 设置配对密码（默认1234）` 

##### **2.stm32程序**

ota升级要用到两个程序烧写到flash的不同分段上，分别为bootloader和app程序。

正常状态运行app程序，当收到新的app程序时，运行bootloader进行升级。



新的app程序通过bin文件的形式通过蓝牙传给stm32

##### **2.1获取app.bin文件**

打开STM32F103rb_App1的keil工程文件，点击魔术棒，如下图，进入这个user界面，选中图中红框位置的Run #1

![f60a6104acda6763794808ff5396b525](F:\qq�ļ�-������Ϣ\������Ϣ\Tencent Files\488763619\nt_qq\nt_data\Pic\2025-03\Ori\f60a6104acda6763794808ff5396b525.png)

然后点击第二个红框的文件夹图标

图中的配置是`D:\MDK5.36\ARM\ARMCC\bin\fromelf.exe --bin --output STM32F103rb_App1\STM32F103rb_App1.bin STM32F103rb_App1\STM32F103rb_App1.axf`

1.首先是fromolf.exe路径，在MDK的文件夹里面，MDK5.36->ARM->ARMCC->bin->fromelf.exe

2.路径后面是固定的 `--bin --output` ，注意空格

3.最后是STM32F103rb_App1\STM32F103rb_App1.bin STM32F103rb_App1\STM32F103rb_App1.axf

这个STM32F103rb_App1是魔术棒里output界面的名称，注意两个文件路径中间有一个空格隔开（相对路径）

![d67ab817f862b08d51d126ba0584ebf1](F:\qq�ļ�-������Ϣ\������Ϣ\Tencent Files\488763619\nt_qq\nt_data\Pic\2025-03\Ori\d67ab817f862b08d51d126ba0584ebf1.png)

配置好之后编译，输出中有红框信息说明生成bin文件成功,或者直接到STM32F103rb_App1\STM32F103rb_App1.bin 这个相对路径下查看

![6921b60643532df675652f447be9bb1e](F:\qq�ļ�-������Ϣ\������Ϣ\Tencent Files\488763619\nt_qq\nt_data\Pic\2025-03\Ori\6921b60643532df675652f447be9bb1e.png)

![221147756cbdce549d5e85d71a51151f](F:\qq�ļ�-������Ϣ\������Ϣ\Tencent Files\488763619\nt_qq\nt_data\Pic\2025-03\Ori\221147756cbdce549d5e85d71a51151f.png)

**2.2设置代码烧写地址**

stm32程序地址从0x8000000开始，前面放bootloader,后面放app

**2.2.1设置bootloader地址**

打开bootloader程序，打开魔术棒target页面，start不变，**把size值调小**，size的大小需要可以容纳bootloader程序，另外注意不能刚刚好，因为stm32f103zet6的flash程序擦除是按页擦除的，也就是说bootloader程序的尾地址不能和app程序的首地址在同一页，所以这个地址最好是某一页的首地址。页就是一个地址块，里面是连续的地址。

![b744250096f5b16dac663c7cd21717e9](F:\qq�ļ�-������Ϣ\������Ϣ\Tencent Files\488763619\nt_qq\nt_data\Pic\2025-03\Ori\b744250096f5b16dac663c7cd21717e9.png)

**2.2.2设置app地址**

同样打开app的target界面

**app的start**是**bootloader的start** + **bootloader的size**

app的size同样也不能设置的太大，因为还要预留空间用来接收bin文件

![e8b86fb1e0f6f51c34e26239834a2096](F:\qq�ļ�-������Ϣ\������Ϣ\Tencent Files\488763619\nt_qq\nt_data\Pic\2025-03\Ori\e8b86fb1e0f6f51c34e26239834a2096.png)

#### **3.flash图示**

到这里已经设置好了 flash地址分区，下图是flash分区示意图.

![image-20250307204609054](C:\Users\48876\AppData\Roaming\Typora\typora-user-images\image-20250307204609054.png)

app1是运行区，app2是备份区，app2的最后一位地址是标志位，这个标志位在接受bin文件完成后和更新app完成后会发生变化，app程序和bootloader都可以读取到。

**4.下载程序**

![image-20250307200117316](C:\Users\48876\AppData\Roaming\Typora\typora-user-images\image-20250307200117316.png)

## **APP的下载**

![74d806b995da138ee17d2f06fb5454f9](F:\qq�ļ�-������Ϣ\������Ϣ\Tencent Files\488763619\nt_qq\nt_data\Pic\2025-03\Ori\74d806b995da138ee17d2f06fb5454f9.png)

**开始下载烧录bootloader,然后烧录app，查看串口输出**

修改app的main.c中的版本号，再次下载，看到串口输出的版本号有变化，说明可以成功下载并跳转到app.

![image-20250307200610221](C:\Users\48876\AppData\Roaming\Typora\typora-user-images\image-20250307200610221.png)

以上是用单片机的debug口下载的，后面就可以通过各种方式更新app，如串口，wifi，蓝牙等，传输协议是ymodem串口协议。

因为之前已经设置过hc-05为透传模式，所以相当于电脑和单片机之间有一个无线的串口

### **5.python程序**

下面就到最后一步，修改python的参数

我用的是pycharm<img src="C:\Users\48876\AppData\Roaming\Typora\typora-user-images\image-20250307201148748.png" alt="image-20250307201148748"  />

**安装依赖，在终端运行**

  `pip install pyserial`  

![12a46a3759fc3cd076589b7239a53859](F:\qq�ļ�-������Ϣ\������Ϣ\Tencent Files\488763619\nt_qq\nt_data\Pic\2025-03\Ori\12a46a3759fc3cd076589b7239a53859.png)

需要修改下面两块，一个是com口，一个是路径

![9ebe65a6b525149076ba84191a3ca7e0](F:\qq�ļ�-������Ϣ\������Ϣ\Tencent Files\488763619\nt_qq\nt_data\Pic\2025-03\Ori\9ebe65a6b525149076ba84191a3ca7e0.png)

**5.1.路径**

可以用**相对路径**或者**绝对路径**，绝对路径就是右键bin文件，然后复制文件地址

**5.2.COM**，（参考：[PC蓝牙加串口调试助手调试蓝牙设备_电脑蓝牙调试助手-CSDN博客](https://blog.csdn.net/louyangyang91/article/details/125374324)）

**5.2.1.右键蓝牙，转到设置**

![image-20250307201833287](C:\Users\48876\AppData\Roaming\Typora\typora-user-images\image-20250307201833287.png)

**5.2.2.点击设备**

![d80c1546778852402b36195beff271f4](F:\qq�ļ�-������Ϣ\������Ϣ\Tencent Files\488763619\nt_qq\nt_data\Pic\2025-03\Ori\d80c1546778852402b36195beff271f4.png)

**5.2.3下滑到相关设置点击  *更多蓝牙设置***

![5d115df926e7313113def0158a9608b8](F:\qq�ļ�-������Ϣ\������Ϣ\Tencent Files\488763619\nt_qq\nt_data\Pic\2025-03\Ori\5d115df926e7313113def0158a9608b8.png)

**5.2.4添加COM     点击添加后会加载一小会**

![4049eb3fc8c89036fd12938c5a0d76be](F:\qq�ļ�-������Ϣ\������Ϣ\Tencent Files\488763619\nt_qq\nt_data\Pic\2025-03\Ori\4049eb3fc8c89036fd12938c5a0d76be.png)

**5.2.5选中传出，点击浏览，选择设备，确定**

![f2b1d0ccb78cbe983474d73e7c40276b](F:\qq�ļ�-������Ϣ\������Ϣ\Tencent Files\488763619\nt_qq\nt_data\Pic\2025-03\Ori\f2b1d0ccb78cbe983474d73e7c40276b.png)

**5.2.6查看COM口  更换参数**

![5de22c37fa602003abc304a7cdc2a030](F:\qq�ļ�-������Ϣ\������Ϣ\Tencent Files\488763619\nt_qq\nt_data\Pic\2025-03\Ori\5de22c37fa602003abc304a7cdc2a030.png)

**然后点击运行，注意确保hc-05上电，并且vcc接5v,gnd，tx，rx都与单片机连接正常**

![9e11f9126ece7151ed8250521e26b85f](F:\qq�ļ�-������Ϣ\������Ϣ\Tencent Files\488763619\nt_qq\nt_data\Pic\2025-03\Ori\9e11f9126ece7151ed8250521e26b85f.png)

**运行之后，观察串口输出**

## **结语**

这只是怎么使用蓝牙ota，具体原理请查看STM32CubeMx_OTA文件夹，遇到问题联系：QQ:488763619

程序在128k，并且按页擦除的flash没问题，其他类型的单片机需要修改bootloader和 app1，app2的地址，还有标志位，我还没有在其它类型的单片机复现过，后面我应该会再写一个更详细的包含具体过程的笔记