from pip import main
import os
from pathlib import Path
import shutil

main(['install', 'Aworda-LBot-Resource', '-t', '.',"-i","https://pypi.tuna.tsinghua.edu.cn/simple"])
Path('./aworda_lbot_resource').rename("resource")
shutil.rmtree('./aworda_lbot_resource-0.1.0.dist-info')
