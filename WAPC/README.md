# WAPC 奖状计算器

## 依赖
* Python3
* `adif_io`：`pip install adif_io`

## 使用
首先，从 Lotw / Your QSOs / Download Report 下载已确认的 QSO 日志 adif 文件：
* 调整日期以包含全部 QSO；
* 勾选“Include QSL details”选项。

双击运行 `cal_wapc.exe` 可执行文件，将 ADIF 文件拖入窗口中，按回车键。

或者，打开终端运行下面命令。
```sh
python cal_wapc.py <path-to-lotwreport.adi>
```

随后程序会自动统计 WAPC 奖状情况，输出结果类似于：
```
WAPC Award Statistics
MIXED   24      70%
160M    0       0%
80M     0       0%
40M     16      47%
30M     1       2%
20M     9       26%
17M     3       8%
15M     9       26%
12M     0       0%
10M     0       0%
CW      0       0%
PHONE   0       0%
DATA    24      70%
```

此外，还会输出 `wapc_checksheet_band.csv`、`wapc_checksheet_mode.csv` 两个表格文件，分别为 WAPC 每波段和每模式的检查表。


## 打包
在 `py` 文件末尾添加：
```python
os.system("pause")
```

运行命令：
```powershell
pyinstaller -F cal_wapc.py
```
