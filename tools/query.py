#!/usr/bin/env python3
"""Read-only, offline lookup of the checked DRAENERT catalog.

No packages, network access, or persistent assistant state are required.
The catalog records remain the source of every fact returned by this tool.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any


DEFAULT_CATALOG = Path(__file__).resolve().parent.parent / "data" / "catalog.json"
STOCK_NOTE = (
    "官网资料为核验日期的快照。天然石板的颜色、纹理及库存以具体板材和官网最新状态为准；"
    "本结果不保证当前库存。"
)
DOWNLOAD_NOTE = (
    "仅 status=link_observed 且带 URL 的格式链接可作为已观测下载链接；"
    "未解析的链接和格式标记不代表文件已取得或已验证。"
)

COLOR_ALIASES = {
    "blue": ("blue", "blau", "蓝色", "蓝", "藍色", "藍"),
    "black": ("black", "schwarz", "黑色", "黑"),
    "white": ("white", "weiß", "weiss", "白色", "白"),
    "gray": ("gray", "grey", "grau", "灰色", "灰"),
    "brown": ("brown", "braun", "棕色", "棕", "褐色", "褐"),
    "green": ("green", "grün", "gruen", "绿色", "绿", "綠色", "綠"),
    "yellow": ("yellow", "gelb", "黄色", "黄", "黃色", "黃"),
    "beige": ("beige", "米色", "米白色"),
    "red": ("red", "rot", "红色", "红", "紅色", "紅"),
    "pink": ("pink", "rosa", "粉色", "粉红色", "粉紅色"),
    "purple": ("purple", "violet", "violett", "lila", "紫色", "紫"),
    "orange": ("orange", "橙色", "橙"),
    "multicolor": ("multicolor", "multicolour", "bunt", "mehrfarbig", "多色", "彩色"),
}
KIND_ALIASES = {
    "product": ("product", "products", "produkt", "produkte", "产品", "產品", "家具"),
    "stone": ("stone", "stones", "stein", "naturstein", "石材", "石料", "石板"),
    "wood": ("wood", "holz", "木材", "木料", "实木", "實木"),
    "leather": ("leather", "leder", "皮革", "真皮"),
    "fabric": ("fabric", "stoff", "布料", "面料"),
    "entry": ("entry", "入口", "页面", "頁面"),
}
TERM_ALIASES = (
    ("餐桌", "dining table", "dining", "esstisch", "esstische"),
    ("茶几", "coffee table", "couchtisch", "couchtische"),
    ("边桌", "邊桌", "side table", "beistelltisch", "beistelltische"),
    ("吧椅", "吧凳", "bar stool", "barhocker"),
    ("椅子", "座椅", "chair", "chairs", "stuhl", "stühle", "stuehle"),
    ("户外", "戶外", "outdoor"),
    ("可伸缩", "可伸縮", "伸缩", "伸縮", "可延长", "伸展", "extendable", "ausziehbar", "ausziehbare", "auszug"),
    ("石英岩", "quartzite", "quarzit"),
    ("花岗岩", "花崗岩", "granite", "granit"),
    ("大理石", "marble", "marmor"),
    ("方钠石", "方鈉石", "sodalite", "sodalith"),
    ("玻璃", "glass", "glas"),
    ("巴西", "brazil", "brasilien"),
    ("纳米比亚", "納米比亞", "namibia"),
    ("赞比亚", "贊比亞", "zambia", "sambia"),
    ("加拿大", "canada", "kanada"),
)
VARIANT_MARKERS = frozenset(("magnum", "outdoor"))
ROMAN_VARIANTS = frozenset(("i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"))
CHINESE_NOISE = (
    "请帮我", "請幫我", "给到我", "給到我", "我需要", "帮我", "幫我", "给我", "給我",
    "可下载的", "可下載的", "下载", "下載", "查找", "找到", "查询", "查詢", "提供", "需要",
    "相对应", "相對應", "相关", "相關", "资料", "資料", "信息", "模型", "型号", "型號",
    "板子", "板材", "颜色", "顏色", "表面", "色调", "色調", "请", "請", "的", "为", "為",
)
ENGLISH_NOISE = frozenset(("a", "an", "the", "of", "for", "please", "find", "show", "give", "me", "model", "models", "cad", "3d", "download", "downloads", "information"))
QUERY_FORMATS = frozenset(("dwg", "dxf", "3ds", "obj", "fbx", "stl", "skp", "step", "stp", "iges", "igs"))


def normalize(value: Any) -> str:
    """Normalize for comparison without changing a catalog's display values."""
    value = unicodedata.normalize("NFKC", str(value or "")).casefold()
    return " ".join(re.findall(r"[^\W_]+", value, flags=re.UNICODE))


def canonical(value: Any, aliases: dict[str, tuple[str, ...]]) -> str | None:
    normalized = normalize(value)
    for key, values in aliases.items():
        if normalized in {normalize(item) for item in (key, *values)}:
            return key
    return None


def canonical_format(value: Any) -> str:
    return str(value or "").strip().casefold().lstrip(".")


def contains(text: str, term: str) -> bool:
    return f" {normalize(term)} " in f" {text} "


def string_values(value: Any) -> list[str]:
    if isinstance(value, dict):
        return [item for nested in value.values() for item in string_values(nested)]
    if isinstance(value, (tuple, list)):
        return [item for nested in value for item in string_values(nested)]
    return [str(value)] if value is not None else []


def record_aliases(record: dict[str, Any]) -> list[str]:
    aliases = [str(record.get("name", ""))]
    model = normalize(record.get("model_number"))
    name = normalize(record.get("name"))
    if model and name.startswith(model + " "):
        aliases.append(name[len(model) + 1 :])
    for key, value in record.get("attributes", {}).items():
        if "synonym" in normalize(key):
            aliases.extend(re.split(r"[,;|/\n]", str(value)))
    return [normalize(alias) for alias in aliases if normalize(alias)]


def observed_downloads(record: dict[str, Any], file_format: str | None = None) -> list[dict[str, Any]]:
    """Only recorded, resolved options count; never infer URLs from names."""
    return [
        option for option in record.get("download_options", [])
        if isinstance(option, dict)
        and option.get("status") == "link_observed"
        and isinstance(option.get("url"), str)
        and option["url"].strip()
        and (file_format is None or canonical_format(option.get("format")) == file_format)
    ]


def parse_terms(query: str) -> tuple[list[tuple[str, ...]], str, set[str], str | None]:
    text = unicodedata.normalize("NFKC", query).casefold()
    # Chinese color requests mean a color classification. English proper names,
    # such as Blue Pearl, remain names unless --color is explicitly supplied.
    inferred_color = None
    for color, aliases in COLOR_ALIASES.items():
        for alias in sorted(aliases, key=len, reverse=True):
            if re.search(r"[\u3400-\u9fff]", alias) and alias in text:
                inferred_color = color
                text = text.replace(alias, " ")
                break
        if inferred_color:
            break
    for token in sorted(CHINESE_NOISE, key=len, reverse=True):
        text = text.replace(token, " ")

    groups: list[tuple[str, ...]] = []
    # Consume phrases first, so adjacent Chinese words do not become one token.
    expansions = [tuple((key, *aliases)) for key, aliases in KIND_ALIASES.items()] + list(TERM_ALIASES)
    candidates = sorted(
        ((alias, terms) for terms in expansions for alias in terms),
        key=lambda item: len(item[0]), reverse=True,
    )
    for alias, terms in candidates:
        if re.search(r"[\u3400-\u9fff]", alias):
            pattern = re.escape(alias)
        else:
            pattern = r"(?<!\w)" + re.escape(alias) + r"(?!\w)"
        if re.search(pattern, text):
            groups.append(tuple(dict.fromkeys(normalize(item) for item in terms)))
            text = re.sub(pattern, " ", text)

    remaining = [token for token in normalize(text).split() if token not in ENGLISH_NOISE]
    formats = {token for token in remaining if token in QUERY_FORMATS}
    remaining = [token for token in remaining if token not in formats]
    groups.extend((token,) for token in remaining)
    clean_query = " ".join(token for token in normalize(query).split() if token not in ENGLISH_NOISE and token not in QUERY_FORMATS)
    # A name entered verbatim can contain Chinese request noise only at its ends.
    identity_query = unicodedata.normalize("NFKC", query).casefold()
    if inferred_color:
        for alias in sorted(COLOR_ALIASES[inferred_color], key=len, reverse=True):
            if re.search(r"[\u3400-\u9fff]", alias):
                identity_query = identity_query.replace(alias, " ")
    for token in sorted(CHINESE_NOISE, key=len, reverse=True):
        identity_query = identity_query.replace(token, " ")
    identity_query = " ".join(token for token in normalize(identity_query).split() if token not in ENGLISH_NOISE and token not in QUERY_FORMATS)
    return groups, identity_query or clean_query, formats, inferred_color


def query_catalog(
    catalog: dict[str, Any], query: str = "", *, kind: str | None = None,
    color: str | None = None, file_format: str | None = None, record_id: str | None = None,
    limit: int = 8, brief: bool = False,
) -> dict[str, Any]:
    """Return matching original records plus provenance, without side effects."""
    if limit < 1:
        raise ValueError("limit must be at least 1")
    if kind:
        kind = canonical(kind, KIND_ALIASES)
        if kind is None:
            raise ValueError("Unknown kind")
    if color:
        color = canonical(color, COLOR_ALIASES)
        if color is None:
            raise ValueError("Unknown color")
    file_format = canonical_format(file_format) if file_format else None
    groups, identity_query, natural_formats, inferred_color = parse_terms(query)
    color = color or inferred_color
    formats = {file_format} if file_format else natural_formats
    numbers = {token for group in groups for token in group if token.isdecimal()}
    query_variants = {term for group in groups for term in group if term in VARIANT_MARKERS}
    query_roman_variants = {term for group in groups for term in group if term in ROMAN_VARIANTS}
    eligible_records = [
        record for record in catalog.get("records", [])
        if (record_id is None or str(record.get("id")) == record_id)
        and (kind is None or canonical(record.get("kind"), KIND_ALIASES) == kind)
    ]
    # Resolve identity before capability filters. Otherwise an unsupported
    # format on Adler could silently substitute Adler Outdoor, or a color
    # mismatch could substitute a longer stone name for the requested stone.
    exact_candidates = [
        record for record in eligible_records
        if identity_query and identity_query in record_aliases(record)
    ]
    if exact_candidates:
        eligible_records = exact_candidates
    matches = []
    for record in eligible_records:
        # Color comes exclusively from the catalog field, never from a name or
        # prose containing a color word (Blue Pearl is officially black).
        if color and canonical(record.get("color"), COLOR_ALIASES) != color:
            continue
        if formats and not all(observed_downloads(record, fmt) for fmt in formats):
            continue
        identity = normalize(" ".join(str(record.get(key) or "") for key in ("name", "model_number")))
        if numbers and not all(contains(identity, number) for number in numbers):
            continue
        if numbers:
            record_variants = {marker for marker in VARIANT_MARKERS if contains(identity, marker)}
            if record_variants != query_variants:
                continue
        if query_variants and not all(contains(identity, variant) for variant in query_variants):
            continue
        if query_roman_variants and not all(contains(identity, variant) for variant in query_roman_variants):
            continue
        searchable = normalize(" ".join(string_values({
            key: record.get(key) for key in
            ("name", "model_number", "kind", "category", "description", "attributes", "color")
        })))
        if not all(any(contains(searchable, term) for term in group) for group in groups):
            continue
        aliases = record_aliases(record)
        exact = bool(identity_query and identity_query in aliases)
        score = (1000 if exact else 0) + sum(
            20 if any(contains(identity, term) for term in group) else 1
            for group in groups
        )
        matches.append((score, exact, record))
    matches.sort(key=lambda match: (-match[0], normalize(match[2].get("name")), str(match[2].get("id"))))
    return {
        "query": query,
        "filters": {"kind": kind, "color": color, "formats": sorted(formats), "id": record_id},
        "catalog_checked_on": catalog.get("checked_on"),
        "total_matched": len(matches),
        "returned_count": min(limit, len(matches)),
        "results": [brief_record(record) if brief else record for _, _, record in matches[:limit]],
        "notes": [STOCK_NOTE, DOWNLOAD_NOTE],
    }


def brief_record(record: dict[str, Any]) -> dict[str, Any]:
    """Drop long page prose and limit slabs, preserving their record association."""
    result = {key: value for key, value in record.items() if key != "description"}
    slabs = record.get("slabs", [])
    result["slabs"] = slabs[:5]
    result["slab_count"] = len(slabs)
    return result


def load_catalog(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        catalog = json.load(handle)
    if not isinstance(catalog, dict) or catalog.get("schema_version") != 1:
        raise ValueError("Catalog must use schema_version 1")
    if not isinstance(catalog.get("records"), list) or not all(isinstance(item, dict) for item in catalog["records"]):
        raise ValueError("Catalog records must be an array of objects")
    return catalog


def print_result(result: dict[str, Any]) -> None:
    print(f"官网资料核验日期：{result.get('catalog_checked_on') or '未记录'}")
    print(f"匹配 {result['total_matched']} 条，展示 {result['returned_count']} 条。")
    if not result["results"]:
        print("没有符合条件的已收录资料。可使用型号、正式名称或 --kind / --color 筛选。")
    for record in result["results"]:
        print(f"\n{record.get('name', '未命名')} [{record.get('kind', '')}]  ID: {record.get('id', '')}")
        for field, label in (("model_number", "型号"), ("category", "类别"), ("color", "官网颜色分类")):
            if record.get(field):
                print(f"{label}：{record[field]}")
        if record.get("description"):
            print(record["description"])
        for key, value in record.get("attributes", {}).items():
            print(f"{key}：{value}")
        print(f"官网：{record.get('source_url') or '未记录'}")
        print(f"核验日期：{record.get('checked_on') or result.get('catalog_checked_on') or '未记录'}")
        if record.get("source_crawled"):
            print(f"来源抓取日期：{record['source_crawled']}")
        downloads = record.get("download_options", [])
        for option in downloads:
            suffix = f" ({option['format']})" if option.get("format") else ""
            if option in observed_downloads(record):
                print(f"下载{suffix}：{option.get('label') or '链接'} — {option['url']}")
            else:
                print(f"下载{suffix}：{option.get('label') or '链接'} — 链接尚未解析")
        if record.get("available_model_formats"):
            print("记录的模型格式标记：" + ", ".join(record["available_model_formats"]))
        slabs = record.get("slabs", [])
        for slab in slabs[:5]:
            size = f"{slab.get('length_mm', '?')} × {slab.get('width_mm', '?')} mm"
            print(f"石板：{slab.get('number', '?')}；{size}；页面状态：{slab.get('status') or '未记录'}")
        slab_count = record.get("slab_count", len(slabs))
        if slab_count > 5:
            print(f"另有 {slab_count - 5} 块已收录石板；使用 --json 并去掉 --brief 查看完整记录。")
    for note in result["notes"]:
        print(f"\n说明：{note}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="离线查询 DRAENERT 产品、材质及已观测下载链接。")
    parser.add_argument("query", nargs="?", default="", help="型号、名称或中文需求；包含空格时请加引号")
    parser.add_argument("--kind", help="product / stone / wood / leather / fabric / entry 或中文类别")
    parser.add_argument("--color", help="按官网颜色字段精确筛选，如 blue、blau、蓝色")
    parser.add_argument("--format", dest="file_format", help="只返回有该格式已观测下载链接的记录，如 dwg 或 3ds")
    parser.add_argument("--id", dest="record_id", help="精确匹配目录 ID")
    parser.add_argument("--limit", type=int, default=8, help="返回条数，默认 8")
    parser.add_argument("--json", action="store_true", help="输出完整 JSON")
    parser.add_argument("--brief", action="store_true", help="省略网页描述；石板仅返回前 5 块及 slab_count")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG, help="目录 JSON 路径")
    args = parser.parse_args(argv)
    try:
        result = query_catalog(
            load_catalog(args.catalog), args.query, kind=args.kind, color=args.color,
            file_format=args.file_format, record_id=args.record_id, limit=args.limit, brief=args.brief,
        )
    except (OSError, ValueError, TypeError) as error:
        parser.error(str(error))
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_result(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
