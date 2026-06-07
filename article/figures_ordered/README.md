# CAEN New_Analysis 图片整理说明

本目录从 `/home/guiyu/workspace/CAEN/New_Analysis` 中复制全部分析图片，并按论文叙事顺序重新分类编号。图片没有改变内容，只是复制到 `article/figures_ordered/` 便于写作和引用。

## 01_week1_basic

第一周 0、10、20、30 片铅板的基础统计和诊断图。

| 文件 | 内容 |
| --- | --- |
| `01_week1_coin_rate.png` | 第一周原始双探测器符合率随铅厚变化。 |
| `02_week1_transmission_blocking.png` | 第一周相对透过率和有效阻挡率。 |
| `03_week1_normalized_coin_ratios.png` | 第一周 `Coin/Up` 与 `Coin/Down` 条件符合比。 |
| `04_week1_conditional_weighted_coin_rate.png` | 第一周 `coin/hour` 乘条件符合比后的加权符合率。 |
| `05_week1_area_distribution.png` | 第一周上探测器 `area` 分布。 |
| `06_week1_area2_distribution.png` | 第一周下探测器 `area2` 分布。 |
| `07_week1_area_vs_area2_5181.png` | 第一周 0 片 run 5181 的 `area` vs `area2` 二维分布。 |
| `08_week1_area_vs_area2_5182.png` | 第一周 10 片 run 5182 的二维分布。 |
| `09_week1_area_vs_area2_5183.png` | 第一周 20 片 run 5183 的二维分布。 |
| `10_week1_area_vs_area2_5184.png` | 第一周 30 片 run 5184 的二维分布。 |

## 02_week1_fit_spectrum

第一周经验指数拟合和符合事件脉冲积分谱。

| 文件 | 内容 |
| --- | --- |
| `01_week1_attenuation_fit.png` | 第一周透过率模型 `T(x)=exp(-x/lambda)` 拟合及残差。 |
| `02_week1_coin_rate_fit.png` | 第一周绝对符合率模型 `R(x)=R0 exp(-x/lambda)` 拟合及残差。 |
| `03_week1_area_coin_spectrum.png` | 第一周符合事件上探测器 `area` 谱。 |
| `04_week1_area2_coin_spectrum.png` | 第一周符合事件下探测器 `area2` 谱。 |

## 03_week2_basic

第二周 0、40、50、60 片铅板的基础统计和诊断图。

| 文件 | 内容 |
| --- | --- |
| `01_week2_coin_rate.png` | 第二周原始双探测器符合率随铅厚变化。 |
| `02_week2_transmission_blocking.png` | 第二周相对透过率和有效阻挡率。 |
| `03_week2_normalized_coin_ratios.png` | 第二周 `Coin/Up` 与 `Coin/Down` 条件符合比。 |
| `04_week2_conditional_weighted_coin_rate.png` | 第二周 `coin/hour` 乘条件符合比后的加权符合率。 |
| `05_week2_area_distribution.png` | 第二周上探测器 `area` 分布。 |
| `06_week2_area2_distribution.png` | 第二周下探测器 `area2` 分布。 |
| `07_week2_area_vs_area2_51811.png` | 第二周 0 片 run 51811 的二维分布。 |
| `08_week2_area_vs_area2_5185.png` | 第二周 40 片 run 5185 的二维分布。 |
| `09_week2_area_vs_area2_5186.png` | 第二周 50 片 run 5186 的二维分布。 |
| `10_week2_area_vs_area2_5187.png` | 第二周 60 片 run 5187 的二维分布。 |

## 04_week2_fit_spectrum

第二周经验指数拟合和符合事件脉冲积分谱。

| 文件 | 内容 |
| --- | --- |
| `01_week2_attenuation_fit.png` | 第二周透过率模型拟合及残差。 |
| `02_week2_coin_rate_fit.png` | 第二周绝对符合率模型拟合及残差。 |
| `03_week2_area_coin_spectrum.png` | 第二周符合事件上探测器 `area` 谱。 |
| `04_week2_area2_coin_spectrum.png` | 第二周符合事件下探测器 `area2` 谱。 |

## 05_week2_system_checks

第二周 `area2` 左移和阈值扫描的系统误差诊断图。

| 文件 | 内容 |
| --- | --- |
| `01_area2_zero_lead_left_shift.png` | 第一周 0 片和第二周 0 片的 `area2` 分布直接对比。 |
| `02_area2_distribution_week2_vs_week1.png` | 第一周参考与第二周全部 run 的 `area2` 分布对比。 |
| `03_area2_ecdf_week2_vs_week1.png` | `area2` 经验累积分布函数对比。 |
| `04_area2_boxplot_week2_vs_week1.png` | `area2` 箱线图，展示中位数和四分位差异。 |
| `05_area2_pass_fraction_gt30.png` | `area2 > 30` 阈值通过率对比。 |
| `06_week2_coin_counts_area2_threshold_scan.png` | 第二周改变 `area2` 阈值时的符合数变化。 |
| `07_week2_coin_over_up_area2_threshold_scan.png` | 第二周不同 `area2` 阈值下的 `Coin/Up`。 |
| `08_week2_recovered_coin_events.png` | 降低 `area2` 阈值后恢复的符合事件数。 |

## 06_combined_diagnostics

跨周系统差异诊断图。

| 文件 | 内容 |
| --- | --- |
| `01_zero_lead_area_comparison.png` | 两周 0 片上探测器 `area` 分布对比。 |
| `02_zero_lead_area2_comparison.png` | 两周 0 片下探测器 `area2` 分布对比。 |
| `03_zero_lead_area_vs_area2_comparison.png` | 两周 0 片 `area` vs `area2` 二维分布对比。 |
| `04_detector_pass_fraction_comparison.png` | 上下探测器阈值通过率跨周对比。 |
| `05_conditional_coin_ratio_comparison.png` | 跨周 `Coin/Up` 与 `Coin/Down` 条件符合比对比。 |

## 07_combined_normalization

跨周归一化和综合趋势图。

| 文件 | 内容 |
| --- | --- |
| `01_raw_coin_rate_combined.png` | 原始 `coin/hour` 跨周拼接图，仅用于诊断。 |
| `02_week_transmission_comparison.png` | 第一周和第二周分别用本周 0 片归一化的透过率对比。 |
| `03_coin_up_normalized_rate_combined.png` | `Coin/Up * N_up(5181)` 上探测器归一化符合率。 |
| `04_coin_up_normalized_transmission_combined.png` | 上探测器归一化后的相对透过率。 |
| `05_coin_up_normalized_then_scaled_rate_combined.png` | 在 `Coin/Up * N_up(5181)` 后，对第二周再乘旧 0 片缩放因子的综合计数率。 |
| `06_coin_up_normalized_then_scaled_transmission_combined.png` | 上述“归一化后再缩放”结果相对第一周 0 片的透过率。 |

## 08_combined_fits

对“归一化后再缩放”综合曲线的经验模型拟合图。

| 文件 | 内容 |
| --- | --- |
| `01_normalized_scaled_transmission_fit.png` | 单指数透过率模型 `T(x)=exp(-x/lambda)` 拟合及残差。 |
| `02_normalized_scaled_rate_fit.png` | 单指数计数率模型 `R(x)=R0 exp(-x/lambda)` 拟合及残差。 |
| `03_normalized_scaled_transmission_log_fit.png` | 单指数透过率模型的对数化图 `ln T`。 |
| `04_normalized_scaled_rate_log_fit.png` | 单指数计数率模型的对数化图 `ln R`。 |
| `05_normalized_scaled_transmission_offset_exp_fit.png` | 指数加常数平台模型 `T(x)=T_inf + A exp(-x/lambda)` 拟合及残差。 |
| `06_normalized_scaled_rate_offset_exp_fit.png` | 指数加常数平台模型 `R(x)=R_inf + A exp(-x/lambda)` 拟合及残差。 |
| `07_normalized_scaled_transmission_offset_exp_log_fit.png` | 扣除平台后的透过率对数化图 `ln(T-T_inf)`。 |
| `08_normalized_scaled_rate_offset_exp_log_fit.png` | 扣除平台后的计数率对数化图 `ln(R-R_inf)`。 |

## 使用建议

论文正文建议优先使用：

1. 第一周主结果：`01_week1_basic/02_week1_transmission_blocking.png`。
2. 第二周系统诊断：`03_week2_basic/03_week2_normalized_coin_ratios.png`、`05_week2_system_checks/06_week2_coin_counts_area2_threshold_scan.png`。
3. 跨周诊断：`06_combined_diagnostics/05_conditional_coin_ratio_comparison.png`。
4. 综合趋势：`07_combined_normalization/05_coin_up_normalized_then_scaled_rate_combined.png`。
5. 模型比较：`08_combined_fits/02_normalized_scaled_rate_fit.png` 与 `08_combined_fits/06_normalized_scaled_rate_offset_exp_fit.png`。
