# 开源发布清单

## 发布前必须通过

- [ ] `README.md`能够让新用户在15分钟内初始化项目并运行一次检查；
- [ ] `LICENSE`、`NOTICE.md`、`CONTRIBUTING.md`、`SECURITY.md`和`CODE_OF_CONDUCT.md`存在；
- [ ] `CITATION.cff`没有虚假仓库地址、个人隐私或未确认作者信息；
- [ ] 仓库中没有用户原始Word、机构模板、课程成品PPT、论文PDF或受限字体；
- [ ] 仓库中没有绝对路径、微信标识、用户名、访问令牌、Cookie或内部URL；
- [ ] 示例图全部为项目自行生成并明确许可，或示例只提供元数据不再分发第三方图；
- [ ] `python -m pip install -e ".[dev]"`成功；
- [ ] `pytest -q`全部通过；
- [ ] 初始化器不会覆盖已有目录；
- [ ] 合格测试PPT通过，故意损坏的PPT被正确拦截；
- [ ] JSON Schema可解析；
- [ ] 文档中的命令、目录和文件名与实际仓库一致；
- [ ] 版本号在`pyproject.toml`、`CITATION.cff`、`CHANGELOG.md`和脚本中一致；
- [ ] 发布标签遵循语义化版本，例如`v1.0.0`；
- [ ] 已生成源代码归档，并在干净环境中复测安装。

## 禁止进入公开仓库的内容

- 用户输入材料和用户修改后的PPT；
- 机构母版、Logo和未获再分发许可的模板底图；
- 从论文PDF或出版商网页取得的第三方原图；
- 真实项目的素材包和网络下载缓存；
- PowerPoint渲染结果中的保密数据；
- 访问受限网站所用的认证信息；
- 本机临时目录和QA缓存。

第三方科研图片可以在公开示例中记录来源、DOI、图号和获取步骤，但除非许可明确允许，不应随仓库重新分发。

## 推荐发布流程

```bash
python -m pip install -e ".[dev]"
pytest -q
python -m compileall scripts
git status --short
git tag -s v1.0.0 -m "Evidence-First PPT Workflow v1.0.0"
```

发布后记录仓库正式URL，再将它加入`CITATION.cff`的`repository-code`字段；在URL尚未确定前，不使用`example.org`之类的伪地址。
