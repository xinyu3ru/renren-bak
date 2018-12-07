## renren-bak
人人网资料备份python脚本 write by rublog 2018.01.28已失效
===================

通过运行本脚本来保存人人网上的说说、博客文章、相册照片

仅此而已。

运行需要安装的软件：

* Python 3.5 +（理论上3.3之后的版本应该都行，我调试的版本是windows 8.1 64位，python 3.5 32位）

* 依赖：pypi requests   实现cookie的快速管理

* 依赖：pypi tqdm   实现快速的进度条显示


![开始界面](https://github.com/xinyu3ru/renren-bak/blob/master/pic/021316_1319_201602136.png "开始界面")

![保存界面](https://github.com/xinyu3ru/renren-bak/blob/master/pic/021316_1319_201602137.png "保存界面")

[可以到我的博客上看更多一点图片](http://www.rxx0.com/motion/ren-ren-wang-bei-fen-2016-02-13-python-3-5.html)<br>



2017.02.17 
update by [NewFuture](https://github.com/NewFuture)
bug fix 
>cls 清屏(linux clear)
>密码明文
>解码方式太原始粗暴了 😂 (导致解析BUG)
>blog的失效图片链接网络异常，会直接崩溃

2016.03.08 增加保存单个朋友资料功能，并把备份的文件放置于“人人网xxx资料备份xxxx-xx-xx”文件夹下面
           更新因为突然想保存某个朋友的相片
           
           
2018.01.28 脚本已经失效，研究了一个小时，没有太大进展，不想再更新


           人人网仍然没有使用ssl加密，不过改登录模式为ajax方式登录，登录页面改为http://www.renren.com/ajaxLogin/login?1=1&uniqueTimestamp=2018001123570


timestamp组成为  
           'try{var s=new Date;e=e+"&uniqueTimestamp="+s.getFullYear()+s.getMonth()+s.getDay()+s.getHours()+s.getSeconds()+s.getUTCMilliseconds()'



           登录成功不返回response 或者隐藏response，response的url也为空，原来通过返回的url判断成功失败的方法失效
         
         
         
2018.12.07 
Update by [bitdust](https://github.com/bitdust)
           1. 修复抓取用户名中多余空格
           2. 图片无标题带来的程序崩溃
           PS：根据我的测试，没有遇到您 readme 中提到的 ajax 登录问题。似乎是人人网又把登录方式改回来了。这个 renren-bak 项目又可以正常使用了。
