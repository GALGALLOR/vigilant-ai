



# Suppose you already created a 5-min parent clip:
parent_clip_path = "C:/.../clips_out/clip_0000_000000_000300.mp4"
parent_duration_sec = 300.0

mini = MiniClipGenerator(
    ffmpeg_path=FFMPEG,       # your resolved ffmpeg path
    mini_length_sec=10.0,
    stride_sec=2.0,
    cut_files=True,
    exact_cuts=False,
    write_json_files=True,
)

result = mini.generate(
    parent_clip_index=0,
    parent_clip_path=parent_clip_path,
    parent_duration_sec=parent_duration_sec,
    output_dir="C:/.../clips_out/miniclips/clip_0000",
)

print(result["miniclips"][0])