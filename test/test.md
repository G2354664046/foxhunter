## 2. 执行命令
```bash
python test/run_api_tests.py
```
可选参数：
```bash
python test/run_api_tests.py --base-url http://localhost:8000 --timeout 15 --wait-seconds 25
```
```bash
python test/run_api_tests.py --basename api_test_report_20260410_025457
```


字段名称	描述
标识符	    TE001
测试项	    用户登录系统用例
测试环境要求	后端服务已启动（http://localhost:8000），数据库可用，已存在可登录账户
输入标准	正向：正确用户名与密码访问 /api/v1/auth/login；反向：正确用户名与错误密码
输出标准	正向：返回200与JWT；反向：返回401，提示用户名或密码错误
测试结果	待执行
测试用例间关系	依赖TE002先成功创建账户

字段名称	描述
标识符	    TE002
测试项	    用户注册系统用例
测试环境要求	后端服务已启动，数据库连接正常
输入标准	正向：未被占用用户名、邮箱、合法密码提交 /api/v1/auth/register；反向：重复用户名或邮箱再次注册
输出标准	正向：返回200并新增用户；反向：返回400，提示 Username or email already exists
测试结果	待执行
测试用例间关系	可作为TE001与其他鉴权用例前置条件

字段名称	描述
标识符	    TE003
测试项	    获取当前用户信息用例
测试环境要求	后端服务已启动
输入标准	正向：Authorization: Bearer <有效token> 访问 /api/v1/auth/me；反向：不带Token或 Bearer invalid_token 访问
输出标准	正向：返回200与当前用户信息；反向：返回401未授权或凭证校验失败
测试结果	待执行
测试用例间关系	依赖TE001获取有效token

字段名称	描述
标识符	    TE004
测试项	    样本文件上传并触发异步检测用例
测试环境要求	后端与Celery Worker已启动，Redis可用，用户已登录
输入标准	正向：上传 .exe/.dll/.bin 至 /api/v1/upload；反向：上传 .txt 等非法扩展名
输出标准	正向：返回200与 sample_id/task_id；反向：返回400，提示仅支持指定格式
测试结果	待执行
测试用例间关系	依赖TE001（登录）；输出ID供TE005、TE006、TE007使用

字段名称	描述
标识符	    TE005
测试项	    查询单个样本检测结果用例
测试环境要求	后端服务已启动，用户已登录
输入标准	正向：访问 /api/v1/result/{有效ID}；反向：访问 /api/v1/result/{不存在ID}
输出标准	正向：返回200，含 status 与检测结果；反向：返回404，Sample not found
测试结果	待执行
测试用例间关系	有效ID依赖TE004生成

字段名称	描述
标识符	    TE006
测试项	    查询当前用户样本记录列表用例
测试环境要求	后端服务已启动
输入标准	正向：携带有效Token访问 /api/v1/samples；反向：不带Authorization或 Bearer invalid_token
输出标准	正向：返回200与样本列表；反向：返回401
测试结果	待执行
测试用例间关系	可依赖TE004生成数据；与TE007联动验证删除后列表

字段名称	描述
标识符	    TE007
测试项	    删除指定样本记录用例
测试环境要求	后端服务已启动，用户已登录
输入标准	正向：DELETE /api/v1/samples/{有效ID}；反向：DELETE /api/v1/samples/{不存在ID}
输出标准	正向：返回204或200且记录删除；反向：返回404，Sample not found
测试结果	待执行
测试用例间关系	有效ID依赖TE004；删除后可回查TE006

字段名称	描述
标识符	    TE008
测试项	    URL安全检测用例
测试环境要求	后端服务已启动，网络可访问URLhaus（若需在线检测）
输入标准	正向：GET /api/v1/url/scan?url=<非空URL>；反向：?url= 为空
输出标准	正向：返回200与检测结果（未配 key 时可能503）；反向：返回400，提示提供URL
测试结果	待执行
测试用例间关系	可独立执行

字段名称	描述
标识符	    TE009
测试项	    文件Hash情报查询用例
测试环境要求	后端服务已启动，网络可访问VirusTotal（若需在线检测）
输入标准	正向：GET /api/v1/hash/scan?file_hash=<非空哈希>；反向：?file_hash= 为空
输出标准	正向：返回200与情报（未配 key 时可能503）；反向：返回400，提示 file_hash 必填
测试结果	待执行
测试用例间关系	可独立执行

字段名称	描述
标识符	    TE010
测试项	    健康检查接口用例
测试环境要求	后端服务已启动
输入标准	正向：访问 /api/v1/health；反向：后端未启动或地址错误（无法建立连接）
输出标准	正向：返回200，status 为 healthy；反向：请求失败或返回5xx
测试结果	待执行
测试用例间关系	可作为所有接口测试前置冒烟检查
