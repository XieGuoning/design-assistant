# 云端验证状态

验证日期：2026-10-06。正式检出路径：`/workspace/design-assistant`。

## 本轮资料库同步

已从设计基线 `6c054f4ad6563c77885127424d60aad233d8f16a` 安全快进到资料库基线 `f47a3652041e651cbda234662e723f863e67256c`，保留已有文件和私有权限。

- 现有 `unittest` 套件实际执行 25 项，全部通过，无跳过。
- 400 条记录：产品 78、石材 135、木材 7、皮革 72、面料 108。
- Adler、1224 Outdoor、Tadao III／V、MOVE 1372、2078 家族查询正常；蓝色石材 14 条，具有已观测 3DS 链接的产品 6 条；Bianco Lila 来源正文与行号可读取。
- `2078-V` 精确查询为零条，这是已记录的索引限制。需查询 `2078` 并阅读 `knowledge/nobile-bar-2078.md`；不能将 `2078_VI_NOBILE_BAR.zip` 认定为 V 专用。未修改查询逻辑或证据资料以掩盖这一限制。

## 保留的设计验证

同一实例在设计基线已实际通过依赖导入、`pip check`、R2007 DXF AC1021 写入／读回、显式毫米单位及闭合四边形检查。中文 Word／Excel／PPT 经 LibreOffice 转 PDF、Poppler 转 PNG；各为单页，中文可提取，目视无乱码或溢出。Excel 公式计算为 200，Matplotlib 中文 PDF 预览正常。

`prepare_render` 已验证源图 SHA256、参考图、中文提示词、准备状态和拒绝覆盖。没有生成效果图。本轮设计文件与固定依赖未改变，未重复完整设计验证。原合成证据保留在实例的 `work/onboarding-20261006/`，不上传 Git；可复用验证入口已保存为 `scripts/validate_design_environment.py`。

## 复现与限制

已验证固定版本安装流程、启动检查和资料库验证入口，参见 [云端启动](cloud-start.md)。Python 依赖固定在 `requirements-cloud.lock`；系统字体、LibreOffice 和 Poppler 由当前受管镜像提供。

未验证官网实时库存、下载 ZIP 内部、AutoCAD／SketchUp／Carat 原生兼容性或用户模型的效果图。发布由产品界面处理；此记录不证明环境已发布或新任务恢复已验证。
