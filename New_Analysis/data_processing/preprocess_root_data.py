#!/usr/bin/env python3
"""将 CAEN ROOT 原始数据预处理为轻量 NumPy 数据集。

原始 ROOT 文件中包含较大的波形类 jagged 分支。后续符合计数、能谱和
归一化分析主要需要事件级标量变量，因此本脚本只保留关键标量分支，
每个 run 输出一个压缩 ``.npz`` 文件，并额外生成 CSV/JSON 摘要。
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import uproot


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "Raw_data"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "Processed_data"

# 默认保存的核心分支：覆盖符合选择、能谱、基线噪声和基本质量检查。
CORE_BRANCHES = [
    "area",
    "area2",
    "amp",
    "base",
    "rms",
    "Index_minamp",
]

# 扩展分支：不是主分析必需，但可用于更细的诊断。
EXTENDED_BRANCHES = [
    "Index",
    "overshoot",
    "overshoot_Last",
]

# 只有时间校准文件 5181b.root 中存在这些分通道时间字段。
OPTIONAL_TIME_BRANCHES = [
    "event_num",
    "Index_minamp1",
    "Index_minamp2",
]

# 实验 run 元数据。这里采用顶层 README 的标注：
# 第一周为 0-30 片铅板，第二周为 0、40、50、60 片铅板。
RUNS = {
    "5181": {
        "file": RAW_DATA_DIR / "5181.root",
        "week": 1,
        "lead_plates": 0,
    },
    "5182": {
        "file": RAW_DATA_DIR / "5182.root",
        "week": 1,
        "lead_plates": 10,
    },
    "5183": {
        "file": RAW_DATA_DIR / "5183.root",
        "week": 1,
        "lead_plates": 20,
    },
    "5184": {
        "file": RAW_DATA_DIR / "5184.root",
        "week": 1,
        "lead_plates": 30,
    },
    "51811": {
        "file": RAW_DATA_DIR / "51811.root",
        "week": 2,
        "lead_plates": 0,
    },
    "5185": {
        "file": RAW_DATA_DIR / "5185.root",
        "week": 2,
        "lead_plates": 40,
    },
    "5186": {
        "file": RAW_DATA_DIR / "5186.root",
        "week": 2,
        "lead_plates": 50,
    },
    "5187": {
        "file": RAW_DATA_DIR / "5187.root",
        "week": 2,
        "lead_plates": 60,
    },
    "5181b": {
        "file": RAW_DATA_DIR / "add_time_5181b" / "5181b.root",
        "week": 1,
        "lead_plates": 0,
        "purpose": "time_calibrated",
    },
}

# 铅板和铅材料参数，用于把“铅板片数”换算为报告中的物理横轴。
LEAD_PLATE_THICKNESS_MM = 0.5 
LEAD_DENSITY_G_CM3 = 11.34
LEAD_RADIATION_LENGTH_MM = 5.6


@dataclass
class RunSummary:
    """单个 run 的预处理摘要，最终写入 CSV/JSON。"""

    run: str
    source_file: str
    output_file: str
    week: int
    lead_plates: int
    lead_thickness_mm: float
    radiation_lengths: float
    mass_thickness_g_cm2: float
    entries: int
    saved_branches: str
    missing_branches: str
    area_mean: float | None
    area2_mean: float | None
    area_gt_30: int | None
    area2_gt_30: int | None
    coincidence_30_30: int | None


def parse_args() -> argparse.Namespace:
    """解析命令行参数，允许选择原始数据目录、输出目录和 run 列表。"""

    parser = argparse.ArgumentParser(
        description="Convert CAEN ROOT files to lightweight NumPy npz files."
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=RAW_DATA_DIR,
        help="Directory containing ROOT files. Default: project Raw_data directory.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for processed outputs. Default: project Processed_data.",
    )
    parser.add_argument(
        "--runs",
        nargs="+",
        default=list(RUNS),
        help="Run IDs to process. Default: all known runs.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing npz files.",
    )
    parser.add_argument(
        "--branches",
        choices=["core", "extended"],
        default="core",
        help=(
            "Branch set to save. 'core' keeps area/area2 and basic diagnostics; "
            "'extended' also saves Index and overshoot fields."
        ),
    )
    return parser.parse_args()


def resolve_runs(raw_dir: Path, run_ids: Iterable[str]) -> dict[str, dict]:
    """根据用户指定的 run ID 生成实际输入文件路径。

    RUNS 中保存的是默认 Raw_data 目录下的路径。若用户通过 --raw-dir
    指定了其他原始数据目录，这里会保持相对路径不变并切换根目录。
    """

    runs: dict[str, dict] = {}
    for run_id in run_ids:
        if run_id not in RUNS:
            valid = ", ".join(RUNS)
            raise ValueError(f"Unknown run {run_id!r}. Valid runs: {valid}")
        info = dict(RUNS[run_id])
        relative = info["file"].relative_to(RAW_DATA_DIR)
        info["file"] = raw_dir / relative
        runs[run_id] = info
    return runs


def ensure_output_dirs(output_dir: Path) -> tuple[Path, Path]:
    """创建输出目录。

    npz/ 保存每个 run 的数组数据，summary/ 保存预处理统计摘要。
    """

    npz_dir = output_dir / "npz"
    summary_dir = output_dir / "summary"
    npz_dir.mkdir(parents=True, exist_ok=True)
    summary_dir.mkdir(parents=True, exist_ok=True)
    return npz_dir, summary_dir


def available_scalar_branches(
    tree: uproot.TTree, branch_mode: str
) -> tuple[list[str], list[str]]:
    """筛选当前 ROOT tree 中实际存在且需要保存的标量分支。

    普通 ROOT 文件没有 Index_minamp1/Index_minamp2 等分通道时间字段，
    因此这些可选分支不存在时只记录到 missing_branches，不报错。
    """

    tree_branches = set(tree.keys())
    requested = list(CORE_BRANCHES)
    if branch_mode == "extended":
        requested.extend(EXTENDED_BRANCHES)
    requested.extend(OPTIONAL_TIME_BRANCHES)
    present = [name for name in requested if name in tree_branches]
    missing = [name for name in requested if name not in tree_branches]
    return present, missing


def lead_metadata(lead_plates: int) -> tuple[float, float, float]:
    """由铅板片数计算厚度、辐射长度单位和质量厚度。"""

    thickness_mm = lead_plates * LEAD_PLATE_THICKNESS_MM
    radiation_lengths = thickness_mm / LEAD_RADIATION_LENGTH_MM
    mass_thickness = (thickness_mm / 10.0) * LEAD_DENSITY_G_CM3
    return thickness_mm, radiation_lengths, mass_thickness


def scalar_summary(arrays: dict[str, np.ndarray]) -> dict[str, float | int | None]:
    """计算快速质量检查量。

    固定阈值 area > 30、area2 > 30 来自实验规划文档，用于给出
    后续报告采用的标准符合数。
    """

    area = arrays.get("area")
    area2 = arrays.get("area2")
    if area is None or area2 is None:
        return {
            "area_mean": None,
            "area2_mean": None,
            "area_gt_30": None,
            "area2_gt_30": None,
            "coincidence_30_30": None,
        }

    area_mask = area > 30
    area2_mask = area2 > 30
    return {
        "area_mean": float(np.mean(area)),
        "area2_mean": float(np.mean(area2)),
        "area_gt_30": int(np.count_nonzero(area_mask)),
        "area2_gt_30": int(np.count_nonzero(area2_mask)),
        "coincidence_30_30": int(np.count_nonzero(area_mask & area2_mask)),
    }


def process_run(
    run: str, info: dict, npz_dir: Path, overwrite: bool, branch_mode: str
) -> RunSummary:
    """处理单个 ROOT 文件并返回摘要。"""

    source_file = Path(info["file"])
    if not source_file.exists():
        raise FileNotFoundError(f"Missing ROOT file: {source_file}")

    output_file = npz_dir / f"{run}.npz"
    if output_file.exists() and not overwrite:
        raise FileExistsError(
            f"Output already exists: {output_file}. Use --overwrite to replace it."
        )

    with uproot.open(source_file) as root_file:
        if "t1" not in root_file:
            raise KeyError(f"{source_file} does not contain tree 't1'")
        tree = root_file["t1"]
        branches, missing = available_scalar_branches(tree, branch_mode)

        # 只读取筛选后的标量分支，避免保存 ADC 等大型波形分支。
        arrays = tree.arrays(branches, library="np")

    thickness_mm, radiation_lengths, mass_thickness = lead_metadata(info["lead_plates"])

    # payload 中既包含逐事件数组，也包含 run 级元数据，方便后续分析脚本
    # 只打开 npz 文件即可知道该 run 的铅厚和测量周次。
    payload = {name: arrays[name] for name in branches}
    payload.update(
        {
            "run": np.array(run),
            "week": np.array(info["week"], dtype=np.int16),
            "lead_plates": np.array(info["lead_plates"], dtype=np.int16),
            "lead_thickness_mm": np.array(thickness_mm, dtype=np.float32),
            "radiation_lengths": np.array(radiation_lengths, dtype=np.float32),
            "mass_thickness_g_cm2": np.array(mass_thickness, dtype=np.float32),
        }
    )
    np.savez_compressed(output_file, **payload)

    # 摘要文件用于快速检查每个 run 的规模、均值和默认符合数。
    stats = scalar_summary(payload)
    return RunSummary(
        run=run,
        source_file=str(source_file),
        output_file=str(output_file),
        week=info["week"],
        lead_plates=info["lead_plates"],
        lead_thickness_mm=thickness_mm,
        radiation_lengths=radiation_lengths,
        mass_thickness_g_cm2=mass_thickness,
        entries=int(len(next(iter(arrays.values())))) if arrays else 0,
        saved_branches=";".join(branches),
        missing_branches=";".join(missing),
        area_mean=stats["area_mean"],
        area2_mean=stats["area2_mean"],
        area_gt_30=stats["area_gt_30"],
        area2_gt_30=stats["area2_gt_30"],
        coincidence_30_30=stats["coincidence_30_30"],
    )


def write_summaries(summaries: list[RunSummary], summary_dir: Path) -> None:
    """把所有 run 的摘要同时写成 JSON 和 CSV。"""

    dicts = [asdict(summary) for summary in summaries]

    json_path = summary_dir / "preprocess_summary.json"
    csv_path = summary_dir / "preprocess_summary.csv"

    json_path.write_text(json.dumps(dicts, indent=2), encoding="utf-8")

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(dicts[0]))
        writer.writeheader()
        writer.writerows(dicts)


def main() -> None:
    """脚本入口：创建目录、逐个处理 run、最后写摘要。"""

    args = parse_args()
    npz_dir, summary_dir = ensure_output_dirs(args.output_dir)
    runs = resolve_runs(args.raw_dir, args.runs)

    summaries: list[RunSummary] = []
    for run, info in runs.items():
        summary = process_run(run, info, npz_dir, args.overwrite, args.branches)
        summaries.append(summary)
        print(
            f"processed {run}: entries={summary.entries}, "
            f"coin30={summary.coincidence_30_30}, output={summary.output_file}"
        )

    if summaries:
        write_summaries(summaries, summary_dir)
        print(f"wrote summaries to {summary_dir}")


if __name__ == "__main__":
    main()
