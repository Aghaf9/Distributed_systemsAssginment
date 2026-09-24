from target_recognition import load_ref_images

targets, distractors = load_ref_images()
# targets: dict {label: image}

print("-- Targets --")
for label, images in targets.items():
    print(f"{label}")

print("-- Distractors --")
for label, images in distractors.items():
    print(f"{label}: {len(images)} image(s)")


