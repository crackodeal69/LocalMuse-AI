from pathlib import Path

from PIL import Image

from localmuse.image_prompt import ImagePromptGenerator


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
