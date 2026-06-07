# GitHub 未包含文件清单

生成时间：2026-06-07

本项目已将 `/home/guiyu/workspace/CAEN/New_Analysis` 目录内所有未被 `.gitignore` 排除的文件加入 Git 提交。以下文件不会进入 GitHub，原因是仓库根目录 `/home/guiyu/workspace/CAEN/.gitignore` 排除了 `*.root` 和 Python 缓存目录。

## 被排除的原始 ROOT 数据

这些文件体积较大，属于原始实验数据，当前按 `.gitignore` 规则不提交：

```text
Raw_data/5181.root
Raw_data/51811.root
Raw_data/5182.root
Raw_data/5183.root
Raw_data/5184.root
Raw_data/5185.root
Raw_data/5186.root
Raw_data/5187.root
Raw_data/add_time_5181b/5181b.root
```

## 被排除的 Python 缓存

这些是运行 Python 脚本自动生成的缓存文件，不应提交：

```text
data_analysis/combined_analysis/__pycache__/combined_week_analysis.cpython-310.pyc
data_analysis/week_1/__pycache__/week1_fit_spectrum_analysis.cpython-310.pyc
data_analysis/week_1/__pycache__/week1_pre_fit_analysis.cpython-310.pyc
data_analysis/week_2/__pycache__/week2_fit_spectrum_analysis.cpython-310.pyc
data_analysis/week_2/__pycache__/week2_pre_fit_analysis.cpython-310.pyc
data_processing/__pycache__/preprocess_root_data.cpython-310.pyc
```

## Markdown 文档状态

截至本次提交，`New_Analysis` 目录内未发现被 `.gitignore` 排除的 Markdown 文档。也就是说，目录内的 `.md` 文档都会进入 GitHub。
