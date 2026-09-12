from pathlib import Path

from PIL import Image

from localmuse.caption_cleanup import CaptionCleaner
from localmuse.dataset_analysis import DatasetAnalyzer
from localmuse.dataset_workflow import prepare_training_dataset, scan_dataset
from localmuse.image_prompt import ImagePromptGenerator
from localmuse.presets import PresetStore


def test_generate_prompt_for_portrait_image(tmp_path):
    image_path = tmp_path / "portrait.jpg"
    image = Image.new("RGB", (900, 1200), color=(255, 240, 220))
    image.save(image_path)

    generator = ImagePromptGenerator()
    result = generator.generate_for_file(image_path)

    assert result["file_name"] == "portrait.jpg"
    assert result["format"] == "JPEG"
    assert "portrait" in result["prompt"].lower()
    assert "person" in result["prompt"].lower() or "subject" in result["prompt"].lower()


def test_generate_prompt_for_landscape_image(tmp_path):
    image_path = tmp_path / "landscape.png"
    image = Image.new("RGB", (1400, 900), color=(200, 220, 255))
    image.save(image_path)

    generator = ImagePromptGenerator()
    result = generator.generate_for_file(image_path)

    assert result["file_name"] == "landscape.png"
    assert result["format"] == "PNG"
    assert "landscape" in result["prompt"].lower()


def test_reject_unsupported_extension(tmp_path):
    image_path = tmp_path / "notes.txt"
    image_path.write_text("not an image", encoding="utf-8")

    generator = ImagePromptGenerator()

    try:
        generator.generate_for_file(image_path)
        assert False, "Expected ValueError for unsupported file type"
    except ValueError:
        pass


def test_write_prompt_file_uses_image_stem_for_png(tmp_path):
    image_path = tmp_path / "image1.png"
    Image.new("RGB", (640, 480), color=(220, 220, 220)).save(image_path)

    prompt_path = ImagePromptGenerator().write_prompt_file(image_path)

    assert prompt_path == tmp_path / "image1.txt"
    assert prompt_path.read_text(encoding="utf-8").strip()


def test_write_prompt_file_uses_image_stem_for_jpg_with_complex_name(tmp_path):
    image_path = tmp_path / "my photo.v1.jpg"
    Image.new("RGB", (640, 480), color=(220, 220, 220)).save(image_path)

    prompt_path = ImagePromptGenerator().write_prompt_file(image_path)

    assert prompt_path == tmp_path / "my photo.v1.txt"
    assert "landscape" in prompt_path.read_text(encoding="utf-8").lower()


def test_write_prompts_for_directory_processes_supported_images_only(tmp_path):
    Image.new("RGB", (100, 100), color=(220, 220, 220)).save(tmp_path / "image1.png")
    Image.new("RGB", (100, 100), color=(220, 220, 220)).save(tmp_path / "photo1.jpg")
    (tmp_path / "notes.txt").write_text("ignore", encoding="utf-8")

    prompt_paths = ImagePromptGenerator().write_prompts_for_directory(tmp_path)

    assert prompt_paths == [tmp_path / "image1.txt", tmp_path / "photo1.txt"]
    assert (tmp_path / "notes.txt").read_text(encoding="utf-8") == "ignore"


def test_caption_cleaner_removes_speculative_sentences():
    caption = (
        "nag_person, The image shows a woman wearing a brown top. "
        "She is likely discussing the best hair color for her face."
    )

    cleaned = CaptionCleaner().clean(caption, "nag_person")

    assert cleaned == "nag_person, a woman wearing a brown top."


def test_caption_cleaner_removes_identity_claims_and_keeps_visual_details():
    caption = (
        "nag_person, The image shows a woman wearing a jacket. "
        "She is identified as Anastasia, known for her role in a movie."
    )

    cleaned = CaptionCleaner().clean(caption, "nag_person")

    assert cleaned == "nag_person, a woman wearing a jacket."


def test_dataset_analyzer_reports_missing_captions_and_small_images(tmp_path):
    Image.new("RGB", (400, 700), color=(220, 220, 220)).save(tmp_path / "small.png")
    Image.new("RGB", (800, 800), color=(220, 220, 220)).save(tmp_path / "ready.png")
    (tmp_path / "ready.txt").write_text("nag_person, a portrait.", encoding="utf-8")

    report = DatasetAnalyzer().analyze(tmp_path, "nag_person")

    assert report["image_count"] == 2
    assert report["read_error_count"] == 0
    assert report["warning_counts"] == {"small_dimension": 1, "missing_caption": 1}


def test_preset_store_hides_experimental_and_saves_user_preset(tmp_path):
    built_in = tmp_path / "presets.json"
    built_in.write_text(
        '{"version": 1, "presets": ['
        '{"id": "basic", "label": "Basic"},'
        '{"id": "experimental", "label": "Experimental", "experimental": true}'
        ']}',
        encoding="utf-8",
    )
    store = PresetStore(built_in)

    assert [preset["id"] for preset in store.list_presets()] == ["basic"]
    store.save_user_preset({"id": "my_style", "label": "My style", "steps": 28})

    assert store.get("my_style")["steps"] == 28


def test_prepare_training_dataset_copies_images_and_captions(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    Image.new("RGB", (640, 900)).save(source / "photo.jpg")
    (source / "photo.txt").write_text("token, portrait", encoding="utf-8")

    report = scan_dataset(source)
    prepared = prepare_training_dataset(source, tmp_path / "prepared", "token", 10, "dataset_v02")

    assert report["image_count"] == 1
    assert prepared["target_directory"].endswith("dataset_v02\\10_token")
    assert (Path(prepared["target_directory"]) / "photo.jpg").is_file()
    assert (Path(prepared["target_directory"]) / "photo.txt").is_file()
