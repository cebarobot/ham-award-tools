# Ham Award Tools

![Release](https://img.shields.io/github/v/release/cebarobot/ham-award-tools)
![GitHub Actions Build Executables Status](https://github.com/cebarobot/ham-award-tools/actions/workflows/build.yml/badge.svg)
![GitHub Actions Deploy Web Status](https://github.com/cebarobot/ham-award-tools/actions/workflows/deploy-pages.yml/badge.svg)
![MIT License](https://img.shields.io/github/license/cebarobot/ham-award-tools)

> A series of tools for checking amateur radio awards statics.
> 一系列用于检查业余无线电奖状的小工具。

## Web Version

Visit [https://cebarobot.github.io/ham-award-tools/](https://cebarobot.github.io/ham-award-tools/) to use the web version.

访问 [https://cebarobot.github.io/ham-award-tools/](https://cebarobot.github.io/ham-award-tools/) 使用网页版。

Web version is a pure front-end application, all data is stored in the local browser and will not be uploaded to any server.

网页版是纯前端应用，所有数据都存储在本地浏览器中，不会上传到任何服务器。

## Python Version

Click "Release" on the right to get latest executable.

点击右侧“Release”获取最新版可执行文件。

* [WAPC](http://www.mulandxc.com/index/wapc_medal_app): Worked All provinces of China. 通联全中国之省、直辖市、自治区、特别行政区奖状。
* [JARL](https://www.jarl.org/English/4_Library/A-4-2_Awards/Award_Main.htm): Japan Amateur Radio League Award Program. 日本业余无线电联盟奖状项目，包含 AJD、WAJA、JCC、JCG、AJA。
* [WCSA](https://www.wcsa.ac.cn/): Worked Chinese Schools Award. 通联中国学校业余电台奖状。

### 使用

First, download the confirmed QSO log adif file from Lotw / Your QSOs / Download Report:

* Adjust the date to include all QSOs;
* Check the "Include QSL details" option.

首先，从 Lotw / Your QSOs / Download Report 下载已确认的 QSO 日志 adif 文件：

* 调整日期以包含全部 QSO；
* 勾选“Include QSL details”选项。

Double-click to run the executable file `cal_wapc.exe` / `cal_jarl.exe` / `cal_wcsa.exe`, drag the ADIF file into the window, and press Enter.

双击运行 `cal_wapc.exe` / `cal_jarl.exe` / `cal_wcsa.exe` 可执行文件，将 ADIF 文件拖入窗口中，按回车键。

Or, open the terminal and run the following command.

或者，打开终端运行下面命令。

```sh
python cal_wapc.py <path-to-lotwreport.adi>
python cal_jarl.py <path-to-lotwreport.adi>
python cal_wcsa.py <path-to-lotwreport.adi>
```

Then the program will automatically calculate the award statistics and output the results. In addition, the program will output several csv format table files for easy copying to the award application form.

随后程序会自动统计奖状情况，并输出结果。此外，程序还会输出若干 csv 格式的表格文件，方便用户复制到奖状申请表中。

## LICENSE

MIT LICENSE
