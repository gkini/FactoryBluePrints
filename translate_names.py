#!/usr/bin/env python3
"""
Translate Chinese file and folder names to English using Argos Translate.
Uses official Dyson Sphere Program terminology from the wiki where available.
Renames files/folders in place, preserving directory structure.
"""

import os
import sys
import re
import argparse
from pathlib import Path

try:
    import argostranslate.package
    import argostranslate.translate
except ImportError:
    print("Error: argostranslate not installed.")
    print("Install with: pip install argostranslate")
    sys.exit(1)


# Official Dyson Sphere Program Chinese → English mappings
# Source: https://dsp-wiki.com/
DSP_DICTIONARY = {
    # === Natural Resources ===
    "铁矿": "Iron-Ore",
    "铜矿": "Copper-Ore",
    "石矿": "Stone",
    "煤矿": "Coal",
    "煤": "Coal",
    "硅石": "Silicon-Ore",
    "钛矿": "Titanium-Ore",
    "水": "Water",
    "原油": "Crude-Oil",
    "氢": "Hydrogen",
    "重氢": "Deuterium",
    "氘": "Deuterium",
    "反物质": "Antimatter",
    "临界光子": "Critical-Photon",
    "核心素": "Core-Element",
    "金伯利矿石": "Kimberlite-Ore",
    "可燃冰": "Fire-Ice",
    "木材": "Log",
    "有机晶体": "Organic-Crystal",
    "植物燃料": "Plant-Fuel",
    "硫酸": "Sulfuric-Acid",
    "单极磁石": "Unipolar-Magnet",
    "光栅石": "Grating-Crystal",
    "刺笋结晶": "Spiniform-Stalagmite-Crystal",
    "刺笋": "Spiniform-Stalagmite",
    "分形硅石": "Fractal-Silicon",

    # === Intermediate Products ===
    "铁块": "Iron-Ingot",
    "铜块": "Copper-Ingot",
    "石材": "Stone-Brick",
    "高能石墨": "Energetic-Graphite",
    "高纯硅块": "High-Purity-Silicon",
    "晶格硅": "High-Purity-Silicon",
    "钛块": "Titanium-Ingot",
    "钛合金": "Titanium-Alloy",
    "精炼油": "Refined-Oil",
    "钢材": "Steel",
    "电路板": "Circuit-Board",
    "棱镜": "Prism",
    "电动机": "Electric-Motor",
    "微晶元件": "Microcrystalline-Component",
    "钛晶石": "Titanium-Crystal",
    "碳纳米管": "Carbon-Nanotube",
    "粒子宽带": "Particle-Broadband",
    "齿轮": "Gear",
    "等离子激发器": "Plasma-Exciter",
    "光子合并器": "Photon-Combiner",
    "电磁涡轮": "Electromagnetic-Turbine",
    "处理器": "Processor",
    "卡西米尔晶体": "Casimir-Crystal",
    "钛化玻璃": "Titanium-Glass",
    "位面过滤器": "Plane-Filter",
    "量子芯片": "Quantum-Chip",
    "引擎": "Engine",
    "推进器": "Thruster",
    "加力推进器": "Reinforced-Thruster",
    "超级磁场环": "Super-Magnetic-Ring",
    "粒子容器": "Particle-Container",
    "奇异物质": "Strange-Matter",
    "玻璃": "Glass",
    "磁铁": "Magnet",
    "磁线圈": "Magnetic-Coil",
    "金刚石": "Diamond",
    "石墨烯": "Graphene",
    "硅基神经元": "Silicon-based-Neuron",
    "物质重组器": "Matter-Recombinator",
    "能量碎片": "Energy-Shard",
    "负熵奇点": "Negentropy-Singularity",

    # === Proliferators ===
    "增产剂": "Proliferator",

    # === Logistics Items ===
    "物流运输机": "Logistics-Bot",
    "物流运输船": "Logistics-Vessel",
    "星际物流运输船": "Logistics-Vessel",
    "空间翘曲器": "Space-Warper",
    "翘曲器": "Space-Warper",
    "引力透镜": "Graviton-Lens",
    "地基": "Foundation",

    # === Dyson Sphere Components ===
    "太阳帆": "Solar-Sail",
    "框架材料": "Frame-Material",
    "戴森球组件": "Dyson-Sphere-Component",
    "小型运载火箭": "Small-Carrier-Rocket",
    "运载火箭": "Carrier-Rocket",
    "戴森球": "Dyson-Sphere",

    # === Fuel Rods ===
    "氢燃料棒": "Hydrogen-Fuel-Rod",
    "液氢燃料棒": "Hydrogen-Fuel-Rod",
    "氘核燃料棒": "Deuteron-Fuel-Rod",
    "反物质燃料棒": "Antimatter-Fuel-Rod",
    "奇异湮灭燃料棒": "Strange-Annihilation-Fuel-Rod",
    "燃料棒": "Fuel-Rod",

    # === Science Matrices (糖 = Sugar/Jello/Cube) ===
    "电磁矩阵": "Electromagnetic-Matrix",
    "能量矩阵": "Energy-Matrix",
    "结构矩阵": "Structure-Matrix",
    "信息矩阵": "Information-Matrix",
    "引力矩阵": "Gravity-Matrix",
    "宇宙矩阵": "Universe-Matrix",
    "黑雾矩阵": "Dark-Fog-Matrix",
    "矩阵": "Matrix",
    "蓝糖": "Electromagnetic-Matrix",
    "红糖": "Energy-Matrix",
    "黄糖": "Structure-Matrix",
    "紫糖": "Information-Matrix",
    "绿糖": "Gravity-Matrix",
    "白糖": "Universe-Matrix",
    "彩糖": "Science-Matrix",

    # === Power Buildings ===
    "特斯拉塔": "Tesla-Tower",
    "无线输电塔": "Wireless-Power-Tower",
    "输电塔": "Power-Tower",
    "卫星配电站": "Satellite-Substation",
    "风力涡轮机": "Wind-Turbine",
    "风电": "Wind-Turbine",
    "风能": "Wind-Power",
    "火力发电厂": "Thermal-Power-Plant",
    "火力发电": "Thermal-Power",
    "火电": "Thermal-Power",
    "火力": "Thermal-Power",
    "太阳能板": "Solar-Panel",
    "太阳能": "Solar-Power",
    "地热发电站": "Geothermal-Power-Station",
    "地热发电": "Geothermal-Power",
    "微型聚变发电站": "Mini-Fusion-Power-Station",
    "聚变发电": "Fusion-Power",
    "核电": "Nuclear-Power",
    "能量枢纽": "Energy-Exchanger",
    "蓄电器": "Accumulator",
    "满蓄电器": "Full-Accumulator",
    "射线接收站": "Ray-Receiver",
    "人造恒星": "Artificial-Star",
    "小太阳": "Artificial-Star",
    "发电": "Power-Generation",

    # === Logistics Buildings ===
    "传送带": "Conveyor-Belt",
    "四向分流器": "Splitter",
    "分流器": "Splitter",
    "自动集装机": "Automatic-Piler",
    "流速监测器": "Traffic-Monitor",
    "流速计": "Traffic-Monitor",
    "储物仓": "Storage",
    "箱子": "Storage",
    "仓储": "Storage",
    "储液罐": "Storage-Tank",
    "物流配送器": "Logistics-Distributor",
    "行星内物流运输站": "Planetary-Logistics-Station",
    "星际物流运输站": "Interstellar-Logistics-Station",
    "物流塔": "Logistics-Station",
    "物流站": "Logistics-Station",
    "轨道采集器": "Orbital-Collector",
    "分拣器": "Sorter",
    "集装分拣器": "Pile-Sorter",
    "充电": "Charging",

    # === Resource Extraction ===
    "采矿机": "Mining-Machine",
    "大型采矿机": "Advanced-Mining-Machine",
    "矿机": "Mining-Machine",
    "采矿": "Mining",
    "抽水站": "Water-Pump",
    "抽水机": "Water-Pump",
    "原油萃取站": "Oil-Extractor",
    "原油精炼厂": "Oil-Refinery",
    "分馏塔": "Fractionator",
    "分馏": "Fractionation",

    # === Production Buildings ===
    "电弧熔炉": "Arc-Smelter",
    "熔炉": "Smelter",
    "位面熔炉": "Plane-Smelter",
    "负熵熔炉": "Negentropy-Smelter",
    "制造台": "Assembling-Machine",
    "重组式制造台": "Re-composing-Assembler",
    "矩阵研究站": "Matrix-Lab",
    "研究站": "Lab",
    "自演化研究站": "Self-evolution-Lab",
    "喷涂机": "Spray-Coater",
    "化工厂": "Chemical-Plant",
    "量子化工厂": "Quantum-Chemical-Plant",
    "微型粒子对撞机": "Miniature-Particle-Collider",
    "粒子对撞机": "Particle-Collider",

    # === Military Buildings ===
    "电磁轨道弹射器": "EM-Rail-Ejector",
    "弹射器": "EM-Rail-Ejector",
    "垂直发射井": "Vertical-Launching-Silo",
    "发射井": "Launching-Silo",
    "高斯机枪塔": "Gauss-Turret",
    "导弹防御塔": "Missile-Turret",
    "聚爆加农炮": "Implosion-Cannon",
    "激光塔": "Laser-Turret",
    "等离子炮塔": "Plasma-Turret",
    "战场分析基站": "Battlefield-Analysis-Base",
    "干扰塔": "Jammer-Tower",
    "信号塔": "Signal-Tower",
    "行星护盾发生器": "Planetary-Shield-Generator",
    "黑雾": "Dark-Fog",

    # === Game Terms ===
    "蓝图": "Blueprint",
    "蓝图包": "Blueprint-Book",
    "新蓝图": "New-Blueprint",
    "开荒": "Early-Game",
    "前期": "Early-Game",
    "中期": "Mid-Game",
    "后期": "Late-Game",
    "大后期": "End-Game",
    "全流程": "Full-Playthrough",
    "全球": "Global",
    "赤道": "Equator",
    "极地": "Polar",
    "堆叠": "Stacked",
    "无带": "Belt-Free",
    "有带": "With-Belt",
    "黑盒": "Black-Box",
    "超市": "Mall",
    "建筑超市": "Building-Mall",
    "原矿": "Raw-Ore",
    "模组": "Mod",
    "模块": "Module",
    "艺术": "Art",
    "音乐": "Music",
    "过期": "Expired",
    "仙术": "Exploit",
    "垃圾桶": "Garbage-Disposal",
    "其它": "Other",
    "其他": "Other",
    "说明": "Instructions",
    "简介": "Introduction",
    "注释": "Notes",
    "使用": "Usage",
    "产量": "Output",
    "层": "Layer",
    "版本": "Version",
    "节点": "Node",
    "最密": "Densest",
    "极密": "Ultra-Dense",
    "密铺": "Dense-Tile",
    "可扩展": "Expandable",
    "低纬度": "Low-Latitude",
    "高纬度": "High-Latitude",
    "分布式": "Distributed",
    "配套": "Supporting",
    "设施": "Facilities",
    "建造": "Construction",
    "生产": "Production",
    "制造": "Manufacturing",
    "发射": "Launch",
    "透镜": "Lens",
    "锅盖": "Ray-Receiver",
}


def setup_translation():
    """Download and install Chinese to English translation package if needed."""
    from_code = "zh"
    to_code = "en"

    # Update package index
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()

    # Find Chinese to English package
    package_to_install = next(
        (pkg for pkg in available_packages
         if pkg.from_code == from_code and pkg.to_code == to_code),
        None
    )

    if package_to_install is None:
        print(f"Error: No translation package found for {from_code} -> {to_code}")
        sys.exit(1)

    # Check if already installed
    installed_packages = argostranslate.package.get_installed_packages()
    is_installed = any(
        pkg.from_code == from_code and pkg.to_code == to_code
        for pkg in installed_packages
    )

    if not is_installed:
        print("Downloading Chinese to English translation package...")
        argostranslate.package.install_from_path(package_to_install.download())
        print("Package installed successfully.")

    return argostranslate.translate.get_translation_from_codes(from_code, to_code)


def contains_chinese(text):
    """Check if text contains Chinese characters."""
    return bool(re.search(r'[\u4e00-\u9fff]', text))


def extract_chinese_segments(text):
    """Extract Chinese character sequences from text with their positions."""
    return [(m.group(), m.start(), m.end()) for m in re.finditer(r'[\u4e00-\u9fff]+', text)]


def translate_with_dictionary(chinese_text, translator):
    """
    Translate Chinese text using DSP dictionary first, falling back to Argos.
    Uses longest match first to handle compound terms correctly.
    """
    # Sort dictionary keys by length (longest first) for greedy matching
    sorted_terms = sorted(DSP_DICTIONARY.keys(), key=len, reverse=True)

    result = chinese_text
    matched_ranges = []

    # First pass: find all dictionary matches (longest first)
    for term in sorted_terms:
        start = 0
        while True:
            idx = result.find(term, start)
            if idx == -1:
                break

            end = idx + len(term)
            # Check if this range overlaps with already matched ranges
            overlaps = any(
                not (end <= m_start or idx >= m_end)
                for m_start, m_end, _ in matched_ranges
            )

            if not overlaps:
                matched_ranges.append((idx, end, DSP_DICTIONARY[term]))

            start = idx + 1

    # Sort matches by position
    matched_ranges.sort(key=lambda x: x[0])

    # Build result by replacing matched ranges and translating unmatched Chinese
    if matched_ranges:
        parts = []
        last_end = 0

        for start, end, replacement in matched_ranges:
            # Add text before this match
            before = result[last_end:start]
            if before:
                # Translate any remaining Chinese in the gap
                if contains_chinese(before):
                    before = translate_remaining_chinese(before, translator)
                parts.append(before)

            parts.append(replacement)
            last_end = end

        # Add remaining text after last match
        after = result[last_end:]
        if after:
            if contains_chinese(after):
                after = translate_remaining_chinese(after, translator)
            parts.append(after)

        return ''.join(parts)
    else:
        # No dictionary matches, use Argos translation
        return translate_remaining_chinese(result, translator)


def translate_remaining_chinese(text, translator):
    """Translate any remaining Chinese characters using Argos."""
    segments = extract_chinese_segments(text)
    if not segments:
        return text

    result = text
    # Process in reverse order to preserve positions
    for chinese, start, end in reversed(segments):
        translated = translator.translate(chinese)
        translated = translated.strip()
        translated = re.sub(r'\s+', '-', translated)
        translated = re.sub(r'[^\w\-.]', '', translated)
        result = result[:start] + translated + result[end:]

    return result


def translate_name(name, translator):
    """
    Translate Chinese parts of a filename/dirname to English.
    Uses DSP dictionary for game terms, Argos for everything else.
    Preserves non-Chinese parts and file extensions.
    """
    if not contains_chinese(name):
        return name

    # Separate extension for files
    path = Path(name)
    stem = path.stem if path.suffix else name
    suffix = path.suffix if path.suffix else ""

    # Translate using dictionary + Argos fallback
    translated_stem = translate_with_dictionary(stem, translator)

    # Clean up the result
    translated_stem = re.sub(r'-+', '-', translated_stem)  # Remove multiple dashes
    translated_stem = translated_stem.strip('-')  # Remove leading/trailing dashes

    return translated_stem + suffix


def rename_item(old_path, new_name, dry_run=False):
    """Rename a file or directory."""
    old_path = Path(old_path)
    new_path = old_path.parent / new_name

    if old_path == new_path:
        return None

    # Handle name conflicts
    if new_path.exists():
        counter = 1
        stem = new_path.stem if new_path.suffix else new_name
        suffix = new_path.suffix
        while new_path.exists():
            new_name = f"{stem}_{counter}{suffix}"
            new_path = old_path.parent / new_name
            counter += 1

    if dry_run:
        print(f"  [DRY RUN] {old_path.name} -> {new_name}")
    else:
        os.rename(old_path, new_path)
        print(f"  Renamed: {old_path.name} -> {new_name}")

    return new_path


def translate_directory(root_dir, translator, dry_run=False):
    """
    Recursively translate all file and folder names in a directory.
    Processes depth-first to handle nested renames correctly.
    """
    root_dir = Path(root_dir).resolve()

    # Collect all items first (to avoid issues with renaming during iteration)
    items_to_process = []

    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        dirpath = Path(dirpath)

        # Skip .git and .venv directories
        if '.git' in dirpath.parts or '.venv' in dirpath.parts:
            continue

        # Process files first
        for filename in filenames:
            if contains_chinese(filename):
                items_to_process.append(('file', dirpath / filename))

        # Then directories
        for dirname in dirnames:
            if dirname in ('.git', '.venv'):
                continue
            if contains_chinese(dirname):
                items_to_process.append(('dir', dirpath / dirname))

    if not items_to_process:
        print("No files or folders with Chinese names found.")
        return

    print(f"Found {len(items_to_process)} items to translate.\n")

    # Process items (already in bottom-up order from os.walk)
    renamed_count = 0
    for item_type, item_path in items_to_process:
        if not item_path.exists():
            # Path may have changed due to parent directory rename
            continue

        old_name = item_path.name
        new_name = translate_name(old_name, translator)

        if old_name != new_name:
            rename_item(item_path, new_name, dry_run)
            renamed_count += 1

    print(f"\n{'Would rename' if dry_run else 'Renamed'} {renamed_count} items.")


def main():
    parser = argparse.ArgumentParser(
        description="Translate Chinese file/folder names to English using Argos Translate with DSP wiki terms"
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to process (default: current directory)"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Show what would be renamed without making changes"
    )

    args = parser.parse_args()

    root_dir = Path(args.directory).resolve()
    if not root_dir.is_dir():
        print(f"Error: {root_dir} is not a valid directory")
        sys.exit(1)

    print(f"Processing directory: {root_dir}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print(f"Using {len(DSP_DICTIONARY)} DSP-specific term mappings\n")

    print("Setting up translation...")
    translator = setup_translation()
    print("Translation ready.\n")

    translate_directory(root_dir, translator, args.dry_run)


if __name__ == "__main__":
    main()
