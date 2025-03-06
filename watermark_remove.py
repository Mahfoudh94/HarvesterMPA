import cv2
import numpy as np


def match_logo_to_watermark(image: cv2.typing.MatLike, logo: cv2.typing.MatLike) -> bytes:
    if image is None or logo is None:
        raise ValueError("Error loading images. Check file paths.")

    # Convert input image to grayscale to detect watermark
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_logo = cv2.cvtColor(logo, cv2.COLOR_BGR2GRAY)

    # Use template matching to find watermark location
    result = cv2.matchTemplate(gray_image, gray_logo, cv2.TM_CCOEFF_NORMED)
    _, _, _, max_loc = cv2.minMaxLoc(result)

    # Get the size of the logo
    logo_h, logo_w = logo.shape[:2]

    # Extract region of interest from input image
    roi = image[max_loc[1]:max_loc[1] + logo_h, max_loc[0]:max_loc[0] + logo_w]

    # Resize logo if needed (for better matching)
    scale_factor = min(roi.shape[1] / logo_w, roi.shape[0] / logo_h)
    new_size = (int(logo_w * scale_factor), int(logo_h * scale_factor))
    logo_resized = cv2.resize(logo, new_size, interpolation=cv2.INTER_AREA)

    # Recalculate max location after resizing
    max_loc = (max_loc[0], max_loc[1])

    # Ensure logo has 4 channels (RGBA)
    if logo_resized.shape[2] == 3:
        logo_resized = cv2.cvtColor(logo_resized, cv2.COLOR_BGR2BGRA)

    # Extract alpha channel for transparency
    alpha = logo_resized[:, :, 3] / 255.0
    alpha = cv2.merge([alpha, alpha, alpha])

    # Align the logo on the input image
    overlay = image[max_loc[1]:max_loc[1] + new_size[1], max_loc[0]:max_loc[0] + new_size[0]]

    # Apply Divide blend mode: result = 255 * (image / (logo + 1))
    logo_rgb = logo_resized[:, :, :3].astype(np.float32)
    overlay = overlay.astype(np.float32)
    blended = np.clip(255 * (overlay / (logo_rgb + 1)), 0, 255).astype(np.uint8)

    # Preserve transparency using alpha mask
    output = overlay * (1 - alpha) + blended * alpha
    image[max_loc[1]:max_loc[1] + new_size[1], max_loc[0]:max_loc[0] + new_size[0]] = output.astype(np.uint8)

    # Encode final image as binary data
    _, encoded_image = cv2.imencode('.png', image)

    # Return binary data
    return encoded_image.tobytes()


def remove_beetender(image: cv2.typing.MatLike) -> bytes:
    beetenders_logo = cv2.imread('beetenders_logo.png', cv2.IMREAD_UNCHANGED)
    return match_logo_to_watermark(image, beetenders_logo)