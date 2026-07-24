# Evidence-First PPT Workflow

一套面向课程、科研项目汇报、答辩和论文分享的开源演示文稿生产工作流。

它解决的不是“怎样快速生成很多页”，而是怎样持续产出以下类型的可交付文件：

- 内容有明确证据链；
- 科研图片真实、完整、可核验；
- 公式排版正确；
- 页面信息密度足够且可讲解；
- 使用指定机构模板而不破坏母版几何；
- 可编辑、可复现、可自动验收；
- 每次返工都有记录，而不是在最终PPT里反复打补丁。

本项目的核心原则是：

> 先确认事实与证据，再决定页面；先确定页面任务，再选择排版；先通过机器检查，再进行人工放映验收。

## 适用范围

- 高校与科研院所课程PPT；
- 科研项目申报、年度汇报、中期检查和结题答辩；
- 学术会议报告、论文解读和研究生组会；
- 需要真实论文图、官方产品图、公式和学术表格的演示文稿；
- 基于现有机构模板或用户已修改PPT继续迭代的任务。

不适合直接用于纯营销海报、娱乐演示或无需证据链的社交媒体图文。

## 为什么需要这套工作流

科研PPT中最常见、也最难在最后一轮补救的问题包括：

1. 图片来自搜索引擎缩略图，来源与图中变量无法核验；
2. 从PDF随手截图，坐标轴、图例、面板或正文被截断；
3. 为了排版把图压扁、拉伸或裁剪；
4. 使用形状堆叠伪装成科研图，或反复使用同一幅图；
5. 公式用普通文本模拟，分式、上下标和求和范围错误；
6. 页面只有三行空泛文字和大量空白，无法支撑讲解；
7. 每页套同一版式，虽然统一但高度同质化；
8. 标题、页码、页脚和母版元素互相重叠；
9. 只检查PPTX结构，不做PowerPoint实际渲染；
10. 修改了错误文件，或正式文件与交付副本不是同一版本。

本工作流把这些问题转化为阶段门禁、机器可读元数据和可量化验收指标。

## 快速开始

### 1. 安装

```bash
git clone https://github.com/zcqsaz/evidence-first-ppt-workflow.git
cd Evidence-First-PPT-Workflow
python -m pip install -e .
```

### 2. 创建项目

```bash
efppt-init projects/2026-001-example
cd projects/2026-001-example
```

### 3. 填写范围和输入登记

至少完成：

- `PROJECT.md`：目标、受众、时长、允许修改的文件、禁止事项；
- `project_config.json`：字体、页面比例、禁用措辞和QA阈值；
- `00_input/source_manifest.md`：原始文档、模板和补充资料；
- `01_extract/evidence_map.csv`：关键论断与来源映射。

### 4. 按阶段执行

完整流程见 [docs/WORKFLOW.md](docs/WORKFLOW.md)。科研素材规则见 [docs/standards/REAL_ASSETS.md](docs/standards/REAL_ASSETS.md)，期刊、Elsevier等大型出版商的合规访问与全文/原图获取路径见 [docs/standards/PUBLISHER_ACCESS.md](docs/standards/PUBLISHER_ACCESS.md)。

### 4.1 解析DOI与合法开放版本

```bash
efppt-resolve-paper "10.1016/j.rse.2024.114000" \
  --email "your-research-email@example.edu" \
  --output 04_real_assets/paper_resolution.json
```

该命令只查询Crossref、OpenAlex与Unpaywall，提供出版社落地页和合法开放版本候选；它不会下载付费论文、绕过登录、处理验证码或规避访问控制。

### 5. 验收PPTX

```bash
efppt-validate-pptx final.pptx \
  --config project_config.json \
  --asset-root 04_real_assets \
  --report 07_qa/pptx_validation.json
```

### 6. 验收素材证据链

```bash
efppt-validate-sources \
  04_real_assets/source_metadata.csv \
  --asset-root 04_real_assets \
  --check-urls \
  --report 07_qa/source_validation.json
```

### 7. 实际渲染与缩略图总览

Windows + Microsoft PowerPoint：

```powershell
powershell -ExecutionPolicy Bypass -File ../../scripts/render_with_powerpoint.ps1 `
  -InputPptx final.pptx `
  -OutputDir 07_qa/renders_final
```

```bash
efppt-contact-sheet \
  07_qa/renders_final \
  07_qa/contact_sheet.jpg
```

自动化工具的检查项、退出码和能力边界见 [docs/TOOLING.md](docs/TOOLING.md)。特别注意：`crop=0`只能证明PowerPoint没有再次裁剪，不能代替对原始图片全部面板、坐标轴、图例和正文碎片的人工检查。

v1.0.1的自动测试、隔离安装、61页真实课程PPT集成测试及DOI解析器测试结果见 [docs/VALIDATION.md](docs/VALIDATION.md)。验证记录只公开指标，不再分发用户PPT、模板或第三方论文图。

### 7. 查看可公开复用的五页示例

仓库包含一个从空白16:9画布构建的可编辑示例：[examples/five_slide_academic_demo](examples/five_slide_academic_demo)。它通过五页展示封面、目录高亮、页面规格、素材审计和交付QA；只使用本仓库原创文字及原生PowerPoint对象，不含机构模板、Logo、个人信息、真实项目材料或第三方科研图片。

```bash
python examples/five_slide_academic_demo/build_demo.py

efppt-validate-pptx \
  examples/five_slide_academic_demo/five_slide_academic_demo.pptx \
  --config examples/five_slide_academic_demo/demo_config.json
```

该示例的本地渲染图和检查报告默认被Git忽略，避免把本机绝对路径或临时审阅产物带入公开仓库。

## 阶段概览

| 阶段 | 核心问题 | 强制产物 | 通过条件 |
|---|---|---|---|
| 0. 范围冻结 | 允许改什么，不能改什么？ | `PROJECT.md`、配置文件 | 修改范围明确 |
| 1. 输入与证据 | 事实从哪里来？ | 来源清单、证据映射 | 关键论断可追溯 |
| 2. 叙事 | 观众如何建立理解？ | 批准的叙事主线 | 结构被确认 |
| 3. 页面规格 | 每页完成什么推理任务？ | 逐页规格 | 结论与证据匹配 |
| 4. 真实素材 | 图到底是什么？ | 素材包、元数据 | 图件已核验 |
| 5. 视觉与模板 | 怎样读，而不是怎样装饰？ | 构图语法、代表页 | 模板几何通过 |
| 6. 构建 | 怎样稳定生成可编辑PPTX？ | 构建脚本、PPTX | 可重复生成 |
| 7. QA | 图片、文字、公式是否真的正确？ | 结构报告、渲染图 | 硬性指标全部通过 |
| 8. 交付 | 交付的是不是最终版本？ | PPTX、说明、哈希 | 版本一致 |

## 三项否决规则

以下任一项不合格，PPT不得交付：

1. **图片完整性否决**：科研图被裁断、混入论文正文、缺图例/坐标轴/面板，或被非等比拉伸；
2. **数学排版否决**：复杂公式由普通文本、空格或Unicode拼接模拟；
3. **信息密度否决**：除封面、目录和过渡页外，没有形成“明确结论 + 至少4条实质知识点/证据 + 来源”的授课或论证单元。

## 仓库结构

```text
Evidence-First-PPT-Workflow/
├── README.md
├── LICENSE
├── NOTICE.md
├── CONTRIBUTING.md
├── requirements.txt
├── pyproject.toml
├── docs/
│   ├── WORKFLOW.md
│   ├── GOVERNANCE.md
│   └── standards/
├── templates/
│   └── project/
├── schemas/
├── scripts/
├── tests/
└── examples/
```

## 工具中立

工作流不要求使用特定AI或PPT生成器。任何实现只要能够产生规定的阶段产物、保留证据链并通过验收即可。AI可以帮助检索、编排和编码，但不得替代事实核验、版权判断与最终人工放映检查。

## 开发与发布

```bash
python -m pip install -e ".[dev]"
pytest -q
```

公开发布前执行 [docs/OPEN_SOURCE_RELEASE.md](docs/OPEN_SOURCE_RELEASE.md) 中的隐私、版权、安装和回归测试清单。真实项目PPT、机构模板、论文PDF和第三方科研图片默认不进入公开仓库。

## 开源许可

工作流文档、模板和本仓库原创代码采用 [MIT License](LICENSE)。

论文图、官方图片、机构模板、字体、商标、输入文档和用户项目成果不因本仓库采用MIT而获得再分发许可。详见 [NOTICE.md](NOTICE.md)。

## English summary

Evidence-First PPT Workflow is an open, tool-agnostic production and QA system for academic presentations. It prioritizes traceable evidence, complete publisher-original figures, correctly rendered mathematics, content density, template-safe layout, reproducible builds, and measurable acceptance gates.
