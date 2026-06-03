# 宇宙线铅板阻挡实验物理背景

本文档用于整理本实验报告所需的物理背景，包括宇宙线来源与分布、双探测器符合测量原理、铅板阻挡能力、衰减拟合方法、Rossi 转换曲线，以及可供引用的参考文献。

## 1. 宇宙线来源与组成

宇宙线是来自地球大气层外的高能粒子流。原初宇宙线主要由质子、氦核和更重的原子核组成，也包含少量电子、正电子、反质子和其他粒子。高能原初宇宙线进入地球大气后，会与氮、氧等大气原子核发生强相互作用，产生级联簇射。

典型过程为：

```text
primary cosmic ray + atmosphere -> hadronic shower
hadronic shower -> pi+, pi-, K+, K-, ...
pi/K -> muon + neutrino
```

因此，在地面实验室中探测到的宇宙线带电粒子主要不是原初质子，而是大气簇射产生的次级粒子。其中，μ 子是海平面附近最重要、最容易穿透到探测器中的带电成分。

μ 子能够到达海平面的主要原因包括：

1. μ 子质量较大，电磁辐射损失相对较小。
2. GeV 量级 μ 子速度接近光速。
3. 相对论时间膨胀使其在实验室参考系中的有效寿命变长。

μ 子静止寿命为：

```text
tau_mu = 2.197 us
```

但高能 μ 子的洛伦兹因子：

```text
gamma = E_mu / (m_mu c^2)
```

会显著延长其实验室系寿命：

```text
tau_lab = gamma * tau_mu
```

因此大量 μ 子可以在衰变前到达地面。

## 2. 宇宙线通量与角分布

宇宙线通量常用强度或微分强度表示。一般定义为：

```text
dN = J(E, theta, phi) dE dA dOmega dt
```

其中：

- `dN`：能量区间 `dE`、面积 `dA`、立体角 `dOmega`、时间 `dt` 内穿过探测器的粒子数。
- `J`：宇宙线微分强度。
- `theta`：天顶角。
- `phi`：方位角。

地面 μ 子角分布常用近似形式：

```text
I(theta) = I(0) cos^n(theta)
```

对于 GeV 量级近垂直 μ 子，常见近似为：

```text
n ≈ 2
```

即：

```text
I(theta) ≈ I(0) cos^2(theta)
```

这意味着垂直方向入射的 μ 子最多，倾斜方向的通量较小。对于本实验，上下两个面积有限的闪烁体构成一个几何望远镜，天然更容易接受接近垂直方向的粒子。

如果上下探测器面积为 `A`，间距为 `d`，则双探测器符合率不仅取决于宇宙线真实通量，也取决于几何接受度：

```text
R_coin ∝ ∫ J(theta, phi) * epsilon(theta, phi) * A_eff(theta, phi) dOmega
```

其中：

- `epsilon`：探测效率。
- `A_eff`：有效几何面积。
- `dOmega`：可接受入射方向对应的立体角。

因此，本实验测得的符合率是“宇宙线通量、探测效率和几何接受度”的综合结果。

## 3. 双探测器符合测量原理

本实验使用上下两个闪烁体探测器。一个宇宙线粒子若依次穿过上、下探测器，就可能在两个探测器中都产生脉冲信号。通过数字化仪记录脉冲积分量：

```text
area  -> 上探测器脉冲积分
area2 -> 下探测器脉冲积分
```

实验中固定使用阈值：

```python
area > 30
area2 > 30
```

符合事件定义为：

```python
coincidence = (area > 30) & (area2 > 30)
```

对应计数：

```text
N_up   = count(area > 30)
N_down = count(area2 > 30)
N_coin = count((area > 30) & (area2 > 30))
```

双探测器符合率定义为：

```text
R_coin = N_coin / T
```

其中 `T` 为测量时间。本实验每个 run 的测量时间取：

```text
T = 1 hour = 3600 s
sigma_T = 1 min = 60 s
```

若以每小时计数表示：

```text
R_coin = N_coin counts/hour
```

若以 Hz 表示：

```text
R_coin = N_coin / 3600 s
```

符合计数的统计误差采用泊松分布：

```text
sigma_N = sqrt(N_coin)
```

考虑测量时间误差后：

```text
sigma_R / R_coin = sqrt(1 / N_coin + (sigma_T / T)^2)
```

代入本实验时间误差：

```text
sigma_R / R_coin = sqrt(1 / N_coin + (60 / 3600)^2)
```

## 4. 归一化符合比的物理意义

除了绝对符合率，还可以定义归一化符合比：

```text
Coin/Up = N_coin / N_up
Coin/Down = N_coin / N_down
```

其中 `Coin/Up` 可以理解为：

> 已经被上探测器记录到的候选事件中，有多少比例也被下探测器记录到。

由于铅板放置在上下探测器之间，上探测器近似作为入射候选事件的监视器，下探测器用于判断粒子是否仍能穿过铅板并保持在几何符合范围内。因此：

```text
Coin/Up ≈ P(下探测器也触发 | 上探测器已触发)
```

这个量具有明确物理意义，但不能解释为纯粹的铅吸收概率。它同时包含：

1. 铅板导致的粒子吸收或能量损失。
2. 多重散射导致粒子偏离下探测器。
3. 下探测器探测效率。
4. 探测器几何接受度。
5. 阈值响应变化。

因此，推荐表述为：

```text
Coin/Up 表示穿过铅板后仍能形成双探测器符合的有效概率。
```

第一周内部实验条件较一致，可以直接比较绝对符合率 `R_coin`。跨周分析时，由于探测器增益和效率可能变化，`Coin/Up` 可作为重要归一化量。

## 5. 铅板阻挡能力的定义

铅板对宇宙线的阻挡能力可以用相对符合率或有效透过率描述：

```text
Transmission(x) = R_coin(x) / R_coin(0)
```

其中：

- `x`：铅板厚度。
- `R_coin(x)`：厚度为 `x` 时的符合率。
- `R_coin(0)`：无铅板时的符合率。

有效阻挡能力定义为：

```text
Blocking(x) = 1 - Transmission(x)
```

例如：

```text
Transmission = 0.90
Blocking = 0.10
```

表示在该实验几何和阈值条件下，双探测器有效符合率降低了约 10%。

需要注意：

```text
Blocking 不等于 μ 子被铅板吸收的比例。
```

原因是符合率下降可能来自多种机制：

1. 低能电子、强子等软成分被铅板吸收。
2. μ 子经过铅板后发生多重散射，偏离下探测器。
3. 粒子能量损失导致脉冲积分低于阈值。
4. 次级粒子产生改变事件拓扑。
5. 探测器效率和几何接受度变化。

相对透过率误差可写为：

```text
sigma_Tx / Transmission =
sqrt(1 / N_coin(x) + 1 / N_coin(0) + (sigma_T / T)^2 + (sigma_T0 / T0)^2)
```

若两个测量均取：

```text
T = T0 = 3600 s
sigma_T = sigma_T0 = 60 s
```

则时间误差部分为：

```text
sqrt(2) * 60 / 3600 ≈ 2.36%
```

## 6. 铅中粒子能量损失

带电粒子穿过物质时，会与原子电子发生电磁相互作用并损失能量。对于 μ 子这类重带电粒子，在 GeV 能区主要能量损失机制是电离和激发。

常用近似为：

```text
dE/dx ≈ 1-2 MeV/(g/cm^2)
```

铅的密度为：

```text
rho_Pb = 11.34 g/cm^3
```

铅板厚度 `x` 对应质量厚度：

```text
X_mass = rho_Pb * x
```

其中 `x` 要用 cm。对于 30 mm 铅：

```text
x = 3.0 cm
X_mass = 11.34 * 3.0 = 34.02 g/cm^2
```

若取：

```text
dE/dx ≈ 2 MeV/(g/cm^2)
```

则 μ 子电离能损约为：

```text
Delta E ≈ 2 * 34.02 ≈ 68 MeV
```

相对于海平面 GeV 量级 μ 子，这一能损通常不足以让高能 μ 子完全停止。因此，实验中符合率降低不能简单解释为 μ 子被铅板完全吸收。对于本实验，更合理的解释通常包括：

- 多重散射降低几何符合概率。
- 低能成分被优先削弱。
- 软成分和次级粒子贡献发生变化。

## 7. 多重散射与几何符合效率

带电粒子穿过铅时会受到多个原子核库仑场的小角度偏转，形成多重散射。常用 Highland 近似公式描述散射角均方根：

```text
theta0 ≈ (13.6 MeV / (beta p c)) z sqrt(x / X0) [1 + 0.038 ln(x / X0)]
```

其中：

- `theta0`：投影散射角 RMS。
- `beta = v/c`。
- `p`：粒子动量。
- `z`：粒子电荷数，μ 子取 `z = 1`。
- `x`：材料厚度。
- `X0`：材料辐射长度。

铅的辐射长度约为：

```text
X0(Pb) ≈ 5.6 mm
```

本实验最大铅厚 30 mm，对应：

```text
x / X0 ≈ 30 / 5.6 ≈ 5.4
```

多重散射会使粒子方向发生偏转。由于上下探测器面积有限、间距有限，粒子即使没有被吸收，也可能因散射偏离下探测器有效区域，从而不再形成符合事件。因此，符合率下降可以来自：

```text
粒子仍存在，但不再满足双探测器几何符合条件。
```

这也是本实验中“有效阻挡能力”与“真实吸收概率”不同的核心原因。

## 8. Rossi 转换曲线

Rossi 转换曲线描述宇宙线通过吸收体后，计数率或符合率随吸收体厚度变化的曲线。经典实验中，计数器上方或之间加入不同厚度的金属吸收体，记录符合率变化。

理想化的 Rossi 曲线可能包含两个趋势：

1. 在较薄或中等厚度吸收体中，高能粒子与物质相互作用产生次级粒子，使计数率可能上升。
2. 在更厚吸收体中，粒子吸收、能量损失和散射占主导，使计数率下降。

因此，Rossi 曲线常被用于说明宇宙线中存在：

- 软成分：容易被铅等材料吸收，也容易产生电磁簇射。
- 硬成分：穿透能力强，主要与 μ 子相关。

在本实验中，铅板放在上下探测器之间，观测量是双探测器符合率：

```text
R_coin(x)
```

它与经典 Rossi 曲线类似，但不完全相同。因为本实验要求粒子或相关次级粒子同时触发上下探测器，所以几何符合效率非常重要。如果多重散射使粒子偏离下探测器，即使粒子没有被吸收，符合率也会下降。

因此，如果实验中没有观察到明显 Rossi 峰，可以从以下角度解释：

1. 探测器面积有限，几何接受度较小。
2. 双探测器符合条件抑制了偏离路径的次级粒子。
3. 铅板厚度点较少。
4. 两周测量存在探测效率差异。
5. 多重散射导致的符合效率降低可能强于次级粒子增强。

## 9. 衰减拟合方法

为了定量描述符合率随铅厚度下降的趋势，可以使用经验指数衰减模型：

```text
R_coin(x) = R0 exp(-x / lambda_eff)
```

或者对相对透过率拟合：

```text
Transmission(x) = exp(-x / lambda_eff)
```

其中：

- `R0`：无铅板时的符合率。
- `x`：铅板厚度，可用 mm、`g/cm^2` 或 `X/X0` 表示。
- `lambda_eff`：有效衰减长度。

如果使用质量厚度：

```text
Transmission(X_mass) = exp(-X_mass / Lambda_eff)
```

其中：

- `X_mass` 单位为 `g/cm^2`。
- `Lambda_eff` 单位为 `g/cm^2`。

取对数后：

```text
ln Transmission(x) = -x / lambda_eff
```

可用线性拟合作为交叉检查。但正式分析建议直接对 `Transmission` 做带误差的非线性拟合。

需要强调：

```text
lambda_eff 是实验条件下的有效衰减长度，不是 μ 子在铅中的纯吸收长度。
```

它包含：

1. 粒子真实吸收。
2. 电离能量损失。
3. 多重散射。
4. 探测器几何接受度。
5. 探测效率和阈值响应。
6. 宇宙线软、硬成分比例变化。

拟合优度可用：

```text
chi2 = sum_i [(y_i - f(x_i)) / sigma_i]^2
chi2_ndf = chi2 / (N_points - N_parameters)
```

其中 `y_i` 可取 `Transmission(x_i)`，`sigma_i` 为误差。

## 10. 本实验报告中的推荐表述

建议在报告中采用以下层次：

1. 第一周数据内部比较绝对符合率和相对透过率。
2. 第二周数据内部单独比较厚铅板区域趋势。
3. 跨周比较时不直接拼接绝对符合率，而使用 `Coin/Up` 或 0 片基准缩放。
4. 铅板阻挡能力用 `Blocking = 1 - Transmission` 表示。
5. 衰减拟合参数称为 `lambda_eff`，并明确它是有效量。

推荐句式：

> 本实验测得的不是铅对 μ 子的纯吸收概率，而是在固定探测器几何、固定阈值和有限接受角条件下，宇宙线事件仍能形成双探测器符合的有效概率随铅厚度的变化。

## 11. 可参考文献与资料

### 11.1 权威物理综述

1. Particle Data Group, "Cosmic Rays", Review of Particle Physics 2024.  
   用途：宇宙线组成、能谱、通量定义、各向异性和高能宇宙线背景。  
   链接：https://pdg.lbl.gov/2024/reviews/rpp2024-rev-cosmic-rays.pdf

2. Particle Data Group, "Passage of Particles Through Matter", Review of Particle Physics 2024.  
   用途：电离能损、Bethe 公式、多重散射、辐射长度、粒子穿过物质的标准公式。  
   链接：https://pdg.lbl.gov/2024/reviews/rpp2024-rev-passage-particles-matter.pdf

### 11.2 宇宙线 μ 子通量与角分布

3. M. Bektasoglu and H. Arslan, "Investigation of the zenith angle dependence of cosmic-ray muons at sea level", Pramana 80, 837-846 (2013).  
   用途：海平面 μ 子角分布、`cos^n(theta)` 形式和垂直 μ 子强度。  
   链接：https://link.springer.com/article/10.1007/s12043-013-0519-2

4. D. Guan et al., "A parametrization of the cosmic-ray muon flux at sea-level", arXiv:1509.06176.  
   用途：Gaisser 公式相关的海平面 μ 子通量参数化。  
   链接：https://arxiv.org/abs/1509.06176

5. L. Wang et al., "A New Semi-Empirical Model for Cosmic Ray Muon Flux Estimation", Progress of Theoretical and Experimental Physics (2022).  
   用途：海平面 μ 子通量模型和 μ 子通量估算。  
   链接：https://academic.oup.com/ptep/article/doi/10.1093/ptep/ptac016/6517769

### 11.3 Rossi 曲线与符合方法

6. B. Rossi, "Interaction between Cosmic Rays and Matter", Nature 132, 173 (1933).  
   用途：Rossi 早期符合方法和宇宙线与物质相互作用背景。  
   链接：https://www.nature.com/articles/132173b0

7. "The Second Maximum in the Rossi Transition Curve for Copper", Nature 145, 387 (1940).  
   用途：Rossi 转换曲线和吸收体厚度相关峰结构的历史参考。  
   链接：https://www.nature.com/articles/145387b0

8. A. Bonolis, "Walther Bothe and Bruno Rossi: the birth and development of coincidence methods in cosmic-ray physics", arXiv:1106.1365.  
   用途：符合技术在宇宙线实验中的发展历史。  
   链接：https://arxiv.org/abs/1106.1365

9. M. D'Agostino et al., "Exploring the Interaction of Cosmic Rays with Water by Using an Old-Style Detector and Rossi's Method", Instruments 6, 51 (2022).  
   用途：Rossi 方法的现代教学实验复现，可借鉴实验叙事和误差处理。  
   链接：https://www.mdpi.com/2571-712X/6/3/51

### 11.4 铅屏蔽与宇宙线计数实验

10. "Study of Shielding Effects on Cosmic Ray Rate", Süleyman Demirel University Faculty of Arts and Science Journal of Science.  
    用途：使用铅屏蔽研究宇宙线计数率和 Rossi 转换曲线的实验参考。  
    链接：https://dergipark.org.tr/en/pub/sdufeffd/issue/45380/479554

### 11.5 仪器参考

11. CAEN DT5742 product/manual page.  
    用途：数字化仪采样率、分辨率、通道和波形参数。  
    链接：https://www.caen.it/products/dt5742/

## 12. 写作注意事项

1. 不要把 `Blocking` 直接写成 μ 子吸收比例。
2. 不要把 `lambda_eff` 写成铅中 μ 子真实吸收长度。
3. 对第一周和第二周要先分开讨论。
4. 跨周比较时必须说明探测器效率和增益变化可能导致系统误差。
5. 如果 Rossi 峰不明显，应从几何接受度、多重散射和双符合条件解释，而不是认为实验失败。
