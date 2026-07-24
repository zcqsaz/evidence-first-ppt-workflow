# 自动化工具与边界

本目录中的脚本把工作流中的部分门禁转化为可重复执行的检查。它们是质量护栏，不是事实核验、版权判断或人工放映审查的替代品。

## 1. 安装与调用

使用常规 Python：

```bash
python -m pip install -e .
efppt-init projects/2026-001-example
```

也可直接调用脚本：

```bash
python scripts/validate_pptx.py --help
```

开发者可使用：

```bash
python -m pip install -e ".[dev]"
pytest -q
```

## 2. PPTX结构检查

```bash
efppt-validate-pptx final.pptx \
  --config project_config.json \
  --asset-root 04_real_assets \
  --report 07_qa/pptx_validation.json
```

检查内容：

- 文件是否可打开、页数和宽高比；
- 顶层对象是否越界；
- 文本框几何是否大面积重叠；
- 图片是否存在PowerPoint裁剪值；
- 非母版图片是否重复使用；
- 显式字体是否在允许列表中；
- 是否含禁用的制作语言；
- 页码是否存在并位于页面宽度几何中心；
- 正文字符数、实质单元和视觉对象的启发式密度；
- PPTX内嵌图片与素材根目录文件的SHA-256映射。

退出码：无错误为`0`，存在错误为`1`。警告不会单独造成失败，除非在配置中把相应规则设为失败项。

### 已知边界

- `crop=0`只能证明PowerPoint没有再次裁剪，不能证明原始PNG/JPEG没有在下载或导出前截断；
- 几何重叠不等于实际字形重叠，人工仍需检查换行、行距和溢出；
- 字体检查针对显式字体，主题继承和目标电脑缺字体必须通过实际渲染发现；
- 信息密度是启发式指标，不能判断四条文字是否真的有知识含量；
- 素材哈希匹配证明文件一致，不证明图题、变量、单位和项目归属正确。

因此，机器检查通过后仍必须完成全量渲染、缩略图总览和重点页原尺寸检查。

## 3. 来源与素材检查

```bash
efppt-validate-sources 04_real_assets/source_metadata.csv \
  --asset-root 04_real_assets \
  --check-urls \
  --report 07_qa/source_validation.json
```

检查内容：

- CSV字段和Schema；
- 文件是否存在且路径没有逃逸素材根目录；
- 声明哈希与实际SHA-256；
- 文件名、`asset_id`和文件内容是否重复；
- DOI和HTTP(S) URL格式；
- 图片是否可解码及长边像素；
- 核验状态是否允许正式使用；
- 可选的URL状态与下载MIME检查。

出版社反爬、机构网络限制或临时故障会产生`URL_UNREACHABLE`。默认记为警告并在报告中保留状态、错误和涉及行；使用`--strict-network`可将其升级为错误。不得把“网页当前能访问”解释为“图片事实已核验”。

## 4. PowerPoint真实渲染

Windows且安装Microsoft PowerPoint时：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/render_with_powerpoint.ps1 `
  -InputPptx final.pptx `
  -OutputDir 07_qa/renders_final `
  -Width 1600 `
  -Height 900
```

脚本使用独立PowerPoint COM实例逐页导出，不结束用户已经打开的PowerPoint进程。

随后生成总览：

```bash
efppt-contact-sheet 07_qa/renders_final 07_qa/contact_sheet.jpg
```

## 5. 公式渲染

```bash
efppt-render-formula \
  --latex "\\frac{\\sum_{i=1}^{n}x_i}{n}" \
  --output 04_real_assets/formulas/mean.png \
  --dpi 300 \
  --font-size 32
```

该脚本使用Matplotlib mathtext，适合常见分式、上下标、求和和希腊字母。复杂宏包、矩阵环境或必须使用完整TeX排版的公式，应改用受控LaTeX引擎，并保留`.tex`源文件。公式图必须等比显示且不得被PowerPoint裁剪。

## 6. 交付副本一致性

```bash
efppt-compare-files approved/final.pptx delivery/final.pptx \
  --report 07_qa/delivery_hash.json
```

只有`identical: true`才证明批准文件与交付副本逐字节一致。复制之后不得继续编辑交付副本。

## 7. 配置与报告Schema

- `schemas/project_config.schema.json`：项目范围与QA阈值；
- `schemas/source_metadata.schema.json`：每一行素材元数据；
- `schemas/validation_report.schema.json`：JSON检查报告的最小公共结构。

配置中的例外必须精确到页码或SHA-256，并在人工验收报告中解释原因。不得通过扩大容差、批量加入例外或关闭规则来“让报告变绿”。
