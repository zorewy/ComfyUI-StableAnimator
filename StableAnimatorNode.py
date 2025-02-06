import os
import subprocess
from comfyui import ComfyUI, Node, InputField, OutputField

class StableAnimatorNode(Node):
    name = "StableAnimator"
    description = "Generate high-quality identity-preserving human image animations using StableAnimator."
    category = "Custom"

    inputs = [
        InputField("reference_image", "Reference Image", "image"),
        InputField("pose_sequence", "Pose Sequence", "image_sequence"),
        InputField("output_path", "Output Path", "string", default="output"),
        InputField("resolution", "Resolution", "string", default="512x512")
    ]

    outputs = [
        OutputField("animation", "Generated Animation", "image_sequence")
    ]

    def run(self, reference_image, pose_sequence, output_path, resolution):
        # Ensure the output directory exists
        os.makedirs(output_path, exist_ok=True)

        # Save the reference image and pose sequence to temporary files
        ref_image_path = os.path.join(output_path, "reference.png")
        pose_sequence_path = os.path.join(output_path, "poses")
        os.makedirs(pose_sequence_path, exist_ok=True)

        reference_image.save(ref_image_path)
        for i, pose in enumerate(pose_sequence):
            pose.save(os.path.join(pose_sequence_path, f"frame_{i}.png"))

        # Run StableAnimator inference
        command = [
            "bash", "command_basic_infer.sh",
            "--validation_image", ref_image_path,
            "--validation_control_folder", pose_sequence_path,
            "--output_dir", output_path,
            "--width", resolution.split("x")[0],
            "--height", resolution.split("x")[1]
        ]
        subprocess.run(command, check=True)

        # Load the generated animation
        animation_frames = []
        for file in sorted(os.listdir(output_path)):
            if file.startswith("frame_") and file.endswith(".png"):
                animation_frames.append(os.path.join(output_path, file))

        return {"animation": animation_frames}

# Register the node in ComfyUI
ComfyUI.register_node(StableAnimatorNode)