"""Prepare a model-to-render job; never call an image service."""
import argparse
import hashlib
import json
from pathlib import Path
import warnings

from PIL import Image, UnidentifiedImageError


def inspect_image(filename):
    path = Path(filename).expanduser().absolute()
    if not path.is_file():
        raise ValueError(f"Not a file: {path}")
    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        with Image.open(path) as image:
            if image.format not in {"PNG", "JPEG", "WEBP"}:
                raise ValueError("Only PNG, JPEG and WebP images are supported.")
            if getattr(image, "n_frames", 1) != 1:
                raise ValueError("Export a single static frame before preparing a render.")
            metadata = {"path": str(path), "format": image.format,
                        "width": image.width, "height": image.height}
            image.verify()
        # Decode pixels too: verify() alone does not fully decode every format.
        with Image.open(path) as image:
            image.load()
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    metadata["sha256"] = digest.hexdigest()
    return metadata


def prepare(image, references, style, materials, lighting, output):
    target = inspect_image(image)
    refs = [inspect_image(item) for item in references]
    lines = [
        "Use case: sketch-to-render",
        "Asset type: 室内设计视觉提案",
        "Primary request: 将模型图转换为自然写实效果图。",
        "Input images: Image 1 是编辑目标，决定空间结构与相机视角。",
    ]
    for index, _ in enumerate(refs, start=2):
        lines.append(f"Image {index} 是辅助风格/材质参考，不替换 Image 1 的布局。")
    lines.extend([
        f"Style/medium: {style}",
        f"Materials/textures: {materials}",
        f"Lighting/mood: {lighting}",
        "Composition/framing: 保持原图画幅、视角、透视及空间比例。",
        "Constraints: 保留墙体、门窗、柜体、家具的位置和数量；"
        "不新增或删除结构和家具；仅改变所要求的材质、光照与写实表现。",
        "Avoid: 结构漂移、透视扭曲、额外文字、水印、未要求的装饰。",
        "提交工具前先查看原图并补充可观察的具体结构约束；"
        "生成后对照输入复核，记录无法保持的结构。",
    ])
    prompt = "\n".join(lines) + "\n"
    manifest = {
        "schema_version": 1,
        "status": "prepared_not_rendered",
        "backend": "session_image_edit_tool_required",
        "target": target,
        "references": refs,
        "prompt_file": "prompt.txt",
        "settings": {"style": style, "materials": materials, "lighting": lighting},
        "review_status": "not_generated",
    }
    destination = Path(output).expanduser().resolve()
    # Exclusive creation prevents overwriting an earlier job or an input.
    destination.mkdir(parents=True, exist_ok=False)
    (destination / "prompt.txt").write_text(prompt, encoding="utf-8")
    (destination / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", required=True, help="Model screenshot to edit")
    parser.add_argument("--reference", action="append", default=[], help="Optional style reference")
    parser.add_argument("--style", default="自然写实，忠于原模型")
    parser.add_argument("--materials", default="保留已有材质意图；未指定部分使用中性材质")
    parser.add_argument("--lighting", default="柔和自然光")
    parser.add_argument("--out", required=True, help="A new preparation directory")
    args = parser.parse_args()
    try:
        destination = prepare(args.image, args.reference, args.style,
                              args.materials, args.lighting, args.out)
    except (OSError, ValueError, UnidentifiedImageError,
            Image.DecompressionBombError, Image.DecompressionBombWarning) as error:
        parser.error(str(error))
    print(f"Prepared only (no image generated): {destination}")


if __name__ == "__main__":
    main()
