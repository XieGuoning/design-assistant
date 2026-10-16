# 室内设计云端工作环境


状态：配置文件已准备；已上传 GitHub；尚未安装到云端或发布，尚未完成软件兼容性实测。


## 用途


配合本地 AutoCAD 2027、SketchUp、Carat 使用，处理图纸交换文件、材料清单、预算数据和客户提案。此仓库不安装这些桌面软件，也不包含其授权或厂家目录。


## 部署


1. 在 GitHub 创建私有仓库 interior-design-workspace，勾选添加 README。
2. 将本目录文件上传到仓库根目录。不要上传本地虚拟环境。
3. 在 ChatGPT 设置 → Codex Cloud → Environments → Create environment 中选择该仓库。
4. 将下列要求交给环境配置会话：


> 请配置此仓库作为室内设计辅助环境。读取 AGENTS.md，运行 bash setup.sh。检查中文字体和 PDF 渲染工具；需要时安装 Noto CJK 字体、Poppler，以及用于办公文档预览的 LibreOffice。验证 Python 依赖导入成功，创建并重新读取一个 R2018 DXF 样例，确认版本为 AC1032。验证中文文档预览无乱码。记录依赖版本及检查结果，将安装命令保存到 Install script；给后续任务说明使用 .venv/bin/python。不要启动不需要的常驻服务。遇到权限或网络限制时报告具体原因。全部通过后提供发布前检查结果。


5. 检查结果并保存配置，选择 Publish，看到 Environment published 才算部署完成。
6. 首个任务使用非客户敏感的测试图纸，与本地 AutoCAD 2027 比对单位、尺寸、图层和文字显示。


## 文件交换


- AutoCAD 2027：云端交换默认使用当前 ezdxf 支持的 R2018 DXF（AC1032），软件版本与文件格式版本分别记录。ezdxf 本身不直接读写 DWG；DWG 原件保留在本地，另存 DXF 后处理。复杂块、字体、外部参照须回到原软件检查。
- SketchUp：先确认具体版本和许可支持的导出格式，再决定采用 DXF 或其他交换格式。导出和导入单位必须一致。
- Carat：具体产品、版本及导出能力待确认。先使用该版本实际支持的 PDF、图片或表格导出，不推断可直接修改原生工程文件。
- 中文文字、线型和打印样式：实际验收以用户本地软件打开和打印预览为准。


## 使用示例


“读取 inputs 中的 DXF，列出图层、绘图单位及闭合区域；缺少比例或单位时先询问。输出面积明细及无法确定的项目，不修改原文件。”


“根据提供的报价单整理材料清单，分开显示数量、单价、损耗、税费与来源，缺失价格留空，不编造价格。”


## 参考


- https://learn.chatgpt.com/docs/environments/cloud-environments
- https://ezdxf.readthedocs.io/en/stable/introduction.html
- https://help.sketchup.com/en/sketchup/importing-and-exporting-cad-files

