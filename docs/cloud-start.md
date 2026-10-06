# 云端启动与复现

使用现有 `/workspace/design-assistant` 检出。每个云端任务已隔离，除非用户明确要求，不创建 Git worktree。先阅读 `AGENTS.md` 并检查 `git status --short`，保留未提交工作；不自动重置或推送。

安装／刷新已验证的 Python 版本：

```bash
cd /workspace/design-assistant
bash scripts/cloud-install.sh
source scripts/cloud-start.sh
```

后续使用 `.venv/bin/python`。安装脚本从 `requirements-cloud.lock` 安装全部 20 项固定版本；不覆盖输入、交付文件和旧 DXF。启动脚本设置仓库 `work/` 下可写缓存，核验依赖导入、`pip check`、中文 Noto 字体、LibreOffice 与 Poppler。这是文件处理工作流，不需要常驻服务。

当前受管镜像提供 Python 3.12.14、LibreOfficeDev 26.8.0.0.alpha0、Poppler 26.05.0 和 Noto CJK 字体。脚本检查这些系统能力，不把它们描述为已固定的跨镜像安装包。其他镜像缺少这些工具时应先通过支持的系统安装方式补齐；保持 TLS、包签名和校验验证。

资料库就绪验证：

```bash
.venv/bin/python scripts/verify_catalog.py
```

仅在新实例、设计依赖或运行时改变时重跑完整设计检查：

```bash
.venv/bin/python scripts/validate_design_environment.py
```

该脚本在 `work/environment-check-*` 唯一新目录生成合成 DXF、中文 Word／Excel／PPT／PDF 和 PNG，以及模型图准备包；不会覆盖客户输入或旧验证结果。完成后逐页查看 PNG，检查中文、分页及溢出。脚本只验证准备流程，不生成效果图。

实际模型图任务读取 `docs/model-to-render.md`，先查看原图，再使用 `scripts/prepare_render.py`；每个会话检查图像编辑工具是否可用。准备包状态 `prepared_not_rendered` 不能作为已出图证明。保留原件和目录私有权限，`inputs/`、`work/`、`outputs/`、虚拟环境、缓存和密钥不提交 Git。

验证记录见 [云端验证状态](cloud-validation.md)。配置保存、Git 推送、环境发布和新任务恢复是不同步骤；发布由产品界面执行，新任务恢复须单独核验。
