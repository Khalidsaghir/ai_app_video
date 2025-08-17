from moviepy.editor import ImageSequenceClip
import os

def text_to_video(prompt, num_images=10, fps=6, size="1024x1024"):
    """
    Generate a video from a list of image paths.
    """
    if isinstance(prompt, list):
        images = prompt
    else:
        # fallback: treat prompt as a string and look for images in output folder
        image_dir = os.path.join(os.path.dirname(__file__), "output")
        images = sorted([os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.endswith(".png")])

    if not images:
        raise ValueError("No images found to generate video.")

    # Make a video clip from images
    clip = ImageSequenceClip(images, fps=fps)

    # Path for output video
    video_path = os.path.join(os.path.dirname(images[0]), "output_video.mp4")

    # Write video with H.264 codec (browser compatible)
    clip.write_videofile(
        video_path,
        codec="libx264",
        audio=True,
        ffmpeg_params=["-pix_fmt", "yuv420p"]
    )

    return video_path

# Wrapper function for backward compatibility
def images_to_video(*args, **kwargs):
    return text_to_video(*args, **kwargs)
