nhentai
=======
           _   _            _        _
     _ __ | | | | ___ _ __ | |_ __ _(_)
    | '_ \| |_| |/ _ \ '_ \| __/ _` | |
    | | | |  _  |  __/ | | | || (_| | |
    |_| |_|_| |_|\___|_| |_|\__\__,_|_|

あなたも変態。 いいね?  

由于 [http://nhentai.net](http://nhentai.net) 下载下来的种子速度很慢，而且官方也提供在线观看本子的功能，所以可以利用本脚本下载本子。
### 安装

    git clone https://github.com/RicterZ/nhentai
    cd nhentai
    python setup.py install
    

### 用法
+ 下载指定 id 的本子：


    nhentai --id=123855 --download


+ 下载指定 id 列表的本子：


    nhentai --ids=123855,123866 --download
    

+ 下载某关键词第一页的本子（不推荐）：


    nhentai --search="panda" --page=1 --download


`-t, --thread` 指定下载的线程数，最多为 10 线程。  
`--path` 指定下载文件的输出路径，默认为当前目录。  
`--timeout` 指定下载图片的超时时间，默认为 30 秒。  

### License  
MIT

### あなたも変態
![](./image.jpg)