# 合规访问期刊与获取科研素材规范

## 1. 目标与边界

本规范解决“怎样稳定、可审计地找到论文、全文和原始图件”，而不是规避期刊的付费墙、反爬、验证码、机器人策略、访问频率限制或版权条款。

> 正常访问 = DOI或出版社正式页面 + 合法开放获取、个人/机构订阅、图书馆代理、作者许可或出版社许可。

禁止：

- 绕过登录、付费墙、验证码或访问控制；
- 使用泄露账号、共享订阅、盗版全文站或不明镜像；
- 保存、提交或公开浏览器Cookie、会话令牌、校园网认证信息、API密钥；
- 把“能打开网页”误记为“允许再分发图片”；
- 因出现403、429、验证码而改用搜索引擎缩略图或二次转载图。

没有合法访问权时，允许记录元数据和失败过程；不允许伪造下载成功或以不可靠图替代。

## 2. 访问前的证据链

每篇论文先建立以下记录，再下载任何文件：

1. 规范化DOI；
2. 出版社落地页；
3. 文章正式题名、作者、年份、期刊、卷期页或文章号；
4. 版本：Version of Record、Accepted Manuscript、预印本或补充材料；
5. 开放状态、许可证或本机构访问依据；
6. 计划使用的图号、图题与PPT页；
7. 适用的引用与使用说明。

优先入口：`https://doi.org/<DOI>`。DOI会把访问者带到当前正式出版商页面，避免依赖过时的搜索结果或转载链接。

## 3. 合法访问路由

按下列顺序选择第一个可行、可核验的路由：

```text
DOI → 出版商HTML与单图下载
    → 出版商PDF/补充材料（具有合法访问权时）
    → 合法开放版本（Unpaywall / OpenAlex / PMC / Europe PMC / arXiv / Zenodo / HAL / 机构知识库）
    → 机构图书馆代理或单点登录
    → 作者或出版商许可
    → 只保留元数据、登记未公开
```

### 3.1 开放获取

- 先查看文章页的开放标记和许可证，优先CC BY等明确许可；
- 使用OA PDF、出版社HTML和官方“download figure”链接时，仍需核对图号和图题；
- OpenAlex、Unpaywall、Crossref仅帮助发现元数据和合法开放位置，不能替代出版社归属核验；
- 仓储版本可用于理解方法和寻图，但若出版社提供完整原始单图，应优先使用出版商单图。

### 3.2 机构订阅与图书馆代理

- 用学校/研究所图书馆入口、VPN或EZproxy访问文章；
- 在正常浏览器中完成单点登录，再从文章页点击“PDF”“Supplementary material”或“Download figure”；
- 下载后的文件只在订阅条款、合理使用和教学/研究用途允许的范围内使用；
- 订阅访问不等于有权把PDF、原图或模板上传到公开GitHub；公开仓库只保留元数据、图题、DOI和获取说明。

### 3.3 出版商或TDM API

只有在个人或机构已取得API密钥、订阅授权和相应条款许可时使用出版社API。API密钥只存于本机安全凭据或CI Secret，绝不进入PPT、CSV、Git仓库、命令历史或问题单。

API返回的全文、图片或元数据仍受授权范围约束；必须记录产品、端点类别、授权依据和获取日期，但不得记录密钥或会话参数。

## 4. 主要出版社与平台的正常路径

| 平台 | 首选入口 | 正常获取方式 | 特别注意 |
|---|---|---|---|
| Elsevier / ScienceDirect | DOI → ScienceDirect文章页 | OA文章直接下载；订阅用户经图书馆/SSO访问HTML、PDF、补充材料或页面提供的图件下载 | Elsevier API与Text and Data Mining服务需独立API密钥及授权；不要假定Scopus或API自动含全文/图件权限 |
| Springer Nature / Nature Portfolio | DOI → SpringerLink或nature.com | 使用文章页的OA PDF、HTML图件、补充材料；非OA经机构订阅访问 | Springer's API/内容服务的权限与普通网页阅读权限不同，按当前条款和机构许可执行 |
| Wiley / AGU期刊 | DOI → Wiley Online Library | OA直接下载；订阅用户通过图书馆入口下载PDF、补充材料或文章页提供的图件 | 文章可读不自动允许公开再分发；AGU论文常以Wiley页面为正式入口 |
| Taylor & Francis | DOI → Taylor & Francis Online | OA或机构访问后使用文章页、PDF和补充材料 | 保留最终文章页与实际版本信息，避免混用早期在线版与最终版 |
| SAGE | DOI → SAGE Journals | OA、机构订阅或作者许可后获取 | 对于无法下载单图的文章，不得把浏览器缩略图当原图 |
| IEEE Xplore / ACM DL | DOI → 平台文章页 | 机构订阅、OA或作者开放版本 | 重点核对会议版本、期刊扩展版与图号是否一致 |
| MDPI / PLOS / Copernicus | DOI → 文章HTML | 优先使用出版商提供的原始PNG/SVG/TIFF或补充文件 | 即使可公开访问，也必须保留图号、图题、许可证和版本 |
| PubMed Central / Europe PMC | DOI或PMCID/PMID | 取得合法开放全文、附图和补充材料 | 核对是否为最终正式版本；图像使用仍受文章许可约束 |

平台页面、URL结构和许可会变化。工作流不硬编码某个出版社的图片路径，也不根据URL外观推断图号。

## 5. 出版商HTML与原始图的具体操作

1. 在正常浏览器打开DOI所指向的文章落地页；
2. 确认题名、作者、年份和图号与证据映射一致；
3. 优先点击页面提供的“Download figure / Original image / Supplementary material”；
4. 对每个下载文件打开检查：面板、坐标轴、图例、单位、比例尺、图号和完整图题对应关系；
5. 记录文章页URL、直接文件URL、访问路由、访问依据、许可证/条款、检索日期和文件SHA-256；
6. 若只有PDF可合法取得，提取完整图区域；不得截入正文、页眉、相邻图或残缺图注；
7. 若图件不能公开再分发，则只在项目私有素材目录保存，并在公开仓库保留元数据而非二进制文件。

## 6. DOI开放位置解析工具

工具包提供只读解析器：

```bash
efppt-resolve-paper "10.1016/j.rse.2024.114000" \
  --email "your-research-email@example.edu" \
  --output 04_real_assets/paper_resolution.json
```

它查询Crossref、OpenAlex和（提供邮箱时）Unpaywall，输出：出版商落地页、元数据、OA状态、候选PDF/仓储地址和查询错误。它**不下载论文、不登录出版社、不处理验证码、不绕过订阅限制**。

解析器输出的候选地址必须在浏览器中再次核验：题名、版本、图号、许可、变量和页面对应关系均不能由聚合API替代。

## 7. 访问日志与来源元数据

每个项目必须维护：

- `04_real_assets/access_log.csv`：每篇论文/平台的访问路由与授权依据；
- `04_real_assets/source_metadata.csv`：每幅实际进入PPT的素材及其文件SHA-256；
- `04_real_assets/retrieval_report.md`：失败、限制和替代方案。

`access_basis`建议使用以下受控值：

```text
open_access_license
institutional_subscription
library_interlibrary_loan
author_repository
author_or_publisher_permission
official_public_document
metadata_only
not_available
```

`rights_status`至少区分：`internal_use_only`、`allowed_with_attribution`、`permission_required`、`not_for_redistribution`、`unknown`。

## 8. 访问失败与反爬处置

| 现象 | 合规处理 |
|---|---|
| HTTP 401/403 | 检查是否需图书馆登录或订阅；记录状态，不反复伪装请求 |
| HTTP 429 | 停止自动请求，遵守网站频率限制；改为手动浏览或稍后重试 |
| CAPTCHA/机器人校验 | 在正常浏览器由授权用户完成；自动化程序不得尝试绕过 |
| 付费墙 | 使用机构订阅、OA版本、作者仓储、馆际互借或请求许可 |
| 只有低清缩略图 | 不使用；查单图、补充材料、作者原图或换用可核验图 |
| 无公开图件 | 写入失败报告，保留文字/公式/表格，不伪造科研图 |

失败记录最少包括检索时间、DOI、平台、实际URL、HTTP/页面提示、已尝试的合法路由、未获取原因、可接受替代方案和下一步所需授权。

## 9. 交付前门禁

对每幅期刊图确认：

- 访问路由与授权依据已记录；
- 文章及图件归属、图号、变量、时间、区域、单位和版本已核验；
- PPT中为等比完整显示，裁剪值为0；
- 页内图源与正式DOI/文章页一致；
- 公开仓库没有上传受订阅、受版权限制或仅限内部使用的二进制文件；
- 找不到合法高质量原图时，已登记为“不可用”，而不是用低清截图替代。
