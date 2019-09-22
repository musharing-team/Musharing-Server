# gunicorn_conf.py
'''
Musharing_ser 的 Gunicorn 服务配置文件
'''
import logging
import logging.handlers
from logging.handlers import WatchedFileHandler

bind = '127.0.0.1:8080'      # 绑定ip和端口号
chdir = '/home/admin/ser/musharing_ser/'  # gunicorn要切换到的目的工作目录
timeout = 30      # 超时
daemon = True	# 后台
workers = 1    # 进程数
loglevel = 'info' # 日志级别，这个日志级别指的是错误日志的级别，而访问日志的级别无法设置
access_log_format = '%(t)s %(p)s %(h)s "%(r)s" %(s)s %(L)s %(b)s %(f)s" "%(a)s"'    #设置gunicorn访问日志格式，错误日志无法设置

"""
其每个选项的含义如下：
h          remote address
l          '-'
u          currently '-', may be user name in future releases
t          date of the request
r          status line (e.g. ``GET / HTTP/1.1``)
s          status
b          response length or '-'
f          referer
a          user agent
T          request time in seconds
D          request time in microseconds
L          request time in decimal seconds
p          process ID
"""
accesslog = "/home/admin/ser/musharing_ser/log/gunicorn_access.log"      # 访问日志文件
errorlog = "/home/admin/ser/musharing_ser/log/gunicorn_error.log"        # 错误日志文件
