convert -size 76x76 xc:none -draw "roundrectangle 0,0,76,76,8,8" mask.png
convert cusa.png -matte mask.png -compose DstIn -composite picture_with_rounded_corners.png