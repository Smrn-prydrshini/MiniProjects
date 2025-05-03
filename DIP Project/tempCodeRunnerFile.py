import cv2
import numpy as np

# Load images
background = cv2.imread('C:\Users\SIMRAN\OneDrive\Desktop\DIP Project\background.png')
target = cv2.imread('C:\Users\SIMRAN\OneDrive\Desktop\DIP Project\target.png')

# Check if images are loaded successfully
if background is None:
    print("Error: Couldn't load the background image.")
    exit()

if target is None:
    print("Error: Couldn't load the target image.")
    exit()

# Resize (optional)
background = cv2.resize(background, (640, 480))
target = cv2.resize(target, (640, 480))

# Convert to grayscale
gray_bg = cv2.cvtColor(background, cv2.COLOR_BGR2GRAY)
gray_target = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)

# Subtract images
diff = cv2.absdiff(gray_bg, gray_target)

# Thresholding
_, mask = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

# Morphological cleaning
kernel = np.ones((5, 5), np.uint8)
clean_mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
clean_mask = cv2.morphologyEx(clean_mask, cv2.MORPH_DILATE, kernel)

# Extract foreground
foreground = cv2.bitwise_and(target, target, mask=clean_mask)

# Show results
cv2.imshow("Foreground", foreground)
cv2.waitKey(0)
cv2.destroyAllWindows()
