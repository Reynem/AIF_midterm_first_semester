import argparse
import os
import subprocess
import sys

SCENES = {
    "AgentPerceptsScene": "animations.agent_scene",
    "BFSScene": "animations.search_scenes",
    "DFSScene": "animations.search_scenes",
    "UCSScene": "animations.search_scenes",
    "AStarScene": "animations.search_scenes",
    "ComparisonScene": "animations.comparison_scene",
}


def main():
    parser = argparse.ArgumentParser(description="Render Manim scenes for AI Search Video.")
    parser.add_argument(
        "scene",
        nargs="?",
        default="ALL",
        choices=list(SCENES.keys()) + ["ALL"],
        help="Scene name to render (default: ALL)",
    )
    parser.add_argument(
        "--quality",
        "-q",
        default="h",
        choices=["l", "m", "h", "p", "k"],
        help="Render quality (l=480p, m=720p, h=1080p, k=2160p)",
    )
    parser.add_argument("--preview", "-p", action="store_true", help="Automatically open video after render")
    args = parser.parse_args()

    scenes_to_render = list(SCENES.keys()) if args.scene == "ALL" else [args.scene]

    for scene in scenes_to_render:
        module = SCENES[scene]
        cmd = [
            sys.executable,
            "-m",
            "manim",
            "-r",
            "1920,1080",
            "--fps",
            "30",
            f"-q{args.quality}",
        ]
        if args.preview:
            cmd.append("-p")

        cmd.extend([os.path.join(*module.split(".")) + ".py", scene])

        print(f"\n--- Rendering {scene} ---")
        print("Running command:", " ".join(cmd))
        subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()