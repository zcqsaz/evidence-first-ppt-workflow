# 五页学术PPT制作示例

本示例是一个关于“证据优先PPT工作流”的五页微型课程PPT，用于演示：封面、目录高亮、证据页、素材审计页和交付QA页怎样在同一套视觉系统中保持高信息密度且不机械重复。

## 内容与隐私声明

- 不使用机构母版、Logo、学校名称、个人姓名、邮箱、账号、真实项目资料或用户文件；
- 不含论文PDF、第三方科研图片、网页截图、付费内容或受限素材；
- 全部文字、版式、表格与关系图均为本仓库原创示例；
- 幻灯片中的流程与检查项是工作流教学内容，不是实测科研数据；
- 示例以空白16:9画布构建，便于任何用户理解和复用；它不是某一机构模板的替代品。

## 文件

- `five_slide_academic_demo.pptx`：可直接打开的五页示例；
- `build_demo.py`：确定性生成脚本；
- `demo_config.json`：示例PPTX的检查配置；
- `example_spec.md`：五页的页面任务、主结论和验收条件。

## 重新生成与检查

```bash
python examples/five_slide_academic_demo/build_demo.py

efppt-validate-pptx \
  examples/five_slide_academic_demo/five_slide_academic_demo.pptx \
  --config examples/five_slide_academic_demo/demo_config.json
```

生成脚本只依赖本项目已经声明的 `python-pptx`，不访问网络，不下载或嵌入外部二进制素材。
