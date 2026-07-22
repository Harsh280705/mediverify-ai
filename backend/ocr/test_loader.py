from pathlib import Path

from loader import ImageLoader

TEST_FILES = [

    "sample.jpg",

    "sample.png",

    "sample.heic",

    "sample.pdf",

]

for file in TEST_FILES:

    if not Path(file).exists():
        continue

    images = ImageLoader.load(file)

    print()

    print("=" * 50)

    print(file)

    print(f"Pages / Images : {len(images)}")

    for i, img in enumerate(images):

        print(
            f"Image {i+1}",
            img.shape
        )

print()

print("Loader working successfully.")