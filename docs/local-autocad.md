# Windows 11 + AutoCAD 2027 本机桥接（待本机验证）

云端把设计需求整理成结构化 JSON，通过 GitHub Actions 手动下发；你的电脑作为自托管 Runner 执行，使用 AutoCAD COM 接口另存 DWG，并把结果与对象句柄上传为当前运行的 Artifact。代码接入不等于电脑已上线。此初版面向 Windows AutoCAD 完整版；LT 未验证。

支持新图中的直线、圆，以及现有 DWG 内按对象句柄移动。尚不支持任意自然语言直接执行、任意 LISP/命令、自动生成完整施工图、渲染预览或复杂参照打包。执行器不读取 Issue/PR 评论作为命令。

## 1. 本机准备（只需一次）

先将此 PR 合入 main。电脑安装并启动已授权的 AutoCAD 2027，完成首次启动弹窗；安装 Python 3.11 或更新版本（含 py 启动器）。在 PowerShell 中运行：

```powershell
$env:CAD_HOME = "$env:USERPROFILE\DesignAssistantCAD"
New-Item -ItemType Directory -Force "$env:CAD_HOME\inputs", "$env:CAD_HOME\outputs" | Out-Null
py -3 -m venv "$env:CAD_HOME\venv"
& "$env:CAD_HOME\venv\Scripts\python.exe" -m pip install pywin32==311
[Environment]::SetEnvironmentVariable('CAD_HOME', $env:CAD_HOME, 'User')
```

GitHub 仓库 → Settings → Actions → Runners → New self-hosted runner，选择 Windows x64，按照 GitHub 当时显示的下载、校验和注册命令执行。注册时添加标签 `autocad-2027`。注册令牌只在本机使用，不提交到仓库或聊天。

**不要安装为 Windows 后台服务**：在已登录的桌面会话内运行 `run.cmd`，让 CAD 可访问交互桌面。使用设置了 CAD_HOME 的同一个 PowerShell 窗口启动 Runner；其他窗口需重新打开以读取用户环境变量。电脑保持联网、不休眠，初次验证时保持解锁且不要同时手工操作执行器的图纸。

Runner 能执行仓库工作流，应只绑定此可信私有仓库，不接受陌生 PR 的代码。该工作流只手动触发，且仅 main 可执行；仓库写入权限也意味着可修改在电脑上运行的代码。可在 GitHub 设置 main 分支保护。无需开放入站端口。

多版本 AutoCAD 共存时，默认 COM 注册项可能指向其他版本。执行器检查版本为 25.2（2027）；不匹配会停止。可由本机确认注册项后设置 `CAD_PROGID` 为对应版本的 ProgID，不能靠修改检查强行运行别的版本。

## 2. 首次画图验证

仓库 → Actions → Local AutoCAD 2027 → Run workflow，选择 main，在 job 中粘贴：

```json
{"units":"mm","source":null,"operations":[{"type":"line","start":[0,0,0],"end":[3000,0,0]},{"type":"circle","center":[1500,1000,0],"radius":400}]}
```

这是明确以毫米为单位的测试图，不代表其他项目默认使用毫米。运行结束后下载 Artifact 中的 `result.dwg` 和 `result.json`，在 AutoCAD 中检查线长 3000、圆半径 400，确认单位和几何。JSON 返回所涉及对象句柄，后续可以据此移动对象。没有 PDF/图片预览。

同一工作流不并发运行。GitHub concurrency 只保留一个待运行任务，连续快速提交可能替换较早的待运行任务；每次等上一单结束后再提交。离线时任务可能排队，不能把已提交视为已完成。

## 3. 修改现有图纸

把待处理图的副本放进 `%CAD_HOME%\inputs\room.dwg`，文件名仅使用英文字母、数字、下划线或短横线。使用 AutoCAD LIST/对象属性核实需要移动的实体句柄；不是屏幕位置或图层名。示例（把 AB12 换成真实句柄）：

```json
{"units":"mm","source":"room.dwg","operations":[{"type":"move","handle":"AB12","offset":[100,0,0]}]}
```

坐标和偏移采用 WCS，三个数依次为 X/Y/Z。执行器检查 INSUNITS 与声明单位一致；无单位图纸先在本机确认单位。外部参照、图片和 PDF/DGN/DWF 底图会拒绝，需先人工整理独立副本。INSUNITS 检查不能替代比例、块与施工尺寸核验。

每单生成独立的 `%CAD_HOME%\outputs\<唯一编号>`，仅打开副本，不覆盖 inputs。成功文件上传私有仓库的 Actions Artifact，保留 7 天；本机输出仍保留。Git 提交不包含客户图纸。上传意味着仓库有权限的人可下载结果，客户图纸应按项目权限安排。

## 故障与停止

- Runner Offline：检查 run.cmd、网络、电源与睡眠设置。
- COM 注册/版本错误：启动并修复本机 AutoCAD 注册，确认是 2027 完整版。
- CAD 忙、弹窗或超时：查看桌面并关闭弹窗，先在本机小图测试。工作流超时 15 分钟；取消/超时不保证 AutoCAD 进程已退出，检查桌面后再重试。
- 失败目录内会有 FAILED.txt，任何残留 DWG 均不能当作成功结果；重试生成新目录。成功但上传失败时可从本机 outputs 找回结果。
- 停止远程执行：在 run.cmd 窗口按 Ctrl+C；长期停用在 GitHub 移除 Runner。

本机直接调试（在下载的仓库目录运行；不要与 Runner 同时运行）：

```powershell
& "$env:CAD_HOME\venv\Scripts\python.exe" scripts/cad_bridge.py --job examples/cad/new-drawing.json --validate-only
& "$env:CAD_HOME\venv\Scripts\python.exe" scripts/cad_bridge.py --job examples/cad/new-drawing.json
```

## 验证状态

Linux 云端验证了输入校验、路径限制与示例任务；未在 Windows/AutoCAD 2027 实机执行。首次成功运行并检查 DWG 前，状态是“代码已配置，待安装与联调”，不是“CAD 已接通”。
