# design-assistant · 室内设计、效果图与 DRAENERT 资料助手

从 [interior-design-workspace](https://github.com/XieGuoning/interior-design-workspace) 迁移室内设计配置，并增加模型图转效果图工作流程。

同时提供 DRAENERT 官网产品、材料及官方 CAD／3DS 下载入口的本地资料库，供选型、尺寸核对和设计搭配使用。

## 能做什么
| 工作 | 配置与入口 |
| --- | --- |
| CAD 图纸交换 | ezdxf，默认 R2007 DXF（AC1021），核对图层、单位与闭合边界 |
| 材料与预算 | openpyxl，Excel 清单、公式、损耗与税费 |
| 客户方案 | python-docx、python-pptx、pypdf，Word、PPT、PDF |
| 图片与统计图 | Pillow、Matplotlib |
| 模型图转效果图 | 模型截图/白模/线稿 + 风格要求 → 会话图像编辑工具 → 写实效果图与结构复核 |
| DRAENERT 产品与材料检索 | 400 个产品／材料条目、官网来源存档、官方 CAD／3DS 入口与尺寸依据 |

这些是辅助工具和任务流程，不包含 AutoCAD、SketchUp、Carat 桌面软件，也不直接编辑其未验证的原生工程文件。DWG 请先在原软件导出 DXF；模型请先导出 PNG/JPEG/WebP 视图。

## 安装
在 Linux 云端环境的仓库根目录运行：

```bash
bash setup.sh
```

后续使用 `.venv/bin/python`。脚本安装继承的依赖，测试 R2007 DXF 写入/读回，并创建 `inputs/`、`work/`、`outputs/`。中文字体、Poppler、LibreOffice 按环境权限另行安装和检查。

**安装 Python 依赖不会安装或开启图像生成模型。** 模型图转效果图优先使用当前会话已有的图像生成/编辑工具；没有该工具的环境只能整理渲染准备包，不能直接出图。仓库变更不代表云端环境已重新安装或发布。

## 模型图转效果图
将原图放入 `inputs/`，然后发出：

> 将 inputs/living-room.png 转为自然写实的室内效果图。保持原视角、门窗、柜体、家具位置和比例，使用浅橡木、米白墙面与柔和日光。输出到 outputs/renders/，并检查是否有结构偏移。

完整流程见 [模型图转效果图说明](docs/model-to-render.md)。需要准备提示词和输入清单时：

```bash
.venv/bin/python scripts/prepare_render.py --image inputs/living-room.png --style "现代简约" --materials "浅橡木、米白墙面" --lighting "柔和日光" --out work/living-room-render
```

如有材质/风格参考图，增加 `--reference inputs/style.jpg`（可重复）。准备脚本只生成 `prompt.txt` 和 `manifest.json`，不调用外部服务、不收费、不生成图片。

## 输入输出
- `inputs/`：输入副本，保留原件。
- `work/`：中间文件、准备包与安装记录。
- `outputs/`：最终图纸、文档和效果图。
- 以上目录均不上传 Git；交付文件需另行保存。

## 验证状态
- 本仓库提供配置、安装自检脚本和模型图准备工具。
- 2026-10-06 当前云端实例已验证依赖、R2007 DXF、中文 Office／PDF 预览和模型图准备包；用户模型的效果图尚未生成。详见 [云端验证状态](docs/cloud-validation.md)。
- 云端固定版本安装使用 `bash scripts/cloud-install.sh`，启动使用 `source scripts/cloud-start.sh`；复现说明见 [云端启动](docs/cloud-start.md)，资料库验证入口为 `.venv/bin/python scripts/verify_catalog.py`。
- AutoCAD/SketchUp/Carat 兼容性需回到本地软件核验。
- AI 效果图用于视觉提案，不保证尺寸或几何完全一致。

迁移来源：`interior-design-workspace@6a648090f1796e6270268f54e5dfba92dbcacb33`。原配置说明保存在 [迁移来源说明](docs/interior-workspace-source.md)。

## DRAENERT 官网资料库

资料核实日期：2026-10-05。已收录 78 个产品、135 种石材、7 种木材、72 个皮革条目、108 个面料条目，共 400 条；来源存档 464 页。63 个产品有已解析的官方模型下载入口，共 81 个产品与下载入口的关联（75 个 DWG、6 个 3DS），对应 74 个去重下载 URL。数量不代表已检查的模型文件数。

以后在这个项目中可以直接说：

- “给我 Adler 1224 的产品资料和 CAD 模型。”
- “找适合户外使用的蓝色石材。”
- “给我 Atlas Outdoor 的 3DS 下载链接。”
- “比较 Tadao III 和 Tadao V 的尺寸、材料和底座。”

助手会区分完整型号及版本；库存与下载状态在需要时重新核实。

| 资料 | 内容 |
| --- | --- |
| [产品与材料索引](knowledge/catalog-index.md) | 覆盖数量和完整产品清单 |
| [蓝色石材](knowledge/blue-stones.md) | 官方颜色分类、视觉色调、来源和板号实例 |
| [模型下载与尺寸依据](knowledge/model-downloads.md) | 官网下载项、尺寸轴顺序和版本差异 |
| [MOVE 1372](knowledge/move-1372.md) | 茶几图片、Bianco Lila 石材与两档尺寸的来源 |
| [Nobile Bar 2078](knowledge/nobile-bar-2078.md) | V／VI 的尺寸区别及 CAD 包名核验 |

`data/catalog.json` 保存结构化条目；`data/source-pages.json`、`data/raw/` 保存来源正文与采集证据。原始网页读取结果属于资料来源记录，用于重建索引；不包含客户输入、下载的模型二进制或工具运行缓存。

### 本地查询与维护

只需 Python 3 标准库，不需要运行室内设计安装脚本：

```bash
python3 tools/query.py "Adler" --kind product --brief --json
python3 tools/query.py --kind stone --color 蓝色 --limit 20 --brief --json
python3 tools/query.py --kind product --format 3ds --brief --json
python3 tools/source.py "https://draenert.de/de/material/stein/bianco-lila.html"
python3 tools/build_catalog.py
python3 -m unittest discover -s tests -v
```

使用 `--id` 精确读一个完整条目。`build_catalog.py` 只处理已保存的来源，不会抓取新网页；新增或更新来源快照后再重建。资料库测试不验证官网实时库存、ZIP 内部或桌面软件兼容性。

### 来源与能力边界

这是项目内可检索的资料库与助手规则，没有修改其他平台助手的训练参数，也没有安排自动后台更新。来源以 DRAENERT 官网为主；MOVE 的具体尺寸本次由销售商公开规格核对，专项记录明确标注此区别。

模型 ZIP 保存的是官网链接，尚未解压检查；DWG 的二维／三维属性不能只按下载项名称确定。文件名为 `2078_VI_NOBILE_BAR.zip` 的现有包不能直接当作 2078-V 专用模型。PDF 有超时、体积或文字乱码时，应使用清晰来源核实尺寸。完整图库、石材贴图、新闻、历史版本与定制配置未全部归档。

Git 同步只更新仓库内容，不会安装或发布 Codex 云端环境，也不会启用图像生成服务。`inputs/`、`work/`、`outputs/`、虚拟环境、密钥和下载缓存均保持不入库。

## 远程调用本机 AutoCAD 2027

新增 Windows 本机桥接初版：GitHub 手动任务 → 自托管 Runner → AutoCAD COM → 独立 DWG 与执行记录。支持画线、画圆和按句柄移动；输入原件保留。需要本机安装、注册 Runner 和实机验证，当前不代表已经接通。详见 [本机安装与任务示例](docs/local-autocad.md)。

## nobilia 德国柏丽橱柜 · 2026 技术资料库

已归档用户手册8份、730页，保留PDF原件、逐页文本、SHA-256校验、中文关键词与型号查询。06高柜和08 LINE N因上传传输工具32 MiB上限尚待补录。第10章已确认包含在09文件中，并提取成61页独立PDF。

以后在此项目直接说“查柏丽 Easytouch 945 门板”“查转角地柜”“查台面悬挑要求，并给出处”。助手会检索原文，核对图表，并给出文件及页码。使用方法和范围见 [nobilia资料入口](knowledge/nobilia-2026.md)。

```bash
python3 tools/nobilia.py search 'worktop overhangs' --chapter 10
python3 tools/nobilia.py page 09 243
python3 tools/nobilia.py verify
```

新云端实例拉取包含资料库的Git提交即可查询，无需新建API连接。此配置仅作用于能访问本仓库的项目；不等于模型永久记忆，也未配置自动更新。
