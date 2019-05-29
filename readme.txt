#tomcat服务端口
server:
  #服务端口
  port: 51216
#grpc服务端口
grpc:
  server:
    port: 10088
    threadPoolSize: 20
  threadPoolSize: 20
  client:
    local-grpc-server:
      host: 172.19.48.91
      port: 10099
sys:
  sendUrl: http://api.1cloudsp.com/api/send
  accesskey: Xk2s8RAPrWTKnxt7
  accessScrect: WjaYcCEEyT8dBL51LbrMJleFGo0s2oFZ
#日志生效配置
logging:
  config: classpath:logback-debug.xml