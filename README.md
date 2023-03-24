# shareLink2bdLink
从百度分享链接生成秒传链接的后端程序

代码写的比较简易, 仅供参考, 其他的平台自行实现

# run
  ```
  pip install -r requirements.txt
  python main.py
  ```

* 运行前先使用cookie插件: [Cookie Editor](https://cookie-editor.cgagnier.ca/#download) 导出百度网盘cookie并粘贴到 baidu_cookie.txt 内

# protocol
后端默认监听 localhost:9001 (可自行在代码中修改)

http协议发送json数据 { 'sharelink': 'https://<span></span>pan.baidu.com/s/xxx, 'pw': 'xxxx' } 到后端

后端返回的json数据格式为: { 'errno':错误码, 'msg':错误信息, 'list':[ { 'path':文件路径, 'bdlink':秒传链接, 'errno':错误码, 'msg':错误信息 } ] }

* errno=0为成功, 此时不会有'msg'字段

# preview

<img src="https://i.ibb.co/PjTNmz0/1-RL-G-IH2-JGZK966-LC-JZ23.png">