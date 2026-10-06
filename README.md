# design-assistant · 室内设计与效果图助手

从 [interior-design-workspace](https://github.com/XieGuoning/interior-design-workspace) 迁移室内设计配置，并增加模型图转效果图工作流程。

## 能做什么
| 工作 | 配置与入口 |
| --- | --- |
| CAD 图纸交换 | ezdxf，默认 R2007 DXF（AC1021），核对图层、单位与闭合边界 |
| 材料与预算 | openpyxl，Excel 清单、公式、损耗与税费 |
| 客户方案 | python-docx、python-pptx、pypdf，Word、PPT、PDF |
| 图片与统计图 | Pillow、Matplotlib |
| 模型图转效果图 | 模型截图/白模/线稿 + 风格要求 → 会话图像编辑工具 → 写实效果图与结构复核 |

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
- 实际云端安装、中文预览、图像工具可用性及用户模型的效果图生成，需要在目标环境验证。
- AutoCAD/SketchUp/Carat 兼容性需回到本地软件核验。
- AI 效果图用于视觉提案，不保证尺寸或几何完全一致。

迁移来源：`interior-design-workspace@6a648090f1796e6270268f54e5dfba92dbcacb33`。原配置说明保存在 [迁移来源说明](docs/interior-workspace-source.md)。
