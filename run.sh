cd /home/admin/ser/musharing_ser
export PATH=$PATH:/home/admin/ser/musharing_ser/venv/bin
gunicorn -b 127.0.0.1:8080 -w 1 --chdir /home/admin/ser/musharing_ser --daemon ser:app
echo Musharing_ser 服务已启动
echo 获取Gunicorn进程树: 'pstree -ap | grep gunicorn'
echo 关闭服务参考: http://www.chenxm.cc/article/561.html
echo 重启Gunicorn任务: 'kill -HUP <id>'
echo 退出Gunicorn任务: 'kill -9 <id>'
