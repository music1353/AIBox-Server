## Logger

* 基於logging模組再封裝

* 已設置基本config

* 快速上手使用

  ​



## Import Module

```python
import sys
sys.path.append('logger')
import logger.logging as log
```



## Get Started

```python
logger = log.Logging('test')
logger = run()
```



## Print Message

```python
# print log message
logger.debug_msg('debug message')
logger.info_msg('info message')
logger.warn_msg('warn message')
logger.error_msg('error message')
logger.critical_msg('critical message')
```



## Methods

1. Logging實例

```python
class Logging(logger_name)
```

* logger_name：此logger的名字

  ​

2. run()：設置相關config並運行

```python
def run(log_path=None)
```

* log_path：輸出log的檔案位置，默認使用logger_name為檔案名稱



3. 打印不同層級的訊息

```python
def debug_msg('debug message')
def info_msg('info message')
def warn_msg('warn message')
def error_msg('error message')
def critical_msg('critical message')
```