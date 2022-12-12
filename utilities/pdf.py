# import img2pdf
# from pathlib import Path
# from PIL import Image

# def createImagePDF(sourcePath: str, outputPath: str) -> bool:
#   try:
#     with open(outputPath,"wb") as f: f.write(img2pdf.convert(sourcePath))
#     return True
#   except:
#     return False

# def createImageWebP(sourcePath: str, outputPath: str) -> bool:
#   try:
#     Image.open(sourcePath).save(outputPath, format="webp")
#     return True
#   except:
#     return False

# def convertAllWebP(sourcePath: str):
#   paths = Path(sourcePath).glob("**/*.png")
#   for path in paths:
#     createImageWebP(path, path.with_suffix('.webp'))
