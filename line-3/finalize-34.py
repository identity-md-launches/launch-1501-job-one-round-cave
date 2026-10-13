"""Add one confined pigment seal to inherited wall 33; write round 34 outputs.

Generated PNG bytes enter only through one base64 stdin line. No cutout file is
created. The inherited image is hash-checked before compositing.
"""
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("image_helpers", ROOT / "line-3/finalize-31.py")
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)
thumbnail = helpers.thumbnail


def pigment(red, green, blue):
    if max(red, green, blue) < 105:
        return (37, 29, 21), 180  # charcoal has the strongest impression
    if red > green * 1.35 and red > blue * 1.45:
        return (135, 58, 33), 110  # red ochre
    if red > blue * 1.5 and green > blue * 1.3:
        return (165, 106, 47), 95  # yellow ochre
    if min(red, green, blue) > 165:
        return (205, 188, 155), 60  # chalk flecks
    return (105, 67, 39), 75


def main():
    old_path = ROOT / "artifacts/line-3/wall.png"
    inherited = old_path.read_bytes()
    inherited_hash = hashlib.sha256(inherited).hexdigest()
    previous_record = json.loads((ROOT / "dist/line-3/33.json").read_text())
    if previous_record["image"] != "https://api.imd.fun/artifacts/" + inherited_hash:
        raise ValueError("inherited wall does not match record 33")
    width, height, original_rows = thumbnail.png_rgb(inherited)
    if (width, height) != (1254, 1254):
        raise ValueError("unexpected inherited wall size")

    encoded = sys.stdin.buffer.readline(12_000_001).strip()
    if len(encoded) > 12_000_000:
        raise ValueError("generated pigment input is too large")
    cutout = base64.b64decode(encoded, validate=True)
    source_width, source_height, source = helpers.png_rgba(cutout)

    # Open rock to Pepe's left, away from every inherited pigment mark.
    box = (75, 410, 225, 560)
    x0, y0, x1, y1 = box
    target_width, target_height = x1 - x0, y1 - y0
    rows = [bytearray(row) for row in original_rows]
    changed = 0
    for dy in range(target_height):
        sy0, sy1 = dy * source_height // target_height, (dy + 1) * source_height // target_height
        for dx in range(target_width):
            sx0, sx1 = dx * source_width // target_width, (dx + 1) * source_width // target_width
            red = green = blue = alpha = 0
            count = (sy1 - sy0) * (sx1 - sx0)
            for sy in range(sy0, sy1):
                source_row = source[sy]
                for sx in range(sx0, sx1):
                    r, g, b, a = source_row[4 * sx:4 * sx + 4]
                    red += r * a
                    green += g * a
                    blue += b * a
                    alpha += a
            if not alpha:
                continue
            color, strength = pigment(red // alpha, green // alpha, blue // alpha)
            opacity = min(strength, alpha * strength // (count * 255))
            if opacity < 8:
                continue
            at = 3 * (x0 + dx)
            old = rows[y0 + dy][at:at + 3]
            new = bytes((old[channel] * (255 - opacity) + color[channel] * opacity + 127) // 255
                        for channel in range(3))
            if new != old:
                rows[y0 + dy][at:at + 3] = new
                changed += 1
    if changed < 1000:
        raise ValueError("new pigment mark is missing")
    outside = sum(rows[y][3 * x:3 * x + 3] != original_rows[y][3 * x:3 * x + 3]
                  for y in range(height) for x in range(width)
                  if not (x0 <= x < x1 and y0 <= y < y1))
    if outside:
        raise ValueError("pixels changed outside the new mark")

    png = helpers.encode_rgb(width, height, rows)
    if thumbnail.png_rgb(png)[2] != [bytes(row) for row in rows]:
        raise ValueError("round-trip PNG pixels mismatch")
    jpeg = thumbnail.jpeg(thumbnail.resize(width, height, rows))
    if len(jpeg) >= 100_000:
        raise ValueError("JPEG exceeds 100 KB")
    digest = hashlib.sha256(png).hexdigest()
    meaning = "Pepe presses a distinct seal into clay to recognize the exact message again."
    record = {"name": "Pepe's Clay Seal",
              "image": "https://api.imd.fun/artifacts/" + digest,
              "attributes": [{"trait_type": key, "value": value} for key, value in [
                  ("Cave", "Base"), ("Wall", "Line 3"), ("Number", 34),
                  ("Left behind", "keccak-envelope"), ("Meaning", meaning),
                  ("One thing", "Offline EIP-1559 transaction decoding")]]}
    version_path = ROOT / "artifacts/line-3/wall-v15.png"
    version_path.write_bytes(png)
    old_path.write_bytes(png)
    (ROOT / "dist/line-3/34.jpg").write_bytes(jpeg)
    (ROOT / "dist/line-3/34.json").write_text(json.dumps(record, indent=2) + "\n")
    review = {
        "wall": {"paths": ["artifacts/line-3/wall-v15.png", "artifacts/line-3/wall.png"],
                 "width": width, "height": height, "format": "PNG", "mode": "RGB",
                 "bytes": len(png), "sha256": digest},
        "thumbnail": {"path": "dist/line-3/34.jpg", "width": 512, "height": 512,
                      "format": "JPEG", "bytes": len(jpeg)},
        "preservation": {"inheritedSha256": inherited_hash, "editRectangleXYXY": list(box),
                         "changedPixels": changed, "changedPixelsOutsideRectangle": outside},
        "cutout": {"width": source_width, "height": source_height, "format": "PNG", "mode": "RGBA"},
        "visualReview": {"reviewed": False},
        "unmetVisualRequirements": ["Visual review pending"]}
    (ROOT / "line-3/round-34-review.json").write_text(json.dumps(review, indent=2) + "\n")
    print(json.dumps(review, indent=2))


if __name__ == "__main__":
    main()
