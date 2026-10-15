import cairosvg
from pathlib import Path
OUT = Path(r"C:\Users\ASUS\Desktop\五步协议\论文图表_可编辑矢量\Figure8_GNHR")
svg = OUT/"Figure 8.svg"
cairosvg.svg2pdf(url=str(svg), write_to=str(OUT/"Figure 8.pdf"))
cairosvg.svg2png(url=str(svg), write_to=str(OUT/"Figure 8_preview.png"), scale=4.0)
print("pdf", (OUT/"Figure 8.pdf").stat().st_size, "bytes")
print("png", (OUT/"Figure 8_preview.png").stat().st_size, "bytes")
