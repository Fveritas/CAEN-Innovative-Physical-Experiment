import uproot
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.optimize import curve_fit

# ================== 解决中文与负号显示问题 ==================
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'SimSun', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

# ================== 路径与参数定义 ==================
DATA_DIR = "d:/前沿/近代物理实验/root数据"
PLOT_DIR = "d:/前沿/近代物理实验/原始代码分析/plots/plots/rossi"

# 确保图片输出目录存在
os.makedirs(PLOT_DIR, exist_ok=True)

# 文件列表
files_week1 = {
    0: "5181.root",
    10: "5182.root",
    20: "5183.root",
    30: "5184.root"
}

files_week2 = {
    40: "5185.root",
    50: "5186.root",
    60: "5187.root"
}

file_calib = "51811.root"  # 第二周的0片铅板基准

# 归一化参考基准：第一周0片（5181）的上探测器计数 N_REF
N_REF = 7064.0

# ================== 数据提取与计算函数 ==================
def process_file(filepath):
    """读取ROOT文件并计算Up数、符合数、归一化符合计数率（个/小时）及其误差"""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"未找到文件: {filepath}")
    
    with uproot.open(filepath) as f:
        tree = f["t1;1"]
        area = tree["area"].array(library="np")
        area2 = tree["area2"].array(library="np")
        
        # 阈值条件：area > 30 且 area2 > 30
        up_mask = area > 30
        down_mask = area2 > 30
        coin_mask = up_mask & down_mask
        
        n_total = len(area)
        n_up = np.sum(up_mask)
        n_coin = np.sum(coin_mask)
        
        # 符合率 p = N_coin / N_up
        p = n_coin / n_up if n_up > 0 else 0.0
        err_p = np.sqrt(p * (1 - p) / n_up) if n_up > 0 else 0.0
        
        # 归一化符合计数率 R = p * N_REF
        rate = p * N_REF
        err_rate = err_p * N_REF
        
        return {
            "n_total": n_total,
            "n_up": n_up,
            "n_coin": n_coin,
            "p": p,
            "rate": rate,
            "err_rate": err_rate
        }

# ================== 核心处理逻辑 ==================
print("开始读取并处理 ROOT 文件数据...")
print("=" * 80)

# 1. 处理第一周数据
data_w1 = {}
for plates, filename in files_week1.items():
    filepath = os.path.join(DATA_DIR, filename)
    data_w1[plates] = process_file(filepath)

# 2. 处理第二周数据
data_w2 = {}
for plates, filename in files_week2.items():
    filepath = os.path.join(DATA_DIR, filename)
    data_w2[plates] = process_file(filepath)

# 3. 处理第二周 0片 校准数据
filepath_calib = os.path.join(DATA_DIR, file_calib)
data_calib = process_file(filepath_calib)

# 4. 计算符合计数率校准因子
r1_0 = data_w1[0]["rate"]
err_r1_0 = data_w1[0]["err_rate"]
r2_0 = data_calib["rate"]
err_r2_0 = data_calib["err_rate"]

f_factor = r1_0 / r2_0
err_f = f_factor * np.sqrt((err_r1_0 / r1_0)**2 + (err_r2_0 / r2_0)**2)

# 5. 校准第二周数据并进行误差传播
plates_w1 = sorted(data_w1.keys())
r_w1 = np.array([data_w1[pt]["rate"] for pt in plates_w1])
err_r_w1 = np.array([data_w1[pt]["err_rate"] for pt in plates_w1])

plates_w2 = sorted(data_w2.keys())
r_w2_raw = np.array([data_w2[pt]["rate"] for pt in plates_w2])
err_r_w2_raw = np.array([data_w2[pt]["err_rate"] for pt in plates_w2])

# 校准后的符合计数率
r_w2_cal = r_w2_raw * f_factor
err_r_w2_cal = r_w2_cal * np.sqrt((err_r_w2_raw / r_w2_raw)**2 + (err_f / f_factor)**2)

# ================== 绘图 1: 第一周独立 Rossi 曲线 ==================
fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
color_w1 = "#1A5276"

ax.errorbar(plates_w1, r_w1, yerr=err_r_w1, fmt="o-", color=color_w1, 
            linewidth=2.0, markersize=8, elinewidth=1.5, capsize=4, capthick=1.5,
            label="第一周测量数据 (0-30片)")

# 线性拟合显示趋势
slope, intercept = np.polyfit(plates_w1, r_w1, 1)
fit_x = np.linspace(0, 30, 100)
fit_y = slope * fit_x + intercept
ax.plot(fit_x, fit_y, "--", color="#5DADE2", linewidth=1.5, 
        label=f"线性拟合: y = {slope:.3f}x + {intercept:.1f}")

# 美化
ax.set_title("第一周 Rossi 曲线 (0 - 30 片铅板)", fontsize=14, fontweight="bold", pad=15)
ax.set_xlabel("铅板数量 (片)", fontsize=12)
ax.set_ylabel("归一化符合计数率 Coin Count Rate (counts/h)", fontsize=12)
ax.set_xlim(-5, 35)
ax.set_ylim(2850, 3500)
ax.grid(True, linestyle="--", alpha=0.4)
ax.legend(fontsize=10, loc="upper right", framealpha=0.9, facecolor="#F8F9F9")
fig.tight_layout()

plot1_path = os.path.join(PLOT_DIR, "rossi_curve_week1.png")
plt.savefig(plot1_path, dpi=300, bbox_inches="tight")
plt.close()

# ================== 绘图 2: 两周合并校准 Rossi 曲线 ==================
fig, ax = plt.subplots(figsize=(9, 6.5), dpi=300)

# 配色
color_w1 = "#1F618D"       # 第一周
color_w2_raw = "#CD6155"   # 第二周原始（浅红/虚线）
color_w2_cal = "#C0392B"   # 第二周校准（深红）

# 1. 绘制第一周数据
ax.errorbar(plates_w1, r_w1, yerr=err_r_w1, fmt="o-", color=color_w1, 
            linewidth=2.0, markersize=8, elinewidth=1.5, capsize=4, capthick=1.5,
            label="第一周测量数据 (0-30片)")

# 2. 绘制第二周校准前数据 (对照组)
ax.errorbar(plates_w2, r_w2_raw, yerr=err_r_w2_raw, fmt="s--", color=color_w2_raw, 
            linewidth=1.5, markersize=7, elinewidth=1.2, capsize=3, capthick=1.0, alpha=0.5,
            label="第二周原始数据 (40-60片, 未校准)")

# 3. 绘制第二周校准后数据
ax.errorbar(plates_w2, r_w2_cal, yerr=err_r_w2_cal, fmt="D-", color=color_w2_cal, 
            linewidth=2.2, markersize=8, elinewidth=1.8, capsize=4, capthick=1.5,
            label="第二周校准后数据 (40-60片, 向上校准)")

# 4. 绘制第二周 0片 校准基准点
ax.errorbar([0], [r2_0], yerr=[err_r2_0], fmt="s", color=color_w2_raw, 
            markersize=8, elinewidth=1.2, capsize=3, alpha=0.5, label="第二周0片原始基准")
ax.errorbar([0], [r2_0 * f_factor], yerr=[err_r2_0 * f_factor], fmt="D", color=color_w2_cal, 
            markersize=8, elinewidth=1.8, capsize=4, label="第二周0片校准后基准")

# 5. 添加校准动画箭头指示
ax.annotate("", xy=(0, r1_0 - 20), xytext=(0, r2_0 + 20),
            arrowprops=dict(arrowstyle="->", color="black", lw=1.5, ls=":", connectionstyle="arc3,rad=0.1"))
ax.text(1, (r1_0 + r2_0)/2, f"校准乘积因子: {f_factor:.4f}x\n(消除下探测器效率下降)", 
        fontsize=9, color="black", ha="left", va="center", bbox=dict(boxstyle="round,pad=0.3", fc="#FCF3CF", ec="gray", alpha=0.8))

# 6. 进行合并后的全局趋势拟合 (使用第一周数据 + 第二周校准后数据)
combined_x = np.concatenate([plates_w1, plates_w2])
combined_y = np.concatenate([r_w1, r_w2_cal])

# 二次多项式拟合
poly_coefs = np.polyfit(combined_x, combined_y, 2)
poly_fit = np.poly1d(poly_coefs)
fit_comb_x = np.linspace(0, 60, 200)
fit_comb_y = poly_fit(fit_comb_x)

ax.plot(fit_comb_x, fit_comb_y, "-", color="#E67E22", linewidth=2.0, 
        label="全局趋势拟合 (二次多项式)")

# 指数衰减拟合: y = A * exp(-mu * x) + B
try:
    f_exp = lambda x, A, mu, B: A * np.exp(-mu * x) + B
    popt, pcov = curve_fit(f_exp, combined_x, combined_y, p0=[500, 0.05, 2900])
    fit_exp_y = f_exp(fit_comb_x, *popt)
    ax.plot(fit_comb_x, fit_exp_y, "--", color="#27AE60", linewidth=2.0,
            label=f"指数衰减拟合: A*e^(-μx) + B\n(A={popt[0]:.1f}, μ={popt[1]:.4f}, B={popt[2]:.1f})")
except Exception as e:
    print(f"指数衰减拟合失败: {e}")

# 美化
ax.set_title("宇宙射线符合计数率随铅板厚度的变化 (Rossi 曲线校准合并)", fontsize=14, fontweight="bold", pad=15)
ax.set_xlabel("铅板数量 (片)", fontsize=12)
ax.set_ylabel("归一化符合计数率 Coin Count Rate (counts/h)", fontsize=12)
ax.set_xlim(-5, 65)
ax.set_ylim(1300, 3600)
ax.grid(True, linestyle="--", alpha=0.4)

# ================== 响应用户修改图例要求 ==================
# 将图例设为半透明 (framealpha=0.3) 并且放置于 "lower left"
# 同时通过调整图例的内边距和大小，使其尽可能紧凑
ax.legend(fontsize=9, loc="lower left", frameon=True, framealpha=0.35, facecolor="#F8F9F9", edgecolor="gray")

# 标注物理信息
ax.text(45, 1850, "第二周原始数据因\n探测器效率下降而偏低", fontsize=9, color=color_w2_raw, ha="center")
ax.text(50, 3250, "校准与归一化后，数据在\n全局趋势上展现出连续的单调衰减规律", fontsize=9, color="#D35400", ha="center",
        bbox=dict(boxstyle="round,pad=0.3", fc="#FDEDEC", ec="#FADBD8", alpha=0.8))

fig.tight_layout()
plot2_path = os.path.join(PLOT_DIR, "rossi_curve_combined.png")
plt.savefig(plot2_path, dpi=300, bbox_inches="tight")
plt.close()

print("图例优化及绘图任务已成功完成！")
