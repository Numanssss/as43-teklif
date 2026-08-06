from PIL import Image

def process_logo():
    try:
        img = Image.open('asansor_logo.png')
        img = img.convert("RGBA")
        
        datas = img.getdata()
        newData = []
        
        for item in datas:
            r, g, b, a = item
            
            # 1. Background checkerboard detection (white & light grey)
            # If the pixel is close to white/grey, make it transparent
            if r > 180 and g > 180 and b > 180 and abs(r - g) < 20 and abs(g - b) < 20:
                newData.append((0, 0, 0, 0)) # Fully transparent
            # 2. Text color detection (black/dark grey text "AS 43 ASANSÖR")
            # If the pixel is dark, change it to white/silver for contrast on dark background
            elif r < 100 and g < 100 and b < 100:
                # Keep the original transparency if it was already transparent
                if a > 30:
                    newData.append((248, 250, 252, 255)) # Bright slate white
                else:
                    newData.append(item)
            else:
                newData.append(item)
                
        img.putdata(newData)
        img.save('asansor_logo.png', "PNG")
        print("Logo successfully processed and transparency applied!")
    except Exception as e:
        print(f"Error processing logo: {e}")

if __name__ == "__main__":
    process_logo()
