# JARL 奖状计算器
> 2022 年 7 月起，JARL 奖状可使用 LoTW QSL 记录申请。

## 依赖
* Python3
* `adif_io`：`pip install adif_io`

## 使用
首先，从 Lotw / Your QSOs / Download Report 下载已确认的 QSO 日志 adif 文件：
* 调整日期以包含全部 QSO；
* 勾选“Include QSL details”选项。

双击运行 `cal_jarl.exe` 可执行文件，将 ADIF 文件拖入窗口中，按回车键。

或者，打开终端运行下面命令。
```sh
python cal_jarl.py <path-to-lotwreport.adi>
```

随后程序会自动统计 JARL 奖状情况，输出结果类似于：
```
----------JARL AWARDS STATUS----------
JCC:  total 41
JCG:  total 6
AJD:  10 / 10 : 100%
WAJA: 26 / 47 : 55%
AJA:  total 50
--------------------------------------
```

此外，还会输出以下四个表格文件，分别为 AJD、WAJA、JCC、JCG 四个奖状的 QSL 列表，可以方便的复制到 JARL 的申请表中。
* `checksheet_ajd.csv`
* `checksheet_waja.csv`
* `checksheet_jcc.csv`
* `checksheet_jcg.csv`

## 其他

`gen_list.py` 用于格式化 JARL 提供的 JCC、JCG、Ku 列表信息，生成 `no-list.json` 这个 JSON 格式的数据文件供统计脚本调用。

`pref-list.json` 为都道府县的数据文件，这个是手动整理的。

## 打包
在 `py` 文件末尾添加：
```python
os.system("pause")
```

运行命令：
```powershell
pyinstaller --add-data 'no-list.json;.' -F cal_jarl.py
```
